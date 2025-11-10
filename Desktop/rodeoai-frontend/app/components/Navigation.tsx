'use client';

import React from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface NavigationProps {
  user: any;
}

export default function Navigation({ user }: NavigationProps) {
  const router = useRouter();
  const pathname = usePathname();

  const navItems = [
    { name: 'Chat', path: '/', icon: 'chat' },
    { name: 'My Files', path: '/files', icon: 'folder', proOnly: true },
    { name: 'Travel', path: '/travel', icon: 'map', proOnly: false },
    { name: 'Marketplace', path: '/marketplace', icon: 'store', proOnly: false },
    { name: 'Analytics', path: '/analytics', icon: 'chart', proOnly: true },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return pathname === '/';
    }
    return pathname?.startsWith(path);
  };

  return (
    <nav className="w-64 bg-black border-r border-gray-800 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold text-yellow-500">RODEO AI</h1>
        <p className="text-xs text-gray-400 mt-1">Powered by DataSpur</p>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <button
            key={item.path}
            onClick={() => router.push(item.path)}
            className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
              isActive(item.path)
                ? 'bg-yellow-500 text-black font-semibold'
                : 'text-gray-300 hover:bg-gray-900'
            }`}
          >
            <div className="flex items-center justify-between">
              <span>{item.name}</span>
              {item.proOnly && !user?.is_pro && (
                <span className="text-xs px-2 py-1 bg-gray-800 rounded">PRO</span>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Footer - User Info */}
      {user && (
        <div className="p-4 border-t border-gray-800">
          <div className="text-sm">
            <div className="font-semibold">{user.username}</div>
            <div className="text-xs text-gray-400">
              {user.is_pro ? 'Pro Member' : 'Free Tier'}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
