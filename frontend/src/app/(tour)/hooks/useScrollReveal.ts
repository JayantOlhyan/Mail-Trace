'use client';

import { useEffect, useRef, useState } from 'react';

export function useScrollReveal(threshold = 0.5) {
  const ref = useRef<HTMLDivElement>(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let startTime: number | null = null;
    // Animate the progression over 2500ms
    const duration = 2500;
    let rafId: number;

    const animate = (time: number) => {
      if (!startTime) startTime = time;
      const elapsed = time - startTime;
      let newProgress = elapsed / duration;
      
      if (newProgress >= 1) {
        setProgress(1);
      } else {
        setProgress(newProgress);
        rafId = requestAnimationFrame(animate);
      }
    };
    
    // Start animation slightly after mount for smoother effect
    const timeoutId = setTimeout(() => {
      rafId = requestAnimationFrame(animate);
    }, 100);

    return () => {
      clearTimeout(timeoutId);
      if (rafId) cancelAnimationFrame(rafId);
    };
  }, []);

  // isVisible is always true now since components are only mounted when active
  return { ref, isVisible: true, progress };
}
