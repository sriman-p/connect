/**
 * Registration Page
 * New user registration
 */

import { Metadata } from 'next';
import { RegisterForm } from '@/components/auth/register-form';

export const metadata: Metadata = {
  title: 'Sign Up | Connect',
  description: 'Create your Connect account',
};

export default function RegisterPage() {
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

        {/* Registration form */}
        <RegisterForm />
      </div>
    </div>
  );
}
