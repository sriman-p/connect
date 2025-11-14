'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import PageTransition from '@/components/animations/page-transition';
import AnimatedButton from '@/components/animations/animated-button';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');

  const tabs = [
    { id: 'profile', name: 'Profile', icon: '👤' },
    { id: 'account', name: 'Account', icon: '⚙️' },
    { id: 'security', name: 'Security', icon: '🔒' },
    { id: 'notifications', name: 'Notifications', icon: '🔔' },
    { id: 'passkeys', name: 'Passkeys', icon: '🔑' },
  ];

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-1">Manage your account settings and preferences</p>
          </motion.div>

          <div className="grid grid-cols-4 gap-6">
            {/* Sidebar */}
            <div className="col-span-1">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white rounded-lg border border-gray-200 p-2"
              >
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-left ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-600 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <span className="text-xl">{tab.icon}</span>
                    <span className="text-sm">{tab.name}</span>
                  </button>
                ))}
              </motion.div>
            </div>

            {/* Content */}
            <div className="col-span-3">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg border border-gray-200 p-6"
              >
                {activeTab === 'profile' && (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold mb-4">Profile Settings</h2>
                      <p className="text-gray-600 mb-6">Update your personal information</p>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Profile Photo
                        </label>
                        <div className="flex items-center gap-4">
                          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                            U
                          </div>
                          <div>
                            <AnimatedButton variant="ghost" size="sm">
                              Change Photo
                            </AnimatedButton>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            First Name
                          </label>
                          <input
                            type="text"
                            defaultValue="John"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Last Name
                          </label>
                          <input
                            type="text"
                            defaultValue="Doe"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Email Address
                        </label>
                        <input
                          type="email"
                          defaultValue="john.doe@example.com"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Bio
                        </label>
                        <textarea
                          rows={4}
                          placeholder="Tell us about yourself"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-4 border-t">
                      <AnimatedButton variant="ghost">Cancel</AnimatedButton>
                      <AnimatedButton variant="primary">Save Changes</AnimatedButton>
                    </div>
                  </div>
                )}

                {activeTab === 'account' && (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold mb-4">Account Settings</h2>
                      <p className="text-gray-600 mb-6">Manage your account preferences</p>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Language
                        </label>
                        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                          <option>English</option>
                          <option>Spanish</option>
                          <option>French</option>
                          <option>German</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Timezone
                        </label>
                        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                          <option>UTC</option>
                          <option>America/New_York</option>
                          <option>America/Los_Angeles</option>
                          <option>Europe/London</option>
                        </select>
                      </div>

                      <div className="pt-4 border-t">
                        <h3 className="text-lg font-semibold text-red-600 mb-3">Danger Zone</h3>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                            <div>
                              <div className="font-medium text-gray-900">Delete Account</div>
                              <div className="text-sm text-gray-600">
                                Permanently delete your account and all data
                              </div>
                            </div>
                            <AnimatedButton variant="danger" size="sm">
                              Delete
                            </AnimatedButton>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'security' && (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold mb-4">Security Settings</h2>
                      <p className="text-gray-600 mb-6">Manage your security preferences</p>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Current Password
                        </label>
                        <input
                          type="password"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          New Password
                        </label>
                        <input
                          type="password"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Confirm New Password
                        </label>
                        <input
                          type="password"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="pt-4">
                        <AnimatedButton variant="primary">Update Password</AnimatedButton>
                      </div>

                      <div className="pt-4 border-t">
                        <h3 className="text-lg font-semibold mb-3">Two-Factor Authentication</h3>
                        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div>
                            <div className="font-medium text-gray-900">Enable 2FA</div>
                            <div className="text-sm text-gray-600">
                              Add an extra layer of security to your account
                            </div>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" className="sr-only peer" />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'notifications' && (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold mb-4">Notification Preferences</h2>
                      <p className="text-gray-600 mb-6">Choose what updates you want to receive</p>
                    </div>

                    <div className="space-y-4">
                      {[
                        {
                          title: 'Email Notifications',
                          description: 'Receive email updates about your activity',
                        },
                        {
                          title: 'Push Notifications',
                          description: 'Get push notifications on your devices',
                        },
                        {
                          title: 'Issue Updates',
                          description: 'Get notified when issues are updated',
                        },
                        {
                          title: 'Meeting Reminders',
                          description: 'Receive reminders before meetings',
                        },
                        {
                          title: 'Approval Requests',
                          description: 'Get notified about pending approvals',
                        },
                      ].map((item, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                        >
                          <div>
                            <div className="font-medium text-gray-900">{item.title}</div>
                            <div className="text-sm text-gray-600">{item.description}</div>
                          </div>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" className="sr-only peer" defaultChecked />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'passkeys' && (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold mb-4">Passkey Management</h2>
                      <p className="text-gray-600 mb-6">
                        Manage your passkeys for passwordless authentication
                      </p>
                    </div>

                    <div className="space-y-4">
                      <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
                        <h3 className="font-semibold text-blue-900 mb-2">What are Passkeys?</h3>
                        <p className="text-sm text-blue-800">
                          Passkeys are a safer and easier alternative to passwords. They use your device's biometrics or PIN for secure sign-in.
                        </p>
                      </div>

                      <div>
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-semibold">Your Passkeys</h3>
                          <AnimatedButton variant="primary" size="sm">
                            Add Passkey
                          </AnimatedButton>
                        </div>

                        <div className="space-y-3">
                          <div className="p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="font-medium text-gray-900">MacBook Pro</div>
                                <div className="text-sm text-gray-600">
                                  Platform authenticator • Added Jan 15, 2025
                                </div>
                              </div>
                              <AnimatedButton variant="ghost" size="sm">
                                Remove
                              </AnimatedButton>
                            </div>
                          </div>

                          <div className="p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="font-medium text-gray-900">iPhone 15 Pro</div>
                                <div className="text-sm text-gray-600">
                                  Platform authenticator • Added Jan 10, 2025
                                </div>
                              </div>
                              <AnimatedButton variant="ghost" size="sm">
                                Remove
                              </AnimatedButton>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
