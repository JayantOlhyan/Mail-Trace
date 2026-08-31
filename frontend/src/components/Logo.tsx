'use client';

import * as React from 'react';
import Image from 'next/image';

export function Logo({ className = '' }: { className?: string }) {
  return (
    <div className={`relative flex items-center ${className}`}>
      {/* Light Logo for Dark theme (dark background) */}
      <Image
        src="/logo-light.png"
        alt="ThreatTrace AI Logo"
        width={160}
        height={60}
        className="hidden dark:block object-contain"
        priority
      />
      {/* Dark Logo for Light theme (light background) */}
      <Image
        src="/logo-dark.png"
        alt="ThreatTrace AI Logo"
        width={160}
        height={60}
        className="block dark:hidden object-contain border-none"
        priority
      />
    </div>
  );
}
