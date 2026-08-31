'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Mail,
  Briefcase,
  Layers,
  Network,
  GitFork,
  Settings,
  ShieldAlert,
  FileText,
  PlayCircle,
} from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Logo } from '@/components/Logo';

const navItems = [
  { name: 'Dashboard', href: '/workspace', icon: LayoutDashboard },
  { name: 'Investigations', href: '/investigations', icon: Mail },
  { name: 'Cases', href: '/cases', icon: Briefcase },
  { name: 'Campaigns', href: '/campaigns', icon: Layers },
  { name: 'Infrastructure', href: '/infrastructure', icon: Network },
  { name: 'Graph Explorer', href: '/graph', icon: GitFork },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Product Tour', href: '/', icon: PlayCircle },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-screen sticky top-0 text-slate-200 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-center">
        <Link href="/workspace">
          <Logo className="w-48 h-12" />
        </Link>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === '/workspace'
              ? pathname === '/workspace'
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400 border-l-2 border-indigo-500 font-semibold'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Analyst Status Footer */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <div className="text-xs">
              <p className="font-medium text-slate-800 dark:text-slate-200">Analyst Workspace</p>
              <p className="text-slate-500 font-mono">Active Session</p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </div>
    </aside>
  );
}
