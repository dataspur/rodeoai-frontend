'use client';

import React, { useState } from 'react';
import { useAuth } from '../lib/AuthContext';

interface TopBarProps {
  onOpenAuth: () => void;
  onOpenProfile: () => void;
  title?: string;
  subtitle?: string;
  children?: React.ReactNode;
}

export default function TopBar({ onOpenAuth, onOpenProfile, title, subtitle, children }: TopBarProps) {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <div className="border-b border-gray-800 p-6 flex items-center justify-between bg-black">
      <div>
        {title && <h2 className="text-2xl font-bold text-white">{title}</h2>}
        {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {children}

        {user ? (
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg"
            >
              <span className="text-sm font-medium">{user.username}</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-gray-700 rounded-lg shadow-lg z-10">
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    onOpenProfile();
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-800 rounded-t-lg"
                >
                  Profile Settings
                </button>
                <a
                  href={`/profile/${user.username}`}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-800"
                >
                  View Public Profile
                </a>
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    logout();
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-800 rounded-b-lg text-red-400"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={onOpenAuth}
            className="bg-yellow-500 hover:bg-yellow-600 text-black px-4 py-2 rounded-lg font-semibold"
          >
            Login / Sign Up
          </button>
        )}
      </div>
    </div>
  );
}
