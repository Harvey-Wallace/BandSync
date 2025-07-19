import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import UserAvatar from '../components/UserAvatar';
import PWAStatus from '../components/PWAStatus';
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
import apiClient from '../utils/api';
import axios from 'axios';
import { getApiUrl } from '../utils/apiUrl';

function ProfilePage() {
  const [user, setUser] = useState({
    username: localStorage.getItem('username') || '',
    name: '',
    email: '',
    address: '',
    phone: '',
    avatar_url: localStorage.getItem('avatar_url') || ''
  });
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    address: '',
    phone: '',
    avatar_url: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [avatarFile, setAvatarFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

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

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/auth/profile');
      const userData = response.data;
      setUser(userData);
      setFormData(prev => ({
        ...prev,
        name: userData.name || '',
        email: userData.email || '',
        address: userData.address || '',
        phone: userData.phone || '',
        avatar_url: userData.avatar_url || ''
      }));
    } catch (error) {
      showErrorMessage('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        showErrorMessage('Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        showErrorMessage('File size too large. Maximum size is 5MB');
        return;
      }
      
      setAvatarFile(file);
      
      // Create preview URL
      const previewUrl = URL.createObjectURL(file);
      setFormData(prev => ({ ...prev, avatar_url: previewUrl }));
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      let avatarUrl = formData.avatar_url;
      
      // Upload new avatar if file is selected
      if (avatarFile) {
        avatarUrl = await handleUploadAvatar();
      }
      
      // Update profile information
      const profileData = {
        name: formData.name,
        email: formData.email,
        address: formData.address,
        phone: formData.phone,
        avatar_url: avatarUrl
      };

      await axios.put(`${getApiUrl()}/auth/profile`, 
        profileData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (avatarUrl !== user.avatar_url) {
        localStorage.setItem('avatar_url', avatarUrl);
      }
      
      // Update localStorage with new profile data
      localStorage.setItem('name', formData.name);
      localStorage.setItem('email', formData.email);
      localStorage.setItem('phone', formData.phone);
      localStorage.setItem('address', formData.address);

      setUser(prev => ({
        ...prev,
        name: formData.name,
        email: formData.email,
        address: formData.address,
        phone: formData.phone,
        avatar_url: avatarUrl
      }));

      // Clear file selection
      setAvatarFile(null);
      
      // Dispatch custom event to notify navbar of profile update
      window.dispatchEvent(new CustomEvent('profileUpdated', {
        detail: {
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          address: formData.address,
          avatar_url: avatarUrl
        }
      }));

      showSuccessMessage('Profile updated successfully!');
    } catch (error) {
      showErrorMessage('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    
    if (formData.newPassword !== formData.confirmPassword) {
      showErrorMessage('New passwords do not match');
      return;
    }

    if (formData.newPassword.length < 6) {
      showErrorMessage('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      await axios.put(`${getApiUrl()}/auth/update_password`, 
        { 
          current_password: formData.currentPassword,
          new_password: formData.newPassword 
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));

      showSuccessMessage('Password updated successfully!');
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to update password';
      showErrorMessage(message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadAvatar = async () => {
    if (!avatarFile) return null;
    
    setUploading(true);
    const token = localStorage.getItem('token');
    const uploadFormData = new FormData();
    uploadFormData.append('file', avatarFile);
    
    try {
      const response = await axios.post(
        `${getApiUrl()}/auth/upload-avatar`,
        uploadFormData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      setUploading(false);
      return response.data.avatar_url;
    } catch (error) {
      setUploading(false);
      throw error;
    }
  };

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="card shadow-sm">
              <div className="card-header">
                <div className="d-flex align-items-center justify-content-between">
                  <h4 className="mb-0">
                    <i className="bi bi-person-circle me-2"></i>
                    User Profile
                  </h4>
                  <div className="d-flex align-items-center">
                    <UserAvatar user={user} size={48} />
                    <div className="ms-3 d-none d-sm-block">
                      <div className="fw-bold">{user.username}</div>
                      <div className="text-muted small">{user.email}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="card-body p-0">
                <ul className="nav nav-tabs nav-justified" role="tablist">
                  <li className="nav-item" role="presentation">
                    <button 
                      className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
                      onClick={() => setActiveTab('profile')}
                      type="button"
                    >
                      <i className="bi bi-person me-1"></i>
                      <span className="d-none d-sm-inline">Profile Info</span>
                      <span className="d-sm-none">Profile</span>
                    </button>
                  </li>
                  <li className="nav-item" role="presentation">
                    <button 
                      className={`nav-link ${activeTab === 'password' ? 'active' : ''}`}
                      onClick={() => setActiveTab('password')}
                      type="button"
                    >
                      <i className="bi bi-lock me-1"></i>
                      <span className="d-none d-sm-inline">Change Password</span>
                      <span className="d-sm-none">Password</span>
                    </button>
                  </li>
                  <li className="nav-item" role="presentation">
                    <button 
                      className={`nav-link ${activeTab === 'app' ? 'active' : ''}`}
                      onClick={() => setActiveTab('app')}
                      type="button"
                    >
                      <i className="bi bi-phone me-1"></i>
                      <span className="d-none d-sm-inline">App Status</span>
                      <span className="d-sm-none">App</span>
                    </button>
                  </li>
                </ul>

                <div className="p-4">
                  {/* Profile Tab */}
                  {activeTab === 'profile' && (
                    <form onSubmit={handleUpdateProfile}>
                      <div className="row">
                        <div className="col-md-6">
                          <div className="mb-3">
                            <label htmlFor="username" className="form-label">Username</label>
                            <input
                              type="text"
                              className="form-control"
                              id="username"
                              value={user.username}
                              disabled
                            />
                            <div className="form-text">Username cannot be changed</div>
                          </div>

                          <div className="mb-3">
                            <label htmlFor="name" className="form-label">Full Name</label>
                            <input
                              type="text"
                              className="form-control"
                              id="name"
                              name="name"
                              value={formData.name}
                              onChange={handleInputChange}
                              placeholder="Enter your full name"
                            />
                          </div>

                          <div className="mb-3">
                            <label htmlFor="email" className="form-label">Email Address</label>
                            <input
                              type="email"
                              className="form-control"
                              id="email"
                              name="email"
                              value={formData.email}
                              onChange={handleInputChange}
                              required
                            />
                          </div>

                          <div className="mb-3">
                            <label htmlFor="phone" className="form-label">Phone Number</label>
                            <input
                              type="tel"
                              className="form-control"
                              id="phone"
                              name="phone"
                              value={formData.phone}
                              onChange={handleInputChange}
                              placeholder="(555) 123-4567"
                            />
                          </div>

                          <div className="mb-3">
                            <label htmlFor="address" className="form-label">Address</label>
                            <textarea
                              className="form-control"
                              id="address"
                              name="address"
                              value={formData.address}
                              onChange={handleInputChange}
                              rows="3"
                              placeholder="Enter your address"
                            />
                          </div>

                          <div className="mb-3">
                            <label htmlFor="avatar_file" className="form-label">Profile Picture</label>
                            <input
                              type="file"
                              className="form-control"
                              id="avatar_file"
                              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                              onChange={handleFileChange}
                            />
                            <div className="form-text">
                              Upload a profile picture (PNG, JPG, JPEG, GIF, WebP - Max 5MB)
                            </div>
                          </div>
                        </div>

                        <div className="col-md-6">
                          <div className="card bg-light">
                            <div className="card-body text-center">
                              <h6 className="card-title">Avatar Preview</h6>
                              <UserAvatar 
                                user={{ 
                                  username: user.username, 
                                  avatar_url: formData.avatar_url 
                                }} 
                                size={120} 
                                className="mb-3"
                              />
                              <div className="small text-muted">
                                {formData.avatar_url ? 'Custom avatar' : 'Default initials'}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="d-flex gap-2 justify-content-end">
                        <button 
                          type="button" 
                          className="btn btn-secondary"
                          onClick={loadUserProfile}
                          disabled={loading}
                        >
                          Reset
                        </button>
                        <button 
                          type="submit" 
                          className="btn btn-primary"
                          disabled={loading || uploading}
                        >
                          {loading || uploading ? <LoadingSpinner size="sm" /> : 'Update Profile'}
                          {uploading && ' Uploading...'}
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Password Tab */}
                  {activeTab === 'password' && (
                    <form onSubmit={handleUpdatePassword}>
                      <div className="row justify-content-center">
                        <div className="col-md-8">
                          <div className="mb-3">
                            <label htmlFor="currentPassword" className="form-label">Current Password</label>
                            <input
                              type="password"
                              className="form-control"
                              id="currentPassword"
                              name="currentPassword"
                              value={formData.currentPassword}
                              onChange={handleInputChange}
                              required
                            />
                          </div>

                          <div className="mb-3">
                            <label htmlFor="newPassword" className="form-label">New Password</label>
                            <input
                              type="password"
                              className="form-control"
                              id="newPassword"
                              name="newPassword"
                              value={formData.newPassword}
                              onChange={handleInputChange}
                              minLength="6"
                              required
                            />
                            <div className="form-text">Password must be at least 6 characters long</div>
                          </div>

                          <div className="mb-3">
                            <label htmlFor="confirmPassword" className="form-label">Confirm New Password</label>
                            <input
                              type="password"
                              className="form-control"
                              id="confirmPassword"
                              name="confirmPassword"
                              value={formData.confirmPassword}
                              onChange={handleInputChange}
                              minLength="6"
                              required
                            />
                          </div>

                          <div className="d-flex gap-2 justify-content-end">
                            <button 
                              type="button" 
                              className="btn btn-secondary"
                              onClick={() => setFormData(prev => ({
                                ...prev,
                                currentPassword: '',
                                newPassword: '',
                                confirmPassword: ''
                              }))}
                              disabled={loading}
                            >
                              Clear
                            </button>
                            <button 
                              type="submit" 
                              className="btn btn-primary"
                              disabled={loading}
                            >
                              {loading ? <LoadingSpinner size="sm" /> : 'Update Password'}
                            </button>
                          </div>
                        </div>
                      </div>
                    </form>
                  )}

                  {/* App Status Tab */}
                  {activeTab === 'app' && (
                    <PWAStatus />
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <NotificationSystem />
      </div>
    </>
  );
}

export default ProfilePage;
