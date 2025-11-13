/**
 * Login Page
 * Authentication page for user login
 */

import { Metadata } from 'next';
import { LoginForm } from '@/components/auth/login-form';

export const metadata: Metadata = {
  title: 'Sign In | Connect',
  description: 'Sign in to your Connect account',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-black p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Connect
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Enterprise Collaboration Platform
          </p>
        </div>

        {/* Login form */}
        <LoginForm />
      </div>
    </div>
  );
}
