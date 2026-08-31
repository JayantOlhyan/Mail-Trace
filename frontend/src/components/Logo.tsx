'use client';

import * as React from 'react';
import Image from 'next/image';
import { useTheme } from 'next-themes';

export function Logo({ className = '' }: { className?: string }) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Prevent hydration mismatch by rendering an empty block of similar size
    return <div className={`w-32 h-10 ${className}`} />;
  }

  const isLight = resolvedTheme === 'light';

  return (
    <div className={`relative flex items-center ${className}`}>
      <Image
        src={isLight ? '/logo-light.png' : '/logo-dark.png'}
        alt="ThreatTrace AI Logo"
        width={160}
        height={60}
        className="object-contain"
        priority
      />
    </div>
  );
}
