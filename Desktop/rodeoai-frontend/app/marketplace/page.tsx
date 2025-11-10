'use client';

import React, { useState } from 'react';
import { useAuth } from '../lib/AuthContext';
import Navigation from '../components/Navigation';
import TopBar from '../components/TopBar';
import AuthModal from '../components/AuthModal';
import ProfileSettingsModal from '../components/ProfileSettingsModal';

export default function MarketplacePage() {
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const listings = [
    {
      id: 1,
      title: '2018 Sorrel Quarter Horse - "Bo"',
      price: '$15,000',
      location: 'Decatur, TX',
      description: '15.2hh proven heading horse, smooth mover',
      image: 'placeholder',
    },
    {
      id: 2,
      title: 'Gooseneck Trailer - 4 Horse',
      price: '$28,500',
      location: 'Fort Worth, TX',
      description: 'Living quarters, excellent condition',
      image: 'placeholder',
    },
    {
      id: 3,
      title: 'Roping Saddle - Custom Made',
      price: '$3,200',
      location: 'Oklahoma City, OK',
      description: 'Hand-tooled, barely used',
      image: 'placeholder',
    },
  ];

  return (
    <div className="flex h-screen bg-black text-white">
      <Navigation user={user} />

      <div className="flex-1 flex flex-col">
        <TopBar
          onOpenAuth={() => setShowAuthModal(true)}
          onOpenProfile={() => setShowProfileModal(true)}
          title="Marketplace"
          subtitle="Buy and sell horses, trailers, and equipment"
        >
          <button className="bg-yellow-500 hover:bg-yellow-600 text-black px-4 py-2 rounded-lg font-semibold">
            Create Listing
          </button>
        </TopBar>

        <div className="flex-1 overflow-y-auto p-6">
          {/* Filters */}
          <div className="mb-6 flex gap-3 overflow-x-auto">
            <button className="px-4 py-2 bg-yellow-500 text-black rounded-lg font-semibold whitespace-nowrap">
              All Items
            </button>
            <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg whitespace-nowrap">
              Horses
            </button>
            <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg whitespace-nowrap">
              Trailers
            </button>
            <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg whitespace-nowrap">
              Tack & Equipment
            </button>
            <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 rounded-lg whitespace-nowrap">
              Trucks
            </button>
          </div>

          {/* Listings Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {listings.map((listing) => (
              <div key={listing.id} className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden hover:border-gray-700 transition-colors">
                {/* Image Placeholder */}
                <div className="aspect-video bg-gray-800 flex items-center justify-center">
                  <svg className="w-16 h-16 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>

                {/* Content */}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-lg">{listing.title}</h3>
                    <span className="text-yellow-500 font-bold">{listing.price}</span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">{listing.location}</p>
                  <p className="text-sm text-gray-300 mb-4">{listing.description}</p>
                  <button className="w-full bg-gray-800 hover:bg-gray-700 rounded-lg px-4 py-2 font-semibold">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Info Section */}
          <div className="mt-8 bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">AI-Assisted Listing Creation</h3>
            <p className="text-gray-400 mb-4">
              Upload a video or photo of your horse, trailer, or equipment. Our AI will:
            </p>
            <ul className="text-gray-400 space-y-2">
              <li>• Write compelling sales copy based on market trends</li>
              <li>• Highlight key selling points automatically</li>
              <li>• Suggest competitive pricing</li>
              <li>• Optimize your listing for maximum visibility</li>
            </ul>
          </div>
        </div>
      </div>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
      <ProfileSettingsModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
    </div>
  );
}
