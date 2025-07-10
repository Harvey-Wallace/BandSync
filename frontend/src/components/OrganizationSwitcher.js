import React, { useState, useEffect, useRef } from 'react';
import { useOrganization } from '../contexts/OrganizationContext';

function OrganizationSwitcher() {
  const { currentOrganization, availableOrganizations, switchOrganization, loading, error } = useOrganization();
  const [showDropdown, setShowDropdown] = useState(false);
  const [switching, setSwitching] = useState(false);
  const dropdownRef = useRef(null);

  const handleSwitchOrganization = async (organizationId) => {
    setSwitching(true);
    const success = await switchOrganization(organizationId);
    setSwitching(false);
    if (success) {
      setShowDropdown(false);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showDropdown]);

  // Don't render if user only has one organization
  if (availableOrganizations.length <= 1) {
    return (
      <span className="navbar-text ms-2 d-none d-md-inline">
        <span className="badge organization-badge">
          {currentOrganization?.name || 'Loading...'}
        </span>
      </span>
    );
  }

  return (
    <div className="dropdown organization-switcher ms-2" ref={dropdownRef}>
      <button
        className="btn btn-link navbar-text text-white text-decoration-none p-0 d-flex align-items-center"
        onClick={() => setShowDropdown(!showDropdown)}
        disabled={loading || switching}
        title="Switch Organization"
      >
        <span className="badge organization-badge me-1">
          {currentOrganization?.name || 'Loading...'}
        </span>
        <i className={`bi bi-chevron-${showDropdown ? 'up' : 'down'} ms-1`}></i>
      </button>
      
      {showDropdown && (
        <div className="dropdown-menu dropdown-menu-end show position-absolute" style={{ top: '100%', right: 0, zIndex: 1050 }}>
          <div className="dropdown-header">
            <small className="text-muted">Switch Organization</small>
          </div>
          {availableOrganizations.map((org) => (
            <button
              key={org.id}
              className={`dropdown-item d-flex align-items-center ${
                currentOrganization?.id === org.id ? 'active' : ''
              }`}
              onClick={() => handleSwitchOrganization(org.id)}
              disabled={switching || currentOrganization?.id === org.id}
            >
              <i className="bi bi-building me-2"></i>
              <span className="flex-grow-1">{org.name}</span>
              {currentOrganization?.id === org.id && (
                <i className="bi bi-check-circle-fill text-success ms-2"></i>
              )}
              {org.role && (
                <small className="text-muted ms-2">({org.role})</small>
              )}
            </button>
          ))}
          {switching && (
            <div className="dropdown-item-text text-center">
              <div className="spinner-border spinner-border-sm" role="status">
                <span className="visually-hidden">Switching...</span>
              </div>
              <small className="text-muted ms-2">Switching...</small>
            </div>
          )}
          {error && (
            <div className="dropdown-item-text text-danger small">
              <i className="bi bi-exclamation-triangle me-1"></i>
              {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default OrganizationSwitcher;
