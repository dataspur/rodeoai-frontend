'use client';

import React, { useState } from 'react';
import { useAuth } from '../lib/AuthContext';
import Navigation from '../components/Navigation';
import TopBar from '../components/TopBar';
import AuthModal from '../components/AuthModal';
import ProfileSettingsModal from '../components/ProfileSettingsModal';

export default function TravelPage() {
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');

  const handlePlanRoute = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Planning route from', origin, 'to', destination);
    // Route planning logic will go here
  };

  return (
    <div className="flex h-screen bg-black text-white">
      <Navigation user={user} />

      <div className="flex-1 flex flex-col">
        <TopBar
          onOpenAuth={() => setShowAuthModal(true)}
          onOpenProfile={() => setShowProfileModal(true)}
          title="Travel Planner"
          subtitle="Route planning with horse-friendly stops"
        />

        <div className="flex-1 overflow-y-auto p-6">
          {/* Route Planning Form */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6">
              <h2 className="text-xl font-bold mb-4">Plan Your Route</h2>
              <form onSubmit={handlePlanRoute} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Starting Location
                    </label>
                    <input
                      type="text"
                      value={origin}
                      onChange={(e) => setOrigin(e.target.value)}
                      placeholder="Enter city or address"
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Destination
                    </label>
                    <input
                      type="text"
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      placeholder="Enter city or address"
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Trailer Type
                    </label>
                    <select className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500">
                      <option>2-Horse Straight Load</option>
                      <option>4-Horse Slant Load</option>
                      <option>Gooseneck</option>
                      <option>Living Quarters</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Fuel Type
                    </label>
                    <select className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-yellow-500">
                      <option>Diesel</option>
                      <option>Gasoline</option>
                    </select>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full bg-yellow-500 hover:bg-yellow-600 text-black px-6 py-3 rounded-lg font-semibold"
                >
                  Plan Route
                </button>
              </form>
            </div>

            {/* Map Placeholder */}
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6">
              <div className="aspect-video bg-gray-800 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  <p className="text-gray-400">Map integration coming soon</p>
                  <p className="text-sm text-gray-500 mt-2">Google Maps API integration in progress</p>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
                <h3 className="font-semibold mb-2">Horse-Friendly Stops</h3>
                <p className="text-sm text-gray-400">
                  Find rest areas with water, layover arenas, and equine facilities
                </p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
                <h3 className="font-semibold mb-2">Fuel Cost Calculator</h3>
                <p className="text-sm text-gray-400">
                  Real-time diesel prices for big rigs and trailers via GasBuddy API
                </p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
                <h3 className="font-semibold mb-2">Route Optimization</h3>
                <p className="text-sm text-gray-400">
                  Avoid steep grades and find trailer-safe routes
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
      <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
    </div>
  );
}
