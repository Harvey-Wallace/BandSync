import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getApiUrl } from '../utils/apiUrl';

const OrganizationContext = createContext();

export const useOrganization = () => {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
};

export const OrganizationProvider = ({ children }) => {
  const [currentOrganization, setCurrentOrganization] = useState(null);
  const [availableOrganizations, setAvailableOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load current organization from localStorage or API
  const loadCurrentOrganization = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch(`${getApiUrl()}/organizations/current`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentOrganization(data.organization);
        // Update localStorage for compatibility
        localStorage.setItem('organization', data.organization.name);
        localStorage.setItem('organization_id', data.organization.id);
        localStorage.setItem('role', data.role);
      } else {
        // Fallback to localStorage
        const orgName = localStorage.getItem('organization');
        const orgId = localStorage.getItem('organization_id');
        if (orgName && orgId) {
          setCurrentOrganization({ id: parseInt(orgId), name: orgName });
        }
      }
    } catch (error) {
      console.error('Error loading current organization:', error);
      // Fallback to localStorage
      const orgName = localStorage.getItem('organization');
      const orgId = localStorage.getItem('organization_id');
      if (orgName && orgId) {
        setCurrentOrganization({ id: parseInt(orgId), name: orgName });
      }
    }
  }, []);

  // Load available organizations for the user
  const loadAvailableOrganizations = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch(`${getApiUrl()}/organizations/available`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableOrganizations(data.organizations || []);
      }
    } catch (error) {
      console.error('Error loading available organizations:', error);
      setError('Failed to load organizations');
    }
  }, []);

  // Switch to a different organization
  const switchOrganization = async (organizationId) => {
    const token = localStorage.getItem('token');
    if (!token) return false;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${getApiUrl()}/organizations/switch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ organization_id: organizationId })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Update token with new organization context
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('organization', data.organization.name);
        localStorage.setItem('organization_id', data.organization.id);
        localStorage.setItem('role', data.role);
        
        // Update state
        setCurrentOrganization(data.organization);
        
        // Trigger a page refresh to update all components with new context
        window.location.reload();
        
        return true;
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to switch organization');
        return false;
      }
    } catch (error) {
      console.error('Error switching organization:', error);
      setError('Failed to switch organization');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Initialize data on component mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      loadCurrentOrganization();
      loadAvailableOrganizations();
    }
  }, [loadCurrentOrganization, loadAvailableOrganizations]);

  // Listen for login events to reload organization data
  useEffect(() => {
    const handleLogin = () => {
      loadCurrentOrganization();
      loadAvailableOrganizations();
    };

    window.addEventListener('userLogin', handleLogin);
    return () => window.removeEventListener('userLogin', handleLogin);
  }, [loadCurrentOrganization, loadAvailableOrganizations]);

  const value = {
    currentOrganization,
    availableOrganizations,
    loading,
    error,
    switchOrganization,
    loadCurrentOrganization,
    loadAvailableOrganizations
  };

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  );
};
