'use client';

import { useEffect, useRef, useState } from 'react';

export function useScrollReveal(threshold = 0.5) {
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    // Intersection Observer for visibility
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      {
        threshold: [0, threshold, 1],
        rootMargin: '0px 0px -10% 0px'
      }
    );

    observer.observe(element);

    // Scroll listener for progress calculation if needed
    const handleScroll = () => {
      if (!isVisible) return;
      
      const rect = element.getBoundingClientRect();
      const windowHeight = window.innerHeight;
      
      // Calculate progress exclusively for the sticky phase
      // 0 = element top reaches viewport top (starts sticking)
      // 1 = element bottom reaches viewport bottom (stops sticking)
      const stickyScrollDistance = rect.height - windowHeight;
      
      let currentProgress = 0;
      if (stickyScrollDistance > 0) {
        currentProgress = -rect.top / stickyScrollDistance;
      } else {
        // Fallback for short elements
        currentProgress = (windowHeight - rect.top) / (windowHeight + rect.height);
      }
      
      currentProgress = Math.max(0, Math.min(1, currentProgress));
      
      setProgress(currentProgress);
    };

    if (isVisible) {
      window.addEventListener('scroll', handleScroll, { passive: true });
      // Initial call
      handleScroll();
    }

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
    };
  }, [isVisible, threshold]);

  return { ref, isVisible, progress };
}
