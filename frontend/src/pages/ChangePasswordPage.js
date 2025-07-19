import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import NotificationSystem from '../components/NotificationSystem';
import { 
  LoadingSpinner, 
  DataLoadingState, 
  ErrorState, 
  EmptyState 
} from '../components/LoadingComponents';
import { 
  ResponsiveStatsGrid, 
  ResponsiveActionBar,
  ResponsiveButtonGroup,
  ResponsiveCardGrid 
} from '../components/ResponsiveComponents';
import axios from 'axios';
import { getApiUrl } from '../utils/apiUrl';

function ChangePasswordPage() {
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Enhanced notification functions
  const showSuccessMessage = (message) => {
    if (window.showSuccess) window.showSuccess(message);
  };

  const showErrorMessage = (message) => {
    if (window.showError) window.showError(message);
  };

  const showInfoMessage = (message) => {
    if (window.showInfo) window.showInfo(message);
  };

  const showWarningMessage = (message) => {
    if (window.showWarning) window.showWarning(message);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const res = await axios.put(`${getApiUrl()}/auth/update_password`, {
        current_password: currentPassword,
        new_password: newPassword
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setSuccess(res.data.msg);
      setLoading(false);
      
      // Wait 2 seconds then redirect to dashboard
      setTimeout(() => {
        const role = localStorage.getItem('role');
        window.location.href = role === 'Admin' ? '/admin' : '/dashboard';
      }, 2000);
      
    } catch (err) {
      console.error('Password change error:', err);
      setError(err.response?.data?.msg || 'Failed to change password');
      setLoading(false);
    }
  };

  const handleSkip = () => {
    const role = localStorage.getItem('role');
    window.location.href = role === 'Admin' ? '/admin' : '/dashboard';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Change Your Password
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          You're using a temporary password. Please change it to secure your account.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
          
          {success && (
            <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
              {success}
              <p className="mt-2 text-sm">Redirecting to dashboard...</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="current-password" className="block text-sm font-medium text-gray-700">
                Current Password
              </label>
              <div className="mt-1">
                <input
                  id="current-password"
                  name="current-password"
                  type="password"
                  required
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Enter your current/temporary password"
                />
              </div>
            </div>

            <div>
              <label htmlFor="new-password" className="block text-sm font-medium text-gray-700">
                New Password
              </label>
              <div className="mt-1">
                <input
                  id="new-password"
                  name="new-password"
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Enter your new password"
                />
              </div>
            </div>

            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700">
                Confirm New Password
              </label>
              <div className="mt-1">
                <input
                  id="confirm-password"
                  name="confirm-password"
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="Confirm your new password"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Change Password'}
              </button>
            </div>

            <div className="flex justify-center">
              <button
                type="button"
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Skip for now
              </button>
            </div>
          </form>
        </div>
      </div>
      <NotificationSystem />
    </div>
  );
}

export default ChangePasswordPage;
