'use client';

import React, { useState } from 'react';
import { useAuth } from '../lib/AuthContext';
import Navigation from '../components/Navigation';
import TopBar from '../components/TopBar';
import AuthModal from '../components/AuthModal';
import ProfileSettingsModal from '../components/ProfileSettingsModal';

export default function AnalyticsPage() {
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  if (!user) {
    return (
      <div className="flex h-screen bg-black text-white">
        <Navigation user={user} />
        <div className="flex-1 flex flex-col">
          <TopBar
            onOpenAuth={() => setShowAuthModal(true)}
            onOpenProfile={() => setShowProfileModal(true)}
            title="Analytics"
            subtitle="Rodeo performance insights and statistics"
          />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">Login Required</h2>
              <p className="text-gray-400 mb-6">Please login to access analytics</p>
              <button
                onClick={() => setShowAuthModal(true)}
                className="bg-yellow-500 hover:bg-yellow-600 text-black px-6 py-3 rounded-lg font-semibold"
              >
                Login / Sign Up
              </button>
            </div>
          </div>
        </div>
        <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
        <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
      </div>
    );
  }

  if (!user.is_pro) {
    return (
      <div className="flex h-screen bg-black text-white">
        <Navigation user={user} />
        <div className="flex-1 flex flex-col">
          <TopBar
            onOpenAuth={() => setShowAuthModal(true)}
            onOpenProfile={() => setShowProfileModal(true)}
            title="Analytics"
            subtitle="Rodeo performance insights and statistics"
          />
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <h2 className="text-2xl font-bold mb-4">Pro Feature</h2>
              <p className="text-gray-400 mb-6">
                Advanced analytics and performance tracking is available for Pro members.
                Get detailed insights into your rodeo performance and competitor analysis.
              </p>
              <button className="bg-yellow-500 hover:bg-yellow-600 text-black px-6 py-3 rounded-lg font-semibold">
                Upgrade to Pro
              </button>
            </div>
          </div>
        </div>
        <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
        <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-black text-white">
      <Navigation user={user} />

      <div className="flex-1 flex flex-col">
        <TopBar
          onOpenAuth={() => setShowAuthModal(true)}
          onOpenProfile={() => setShowProfileModal(true)}
          title="Analytics"
          subtitle="Rodeo performance insights and statistics"
        >
          <select className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm">
            <option>Last 30 Days</option>
            <option>Last 3 Months</option>
            <option>This Season</option>
            <option>All Time</option>
          </select>
        </TopBar>

        <div className="flex-1 overflow-y-auto p-6">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-sm text-gray-400 mb-2">Total Entries</h3>
              <p className="text-3xl font-bold text-yellow-500">24</p>
              <p className="text-xs text-gray-500 mt-2">+3 from last month</p>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-sm text-gray-400 mb-2">Win Rate</h3>
              <p className="text-3xl font-bold text-yellow-500">42%</p>
              <p className="text-xs text-gray-500 mt-2">+5% from last month</p>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-sm text-gray-400 mb-2">Average Time</h3>
              <p className="text-3xl font-bold text-yellow-500">5.2s</p>
              <p className="text-xs text-gray-500 mt-2">-0.3s from last month</p>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-sm text-gray-400 mb-2">Total Earnings</h3>
              <p className="text-3xl font-bold text-yellow-500">$12.4K</p>
              <p className="text-xs text-gray-500 mt-2">+$2.1K from last month</p>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Performance Over Time</h3>
              <div className="h-64 bg-gray-800 rounded flex items-center justify-center">
                <p className="text-gray-400">Chart visualization coming soon</p>
              </div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Event Breakdown</h3>
              <div className="h-64 bg-gray-800 rounded flex items-center justify-center">
                <p className="text-gray-400">Chart visualization coming soon</p>
              </div>
            </div>
          </div>

          {/* Recent Events */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Events</h3>
            <div className="space-y-3">
              {[
                { event: 'Decatur Rodeo', date: 'Nov 8, 2025', time: '5.1s', place: '2nd', earnings: '$850' },
                { event: 'Fort Worth Stock Show', date: 'Nov 5, 2025', time: '5.4s', place: '5th', earnings: '$320' },
                { event: 'Texas Circuit Finals', date: 'Nov 1, 2025', time: '4.9s', place: '1st', earnings: '$1,500' },
              ].map((result, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                  <div>
                    <h4 className="font-semibold">{result.event}</h4>
                    <p className="text-sm text-gray-400">{result.date}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{result.time} • {result.place}</p>
                    <p className="text-sm text-yellow-500">{result.earnings}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
      <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
    </div>
  );
}
