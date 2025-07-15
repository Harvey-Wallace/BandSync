import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import UserAvatar from './UserAvatar';
import OrganizationSwitcher from './OrganizationSwitcher';
import { useTheme } from '../contexts/ThemeContext';
import { useOrganization } from '../contexts/OrganizationContext';
import { getApiUrl } from '../utils/apiUrl';

function Navbar() {
  const role = localStorage.getItem('role');
  const username = localStorage.getItem('username');
  console.log('Navbar Debug - Role:', role, 'Username:', username); // Debug log
  const { isDark, toggleTheme, orgThemeColor, updateOrgThemeColor } = useTheme();
  const { currentOrganization } = useOrganization();
  const [orgLogo, setOrgLogo] = useState('');
  const [showProfile, setShowProfile] = useState(false);
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    phone: '',
    address: ''
  });

  const loadProfileData = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        console.log('Loading profile data...'); // Debug log
        const response = await fetch(`${getApiUrl()}/auth/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          console.log('Profile data loaded:', data); // Debug log
          setProfileData({
            name: data.name || '',
            email: data.email || '',
            phone: data.phone || '',
            address: data.address || ''
          });
          // Update localStorage as well for persistence
          localStorage.setItem('name', data.name || '');
          localStorage.setItem('email', data.email || '');
          localStorage.setItem('phone', data.phone || '');
          localStorage.setItem('address', data.address || '');
          if (data.avatar_url) {
            localStorage.setItem('avatar_url', data.avatar_url);
            setUser(prev => ({ ...prev, avatar_url: data.avatar_url }));
          }
        } else {
          console.error('Failed to load profile data:', response.status);
          // Fallback to localStorage data
          setProfileData({
            name: localStorage.getItem('name') || '',
            email: localStorage.getItem('email') || '',
            phone: localStorage.getItem('phone') || '',
            address: localStorage.getItem('address') || ''
          });
        }
      } catch (error) {
        console.error('Error loading profile data:', error);
        // Fallback to localStorage data
        setProfileData({
          name: localStorage.getItem('name') || '',
          email: localStorage.getItem('email') || '',
          phone: localStorage.getItem('phone') || '',
          address: localStorage.getItem('address') || ''
        });
      }
    }
  }, []);
  
  const [user, setUser] = useState({
    username: username,
    avatar_url: localStorage.getItem('avatar_url')
  });

  // Initialize profile data from localStorage on mount
  useEffect(() => {
    // Load cached profile data immediately
    setProfileData({
      name: localStorage.getItem('name') || '',
      email: localStorage.getItem('email') || '',
      phone: localStorage.getItem('phone') || '',
      address: localStorage.getItem('address') || ''
    });
    
    // Load fresh data from API
    loadProfileData();
  }, [loadProfileData]);

  // Load organization data from backend
  const loadOrgData = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        console.log('Loading organization data...'); // Debug log
        
        // Try the public endpoint first (for logo and theme)
        let res = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/organizations/current`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // If that fails, try the admin endpoint
        if (!res.ok) {
          console.log('Public org endpoint failed, trying admin endpoint...');
          res = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/admin/organization`, {
            headers: { Authorization: `Bearer ${token}` }
          });
        }
        
        if (res.ok) {
          const orgData = await res.json();
          console.log('Organization data loaded:', orgData); // Debug log
          
          // Handle both direct response and nested organization object
          const organization = orgData.organization || orgData;
          
          if (organization.logo_url) {
            console.log('Setting logo URL:', organization.logo_url);
            setOrgLogo(organization.logo_url);
          }
          if (organization.theme_color && organization.theme_color !== orgThemeColor) {
            console.log('Setting theme color:', organization.theme_color);
            updateOrgThemeColor(organization.theme_color);
          }
        } else {
          console.error('Failed to load organization data:', res.status);
        }
      } catch (error) {
        console.error('Error loading org data:', error);
      }
    }
  }, [orgThemeColor, updateOrgThemeColor]);

  useEffect(() => {
    loadOrgData();
    loadProfileData();
  }, [loadOrgData, loadProfileData]);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  const navbarStyle = {
    backgroundColor: orgThemeColor,
    borderBottom: `3px solid ${orgThemeColor}dd`
  };

  const toggleProfile = () => {
    setShowProfile(!showProfile);
    if (!showProfile) {
      loadProfileData(); // Refresh profile data when opening
    }
  };

  // Add window click listener to close profile bubble
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showProfile && !event.target.closest('.profile-bubble') && !event.target.closest('.avatar-button')) {
        setShowProfile(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showProfile]);

  // Listen for profile updates
  useEffect(() => {
    const handleProfileUpdate = (event) => {
      const updatedProfile = event.detail;
      setProfileData(updatedProfile);
      // Update user avatar URL if it changed
      if (updatedProfile.avatar_url) {
        setUser(prev => ({ ...prev, avatar_url: updatedProfile.avatar_url }));
      }
    };

    window.addEventListener('profileUpdated', handleProfileUpdate);
    return () => {
      window.removeEventListener('profileUpdated', handleProfileUpdate);
    };
  }, []);

  // Listen for organization updates
  useEffect(() => {
    const handleOrgUpdate = () => {
      loadOrgData();
    };

    window.addEventListener('organizationUpdated', handleOrgUpdate);
    return () => {
      window.removeEventListener('organizationUpdated', handleOrgUpdate);
    };
  }, [loadOrgData]);

  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={navbarStyle}>
      <div className="container-fluid">
        <Link className="navbar-brand fw-bold d-flex align-items-center" to="/">
          {orgLogo ? (
            <img 
              src={orgLogo} 
              alt="Logo" 
              style={{ 
                height: '32px', 
                maxWidth: '120px',
                objectFit: 'contain',
                marginRight: '8px'
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'inline';
              }}
            />
          ) : null}
          <span style={{ display: orgLogo ? 'none' : 'inline' }}>
            <i className="bi bi-music-note me-2"></i>
          </span>
          BandSync
        </Link>
        
        {/* Organization Switcher */}
        <OrganizationSwitcher />
        
        {/* Mobile menu toggle */}
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        
        <div className="navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0"
              style={{flexWrap: 'nowrap', overflowX: 'auto'}}>
            <li className="nav-item">
              <Link className="nav-link text-white px-2" to="/dashboard">
                <i className="bi bi-house-door me-1"></i>
                <span>Dashboard</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link text-white px-2" to="/events">
                <i className="bi bi-calendar-event me-1"></i>
                <span>Events</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link text-white px-2" to="/messaging">
                <i className="bi bi-chat-dots me-1"></i>
                <span>Messages</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link text-white px-2" to="/substitution">
                <i className="bi bi-person-plus me-1"></i>
                <span>Substitutes</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link text-white px-2" to="/polls">
                <i className="bi bi-bar-chart me-1"></i>
                <span>Polls</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link text-white px-2" to="/admin">
                <i className="bi bi-gear me-1"></i>
                <span>Admin</span>
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link text-white px-2" to="/bulk-operations">
                <i className="bi bi-stack me-1"></i>
                <span>Bulk</span>
              </Link>
            </li>
          </ul>
          
          <div className="d-flex align-items-center gap-2">
            {/* User Avatar and Menu */}
            <div className="position-relative">
              <button 
                className="btn btn-link p-0 d-flex align-items-center text-decoration-none avatar-button"
                onClick={toggleProfile}
                title="Profile Information"
              >
                <UserAvatar user={user} size={32} className="me-2" />
                <span className="text-white d-none d-sm-inline">{username}</span>
                <i className={`bi bi-chevron-${showProfile ? 'up' : 'down'} text-white ms-1`}></i>
              </button>
              
              <button 
                className="btn btn-link p-0 ms-1"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                title="Menu"
              >
                <i className="bi bi-three-dots-vertical text-white"></i>
              </button>
              <ul className="dropdown-menu dropdown-menu-end">
                <li>
                  <Link className="dropdown-item" to="/profile">
                    <i className="bi bi-person me-2"></i>Profile
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/email-preferences">
                    <i className="bi bi-envelope-gear me-2"></i>Email Preferences
                  </Link>
                </li>
                <li>
                  <Link className="dropdown-item" to="/calendar">
                    <i className="bi bi-calendar-plus me-2"></i>Calendar Sync
                  </Link>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <button className="dropdown-item" onClick={handleLogout}>
                    <i className="bi bi-box-arrow-right me-2"></i>Logout
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Profile bubble section */}
      {showProfile && (
        <div className="profile-bubble position-absolute shadow-lg" style={{ top: '65px', right: '20px', zIndex: 1050 }}>
          <div className="profile-bubble-header d-flex align-items-center mb-3">
            <UserAvatar user={user} size={40} />
            <div className="ms-3">
              <h6 className="mb-0 text-dark fw-bold">{profileData.name || username}</h6>
              <small className="text-muted">{username}</small>
            </div>
          </div>
          
          <div className="profile-info mb-3">
            {profileData.email && (
              <div className="info-item mb-2">
                <i className="bi bi-envelope text-muted me-2"></i>
                <span className="text-dark">{profileData.email}</span>
              </div>
            )}
            {profileData.phone && (
              <div className="info-item mb-2">
                <i className="bi bi-telephone text-muted me-2"></i>
                <span className="text-dark">{profileData.phone}</span>
              </div>
            )}
            {currentOrganization && (
              <div className="info-item mb-2">
                <i className="bi bi-building text-muted me-2"></i>
                <span className="text-dark">{currentOrganization.name}</span>
              </div>
            )}
            {profileData.address && (
              <div className="info-item mb-2">
                <i className="bi bi-geo-alt text-muted me-2"></i>
                <span className="text-dark">{profileData.address}</span>
              </div>
            )}
          </div>
          
          <hr className="my-3" />
          
          <div className="d-flex justify-content-between align-items-center mb-3">
            <span className="text-dark fw-medium">
              <i className={`bi bi-${isDark ? 'moon' : 'sun'} me-2`}></i>
              {isDark ? 'Dark' : 'Light'} Mode
            </span>
            <div className="form-check form-switch">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="themeSwitch"
                checked={isDark}
                onChange={toggleTheme}
              />
              <label className="form-check-label" htmlFor="themeSwitch"></label>
            </div>
          </div>
          
          <div className="d-grid gap-2">
            <Link to="/profile" className="btn btn-outline-primary btn-sm">
              <i className="bi bi-person-gear me-1"></i>
              Edit Profile
            </Link>
            <Link to="/email-preferences" className="btn btn-outline-info btn-sm">
              <i className="bi bi-envelope-gear me-1"></i>
              Email Preferences
            </Link>
            <Link to="/calendar" className="btn btn-outline-success btn-sm">
              <i className="bi bi-calendar-plus me-1"></i>
              Calendar Sync
            </Link>
            <button 
              className="btn btn-outline-secondary btn-sm"
              onClick={handleLogout}
            >
              <i className="bi bi-box-arrow-right me-1"></i>
              Sign Out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
