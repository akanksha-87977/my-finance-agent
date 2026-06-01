'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { removeToken } from '@/lib/auth';
import toast from 'react-hot-toast';
import { FaBell, FaUser, FaSignOutAlt, FaCog } from 'react-icons/fa';

export default function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const response = await authAPI.getProfile();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  };

  const handleLogout = () => {
    removeToken();
    toast.success('Logged out successfully');
    router.push('/login');
  };

  return (
    <nav className="bg-dark-800 border-b border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold gradient-text">Financial AI</h1>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-dark-700 rounded-lg transition relative">
            <FaBell className="text-xl" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          <div className="relative">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center gap-3 px-3 py-2 hover:bg-dark-700 rounded-lg transition"
            >
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <FaUser className="text-sm" />
              </div>
              <div className="text-left">
                <p className="text-sm font-semibold">{user?.username || 'User'}</p>
                <p className="text-xs text-gray-400">{user?.email || ''}</p>
              </div>
            </button>

            {showDropdown && (
              <div className="absolute right-0 mt-2 w-48 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50">
                <button
                  onClick={() => {
                    setShowDropdown(false);
                    router.push('/profile');
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-dark-700 transition text-left"
                >
                  <FaCog />
                  <span>Settings</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-dark-700 transition text-left text-red-400"
                >
                  <FaSignOutAlt />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}