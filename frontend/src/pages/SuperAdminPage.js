import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../utils/apiUrl';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import { 
  LoadingSpinner, 
  LoadingButton, 
  DataLoadingState, 
  ErrorState, 
  EmptyState,
  StatsCardSkeleton 
} from '../components/LoadingComponents';
import { 
  ResponsiveStatsGrid, 
  ResponsiveTabNav, 
  ResponsiveDataTable,
  ResponsiveActionBar 
} from '../components/ResponsiveComponents';
import '../styles/custom.css';

function SuperAdminPage() {
  // Data states
  const [overview, setOverview] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [orgDetails, setOrgDetails] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [bulkOperation, setBulkOperation] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [orgPerformance, setOrgPerformance] = useState(null);
  const [securityData, setSecurityData] = useState(null);
  const [auditLogs, setAuditLogs] = useState(null);
  const [securityEvents, setSecurityEvents] = useState(null);
  
  // Enhanced loading states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [loadingStates, setLoadingStates] = useState({
    overview: false,
    analytics: false,
    security: false,
    auditLogs: false,
    securityEvents: false,
    systemHealth: false,
    orgDetails: false,
    search: false,
    bulkOperation: false
  });
  
  // Error states for individual components
  const [errorStates, setErrorStates] = useState({});
  
  const navigate = useNavigate();

  const isSuperAdmin = localStorage.getItem('super_admin') === 'true';

  // Enhanced utility functions for loading states and notifications
  const setLoadingState = (key, isLoading) => {
    setLoadingStates(prev => ({ ...prev, [key]: isLoading }));
  };

  const setErrorState = (key, error) => {
    setErrorStates(prev => ({ ...prev, [key]: error }));
    if (error && window.showError) {
      window.showError(`Failed to load ${key}: ${error}`);
    }
  };

  const clearErrorState = (key) => {
    setErrorStates(prev => ({ ...prev, [key]: null }));
  };

  const showSuccessMessage = (message) => {
    if (window.showSuccess) {
      window.showSuccess(message);
    }
  };

  const showErrorMessage = (message) => {
    if (window.showError) {
      window.showError(message);
    }
  };

  const showInfoMessage = (message) => {
    if (window.showInfo) {
      window.showInfo(message);
    }
  };

  const showWarning = (message) => {
    if (window.showWarning) {
      window.showWarning(message);
    }
  };

  // Enhanced data loading with better error handling and notifications
  const enhancedApiCall = async (url, key, successMessage = null) => {
    try {
      setLoadingState(key, true);
      clearErrorState(key);
      
      const token = localStorage.getItem('token');
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`${key} data:`, data);
        
        if (successMessage) {
          showSuccessMessage(successMessage);
        }
        
        return data;
      } else {
        const errorData = await response.text();
        console.error(`${key} error:`, response.status, errorData);
        setErrorState(key, `HTTP ${response.status}`);
        return null;
      }
    } catch (err) {
      console.error(`Error loading ${key}:`, err);
      setErrorState(key, err.message);
      return null;
    } finally {
      setLoadingState(key, false);
    }
  };

  useEffect(() => {
    if (!isSuperAdmin) {
      navigate('/dashboard');
      return;
    }
    
    // Show welcome message
    setTimeout(() => {
      showInfoMessage('Welcome to Super Admin Dashboard');
    }, 500);
    
    // Load initial data
    loadOverview();
    loadSystemHealth();
    loadAnalytics();
  }, [isSuperAdmin, navigate]);

  // Enhanced API functions with better UX
  const loadSystemHealth = async () => {
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/system/health`,
      'systemHealth'
    );
    if (data) {
      setSystemHealth(data);
    }
  };

  const loadOverview = async () => {
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/overview`,
      'overview'
    );
    if (data) {
      setOverview(data);
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/analytics`,
      'analytics'
    );
    if (data) {
      setAnalyticsData(data);
    }
  };

  const loadSecurity = async () => {
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/security/audit-summary`,
      'security'
    );
    if (data) {
      setSecurityData(data);
    }
  };

  const loadAuditLogs = async () => {
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/security/audit-log?per_page=50`,
      'auditLogs'
    );
    if (data) {
      setAuditLogs(data);
    }
  };

  const loadSecurityEvents = async () => {
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/security/security-events?per_page=50`,
      'securityEvents'
    );
    if (data) {
      setSecurityEvents(data);
    }
  };

  const loadTrends = async (period = '30d', metric = 'users') => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/analytics/trends?period=${period}&metric=${metric}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Trends data:', data);
        setTrendsData(data);
      } else {
        console.error('Trends error:', response.status);
      }
    } catch (err) {
      console.error('Error loading trends:', err);
    }
  };

  // Phase 3 Security & Compliance Functions
  const loadOrgDetails = async (orgId) => {
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/organization/${orgId}/details`,
      'orgDetails'
    );
    if (data) {
      setOrgDetails(data);
      setSelectedOrg(orgId);
      showSuccessMessage('Organization details loaded successfully');
    }
  };

  const searchUsers = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    setLoadingState('search', true);
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/users/search?q=${encodeURIComponent(searchTerm)}`,
      'search'
    );
    if (data) {
      setSearchResults(data.users || []);
      showSuccessMessage(`Found ${data.users?.length || 0} users`);
    }
  };

  const troubleshootUser = async (userId) => {
    setLoadingState('troubleshoot', true);
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/troubleshoot/user/${userId}`,
      'troubleshoot'
    );
    if (data) {
      showSuccessMessage(`Troubleshooting data retrieved for user ${data.user?.username}`);
      // Could open a modal or navigate to a detailed view
      console.log('User troubleshooting data:', data);
    }
  };

  const resetUserPassword = async (userId, username) => {
    if (!window.confirm(`Reset password for ${username}? This will generate a temporary password.`)) {
      return;
    }

    setLoadingState('resetPassword', true);
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/user/${userId}/reset-password`,
      'resetPassword'
    );
    if (data) {
      showSuccessMessage(`Password reset for ${username}!\nNew password: ${data.new_password}\n\nUser will need to change this on next login.`);
    }
  };

  const impersonateUser = async (userId, username) => {
    if (!window.confirm(`Impersonate user ${username}? This will log you in as them.`)) {
      return;
    }

    setLoadingState('impersonate', true);
    const data = await enhancedApiCall(
      `${getApiUrl()}/super-admin/user/${userId}/impersonate`,
      'impersonate'
    );
    if (data) {
      // Store the impersonation token
      localStorage.setItem('token', data.impersonation_token);
      localStorage.setItem('organization', data.organization.name);
      localStorage.setItem('organization_id', data.organization.id);
      localStorage.setItem('role', data.role);
      localStorage.setItem('impersonating', 'true');
      localStorage.setItem('original_admin', 'Harvey258');
      
      showSuccessMessage(`Now impersonating ${username}. You can return to Super Admin mode by logging out and back in.`);
      window.location.href = '/dashboard';
    }
  };

  const handleBulkOperation = async () => {
    if (!bulkOperation || selectedUsers.length === 0) {
      showWarning('Please select an operation and at least one user.');
      return;
    }

    const operationNames = {
      'disable': 'disable',
      'enable': 'enable', 
      'reset_passwords': 'reset passwords for',
      'delete': 'delete'
    };

    if (!window.confirm(`${operationNames[bulkOperation]} ${selectedUsers.length} users?`)) {
      return;
    }

    try {
      setLoadingState('bulkOperation', true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/users/bulk-operations`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          operation: bulkOperation,
          user_ids: selectedUsers
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        showSuccessMessage(`Bulk operation completed!\n${data.results.join('\n')}`);
        setSelectedUsers([]);
        setBulkOperation('');
        // Refresh search results
        if (searchTerm) {
          searchUsers();
        }
      } else {
        showErrorMessage('Failed to perform bulk operation');
      }
    } catch (err) {
      showErrorMessage('Error performing bulk operation');
      console.error(err);
    } finally {
      setLoadingState('bulkOperation', false);
    }
  };

  const toggleUserSelection = (userId) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  if (!isSuperAdmin) {
    return (
      <div className="container mt-4">
        <div className="alert alert-danger">
          <h4>Access Denied</h4>
          <p>Super Admin access required.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <NotificationSystem />
      <div className="container-fluid mt-4 px-3">
        <div className="row">
          <div className="col-12">
            <ResponsiveActionBar
              title="Super Admin Dashboard"
              actions={[
                {
                  label: 'Refresh All',
                  shortLabel: 'Refresh',
                  icon: 'arrow-clockwise',
                  variant: 'btn-outline-primary',
                  onClick: () => {
                    loadOverview();
                    loadSystemHealth();
                    loadAnalytics();
                    showInfoMessage('Refreshing all dashboard data...');
                  }
                }
              ]}
            />

            {/* Enhanced Navigation Tabs */}
            <ResponsiveTabNav
              tabs={[
                { 
                  id: 'overview', 
                  label: 'Overview', 
                  shortLabel: 'Overview',
                  icon: 'graph-up' 
                },
                { 
                  id: 'analytics', 
                  label: 'Analytics', 
                  shortLabel: 'Analytics',
                  icon: 'bar-chart',
                  badge: analyticsData ? { value: '✓', type: 'success' } : null
                },
                { 
                  id: 'users', 
                  label: 'User Management', 
                  shortLabel: 'Users',
                  icon: 'people'
                },
                { 
                  id: 'health', 
                  label: 'System Health', 
                  shortLabel: 'Health',
                  icon: 'heart-pulse',
                  badge: systemHealth?.status === 'healthy' ? { value: '✓', type: 'success' } : null
                },
                { 
                  id: 'security', 
                  label: 'Security', 
                  shortLabel: 'Security',
                  icon: 'shield-check',
                  badge: { value: 'Phase 3', type: 'info' }
                }
              ]}
              activeTab={activeTab}
              onTabChange={(tabId) => {
                setActiveTab(tabId);
                // Auto-load data when switching tabs
                switch(tabId) {
                  case 'analytics':
                    if (!analyticsData) loadAnalytics();
                    break;
                  case 'security':
                    if (!securityData) loadSecurity();
                    if (!auditLogs) loadAuditLogs();
                    if (!securityEvents) loadSecurityEvents();
                    break;
                  default:
                    break;
                }
              }}
            />
            {/* Tab Content Area */}
            <div className="fade-in">
              {error && (
                <div className="alert alert-danger bounce-in" role="alert">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {error}
                  <button 
                    type="button" 
                    className="btn-close float-end" 
                    onClick={() => setError('')}
                    aria-label="Close"
                  ></button>
                </div>
              )}

              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="slide-in-right">
                  {loading ? (
                    <DataLoadingState type="skeleton" message="Loading overview data..." />
                  ) : overview ? (
                    <>
                      {/* Enhanced Overview Stats */}
                      <ResponsiveStatsGrid
                        stats={[
                          {
                            label: 'Total Users',
                            value: overview.stats?.total_users?.toLocaleString() || 0,
                            subtitle: `${overview.active_users || 0} active`,
                            icon: 'people'
                          },
                          {
                            label: 'Organizations',
                            value: overview.stats?.total_organizations?.toLocaleString() || 0,
                            subtitle: `${overview.active_organizations || 0} active`,
                            icon: 'building'
                          },
                          {
                            label: 'Total Events',
                            value: overview.stats?.total_events?.toLocaleString() || 0,
                            subtitle: `${overview.upcoming_events || 0} upcoming`,
                            icon: 'calendar-event'
                          },
                          {
                            label: 'System Health',
                            value: systemHealth?.status || 'Unknown',
                            subtitle: `${systemHealth?.uptime || 'N/A'} uptime`,
                            icon: 'heart-pulse'
                          }
                        ]}
                        className="mb-4"
                      />

                      {/* Organizations Overview */}
                      <div className="row">
                        <div className="col-12">
                          <div className="card">
                            <div className="card-header">
                              <h5 className="mb-0">
                                <i className="bi bi-building me-2"></i>
                                Organizations Overview
                              </h5>
                            </div>
                            <div className="card-body">
                              <div className="table-responsive">
                                <table className="table table-hover">
                                  <thead>
                                    <tr>
                                      <th>Organization</th>
                                      <th>Users</th>
                                      <th>Events</th>
                                      <th>Created</th>
                                      <th>Actions</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {overview.organizations.map(org => (
                                      <tr key={org.id}>
                                        <td>
                                          <strong>{org.name}</strong>
                                        </td>
                                        <td>
                                          <span className="badge bg-primary">{org.user_count}</span>
                                        </td>
                                        <td>
                                          <span className="badge bg-info">{org.event_count}</span>
                                        </td>
                                        <td>
                                          {org.created_at ? new Date(org.created_at).toLocaleDateString() : 'N/A'}
                                        </td>
                                        <td>
                                          <button 
                                            className="btn btn-sm btn-outline-primary"
                                            onClick={() => loadOrgDetails(org.id)}
                                          >
                                            <i className="bi bi-eye me-1"></i>
                                            View Details
                                          </button>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <ErrorState 
                      message="Failed to load overview data" 
                      onRetry={() => loadOverview()} 
                    />
                  )}
                </div>
              )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <>
          {analyticsData && (
            <>
              {/* Advanced Analytics Overview */}
              <div className="row mb-4">
                <div className="col-12">
                  <div className="card">
                    <div className="card-header">
                      <h5 className="mb-0">
                        <i className="bi bi-graph-up me-2"></i>
                        Platform Analytics
                      </h5>
                    </div>
                    <div className="card-body">
                      <div className="row">
                        <div className="col-md-3">
                          <div className="text-center p-3">
                            <h6 className="text-muted">User Growth (30d)</h6>
                            <h3 className="text-success">+{analyticsData.overview.users.new_30d}</h3>
                            <small className="text-muted">
                              {analyticsData.overview.users.growth_rate_30d}% growth rate
                            </small>
                          </div>
                        </div>
                        <div className="col-md-3">
                          <div className="text-center p-3">
                            <h6 className="text-muted">Active Users (30d)</h6>
                            <h3 className="text-info">{analyticsData.overview.users.active_30d}</h3>
                            <small className="text-muted">
                              {Math.round((analyticsData.overview.users.active_30d / analyticsData.overview.users.total) * 100)}% of total
                            </small>
                          </div>
                        </div>
                        <div className="col-md-3">
                          <div className="text-center p-3">
                            <h6 className="text-muted">Org Activity Rate</h6>
                            <h3 className="text-warning">{analyticsData.overview.organizations.activity_rate}%</h3>
                            <small className="text-muted">
                              {analyticsData.overview.organizations.active_30d} of {analyticsData.overview.organizations.total} active
                            </small>
                          </div>
                        </div>
                        <div className="col-md-3">
                          <div className="text-center p-3">
                            <h6 className="text-muted">Engagement Rate</h6>
                            <h3 className="text-primary">{analyticsData.overview.engagement.rsvp_rate}%</h3>
                            <small className="text-muted">
                              {analyticsData.overview.events.rsvps_30d} RSVPs in 30d
                            </small>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Platform Health Metrics */}
              <div className="row mb-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h6 className="mb-0">Platform Health Indicators</h6>
                    </div>
                    <div className="card-body">
                      <div className="mb-3">
                        <div className="d-flex justify-content-between">
                          <span>Events per User</span>
                          <strong>{analyticsData.overview.engagement.events_per_user}</strong>
                        </div>
                        <div className="progress" style={{height: '6px'}}>
                          <div 
                            className="progress-bar bg-success" 
                            style={{width: `${Math.min(analyticsData.overview.engagement.events_per_user * 20, 100)}%`}}
                          ></div>
                        </div>
                      </div>
                      <div className="mb-3">
                        <div className="d-flex justify-content-between">
                          <span>Avg RSVPs per Event</span>
                          <strong>{analyticsData.overview.engagement.avg_rsvps_per_event}</strong>
                        </div>
                        <div className="progress" style={{height: '6px'}}>
                          <div 
                            className="progress-bar bg-info" 
                            style={{width: `${Math.min(analyticsData.overview.engagement.avg_rsvps_per_event * 10, 100)}%`}}
                          ></div>
                        </div>
                      </div>
                      <div className="mb-3">
                        <div className="d-flex justify-content-between">
                          <span>Avg Users per Org</span>
                          <strong>{analyticsData.overview.organizations.avg_users_per_org}</strong>
                        </div>
                        <div className="progress" style={{height: '6px'}}>
                          <div 
                            className="progress-bar bg-warning" 
                            style={{width: `${Math.min(analyticsData.overview.organizations.avg_users_per_org * 5, 100)}%`}}
                          ></div>
                        </div>
                      </div>
                      <div className="mb-0">
                        <div className="d-flex justify-content-between">
                          <span>Avg Events per Org</span>
                          <strong>{analyticsData.overview.events.avg_per_org}</strong>
                        </div>
                        <div className="progress" style={{height: '6px'}}>
                          <div 
                            className="progress-bar bg-primary" 
                            style={{width: `${Math.min(analyticsData.overview.events.avg_per_org * 5, 100)}%`}}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h6 className="mb-0">Quick Actions</h6>
                    </div>
                    <div className="card-body">
                      <div className="d-grid gap-2">
                        <button 
                          className="btn btn-outline-primary"
                          onClick={() => loadTrends('30d', 'users')}
                        >
                          <i className="bi bi-graph-up me-2"></i>
                          Load User Trends
                        </button>
                        <button 
                          className="btn btn-outline-success"
                          onClick={() => loadTrends('30d', 'events')}
                        >
                          <i className="bi bi-calendar-event me-2"></i>
                          Load Event Trends
                        </button>
                        <button 
                          className="btn btn-outline-info"
                          onClick={() => loadAnalytics()}
                        >
                          <i className="bi bi-arrow-clockwise me-2"></i>
                          Refresh Analytics
                        </button>
                        <button 
                          className="btn btn-outline-secondary"
                          onClick={() => window.open(`${getApiUrl()}/super-admin/analytics/export/system_overview`, '_blank')}
                        >
                          <i className="bi bi-download me-2"></i>
                          Export Report
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Organization Performance Rankings */}
              {orgPerformance && (
                <div className="row mb-4">
                  <div className="col-12">
                    <div className="card">
                      <div className="card-header">
                        <h6 className="mb-0">
                          <i className="bi bi-trophy me-2"></i>
                          Organization Performance Rankings
                        </h6>
                      </div>
                      <div className="card-body">
                        <div className="row mb-3">
                          <div className="col-md-3">
                            <div className="text-center">
                              <h6 className="text-success">Excellent Health</h6>
                              <h4>{orgPerformance.summary.excellent_health}</h4>
                            </div>
                          </div>
                          <div className="col-md-3">
                            <div className="text-center">
                              <h6 className="text-info">Good Health</h6>
                              <h4>{orgPerformance.summary.good_health}</h4>
                            </div>
                          </div>
                          <div className="col-md-3">
                            <div className="text-center">
                              <h6 className="text-warning">Needs Attention</h6>
                              <h4>{orgPerformance.summary.needs_attention}</h4>
                            </div>
                          </div>
                          <div className="col-md-3">
                            <div className="text-center">
                              <h6 className="text-muted">Avg Score</h6>
                              <h4>{orgPerformance.summary.avg_engagement_score}</h4>
                            </div>
                          </div>
                        </div>
                        
                        <div className="table-responsive">
                          <table className="table table-sm">
                            <thead>
                              <tr>
                                <th>Rank</th>
                                <th>Organization</th>
                                <th>Engagement Score</th>
                                <th>Users</th>
                                <th>Events (30d)</th>
                                <th>RSVPs (30d)</th>
                                <th>Status</th>
                              </tr>
                            </thead>
                            <tbody>
                              {orgPerformance.organizations.slice(0, 10).map((org, index) => (
                                <tr key={org.id}>
                                  <td>
                                    <span className={`badge ${index < 3 ? 'bg-warning' : 'bg-secondary'}`}>
                                      #{index + 1}
                                    </span>
                                  </td>
                                  <td><strong>{org.name}</strong></td>
                                  <td>
                                    <div className="d-flex align-items-center">
                                      <div className="progress me-2" style={{width: '60px', height: '6px'}}>
                                        <div 
                                          className="progress-bar bg-success" 
                                          style={{width: `${org.metrics.engagement_score}%`}}
                                        ></div>
                                      </div>
                                      <small>{org.metrics.engagement_score}</small>
                                    </div>
                                  </td>
                                  <td>{org.metrics.user_count}</td>
                                  <td>{org.metrics.recent_events_30d}</td>
                                  <td>{org.metrics.recent_rsvps_30d}</td>
                                  <td>
                                    <span className={`badge ${
                                      org.metrics.health_status === 'excellent' ? 'bg-success' :
                                      org.metrics.health_status === 'good' ? 'bg-info' :
                                      org.metrics.health_status === 'fair' ? 'bg-warning' :
                                      'bg-danger'
                                    }`}>
                                      {org.metrics.health_status.replace('_', ' ')}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Trends Data Display */}
              {trendsData && (
                <div className="row mb-4">
                  <div className="col-12">
                    <div className="card">
                      <div className="card-header">
                        <h6 className="mb-0">
                          <i className="bi bi-graph-up me-2"></i>
                          Trends: {trendsData.metric} ({trendsData.period})
                        </h6>
                      </div>
                      <div className="card-body">
                        <div className="mb-3">
                          <small className="text-muted">
                            Data from {new Date(trendsData.start_date).toLocaleDateString()} to {new Date(trendsData.end_date).toLocaleDateString()}
                          </small>
                        </div>
                        {trendsData.trends.length > 0 ? (
                          <div className="table-responsive">
                            <table className="table table-sm">
                              <thead>
                                <tr>
                                  <th>Date</th>
                                  <th>Value</th>
                                </tr>
                              </thead>
                              <tbody>
                                {trendsData.trends.slice(-10).map((trend, index) => (
                                  <tr key={index}>
                                    <td>{new Date(trend.date).toLocaleDateString()}</td>
                                    <td><strong>{trend.value}</strong></td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <div className="text-center text-muted py-3">
                            No trend data available for the selected period.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          
          {!analyticsData && (
            <div className="text-center py-5">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Loading analytics...</span>
              </div>
              <div className="mt-2">Loading advanced analytics...</div>
            </div>
          )}
        </>
      )}

      {/* User Management Tab */}
      {activeTab === 'users' && (
        <div className="row">
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-search me-2"></i>
                  User Search & Management
                </h5>
              </div>
              <div className="card-body">
                <div className="row mb-3">
                  <div className="col-md-8">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search users by username, name, or email..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && searchUsers()}
                    />
                  </div>
                  <div className="col-md-4">
                    <button className="btn btn-primary" onClick={searchUsers}>
                      Search Users
                    </button>
                  </div>
                </div>
                
                {searchResults.length > 0 && (
                  <>
                    {/* Bulk Operations */}
                    <div className="row mb-3">
                      <div className="col-md-4">
                        <select 
                          className="form-select"
                          value={bulkOperation}
                          onChange={(e) => setBulkOperation(e.target.value)}
                        >
                          <option value="">Select Bulk Operation...</option>
                          <option value="disable">Disable Users</option>
                          <option value="enable">Enable Users</option>
                          <option value="reset_passwords">Reset Passwords</option>
                          <option value="delete">Delete Users</option>
                        </select>
                      </div>
                      <div className="col-md-4">
                        <button 
                          className="btn btn-warning"
                          onClick={handleBulkOperation}
                          disabled={!bulkOperation || selectedUsers.length === 0}
                        >
                          Execute on {selectedUsers.length} users
                        </button>
                      </div>
                      <div className="col-md-4">
                        <small className="text-muted">
                          {selectedUsers.length} users selected
                        </small>
                      </div>
                    </div>

                    <div className="table-responsive">
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>
                              <input 
                                type="checkbox" 
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSelectedUsers(searchResults.map(u => u.id));
                                  } else {
                                    setSelectedUsers([]);
                                  }
                                }}
                                checked={selectedUsers.length === searchResults.length && searchResults.length > 0}
                              />
                            </th>
                            <th>Username</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Organizations</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {searchResults.map(user => (
                            <tr key={user.id}>
                              <td>
                                <input 
                                  type="checkbox"
                                  checked={selectedUsers.includes(user.id)}
                                  onChange={() => toggleUserSelection(user.id)}
                                />
                              </td>
                              <td>{user.username}</td>
                              <td>{user.name}</td>
                              <td>{user.email}</td>
                              <td>
                                {user.organizations.map(org => (
                                  <span key={org.id} className="badge bg-secondary me-1">
                                    {org.name} ({org.role})
                                  </span>
                                ))}
                              </td>
                              <td>
                                <div className="btn-group btn-group-sm">
                                  <button 
                                    className="btn btn-outline-primary"
                                    onClick={() => troubleshootUser(user.id)}
                                    title="Troubleshoot"
                                  >
                                    <i className="bi bi-bug"></i>
                                  </button>
                                  <button 
                                    className="btn btn-outline-warning"
                                    onClick={() => resetUserPassword(user.id, user.username)}
                                    title="Reset Password"
                                  >
                                    <i className="bi bi-key"></i>
                                  </button>
                                  <button 
                                    className="btn btn-outline-info"
                                    onClick={() => impersonateUser(user.id, user.username)}
                                    title="Impersonate User"
                                  >
                                    <i className="bi bi-person-badge"></i>
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Health Tab */}
      {activeTab === 'system' && (
        <div className="row">
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-cpu me-2"></i>
                  System Status
                </h5>
              </div>
              <div className="card-body">
                {systemHealth ? (
                  <>
                    <div className="mb-3">
                      <strong>Overall Status:</strong>
                      <span className={`ms-2 badge ${systemHealth.status === 'healthy' ? 'bg-success' : 'bg-warning'}`}>
                        {systemHealth.status}
                      </span>
                    </div>
                    
                    <div className="mb-3">
                      <strong>Database:</strong>
                      <div className="ms-3">
                        <div>Status: <span className="badge bg-success">{systemHealth.database?.status || 'Unknown'}</span></div>
                        {systemHealth.database?.response_time_ms && (
                          <div>Response Time: {systemHealth.database.response_time_ms}ms</div>
                        )}
                      </div>
                    </div>

                    {systemHealth.system && (
                      <div className="mb-3">
                        <strong>System Metrics:</strong>
                        <div className="ms-3">
                          <div>CPU: {systemHealth.system.cpu_percent}%</div>
                          <div>Memory: {systemHealth.system.memory_percent}%</div>
                          <div>Disk: {systemHealth.system.disk_percent}%</div>
                        </div>
                      </div>
                    )}

                    <div className="mb-3">
                      <strong>Recent Activity (24h):</strong>
                      <div className="ms-3">
                        <div>Logins: {systemHealth.activity?.recent_logins_24h || 0}</div>
                        <div>Events Created: {systemHealth.activity?.recent_events_24h || 0}</div>
                      </div>
                    </div>

                    <small className="text-muted">
                      Last updated: {new Date(systemHealth.timestamp).toLocaleString()}
                    </small>
                  </>
                ) : (
                  <div className="text-center py-3">
                    <div className="spinner-border" role="status">
                      <span className="visually-hidden">Loading system health...</span>
                    </div>
                    <div className="mt-2">Loading system health data...</div>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="col-md-6">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-speedometer2 me-2"></i>
                  Quick Actions
                </h5>
              </div>
              <div className="card-body">
                <div className="d-grid gap-2">
                  <button 
                    className="btn btn-outline-primary"
                    onClick={loadSystemHealth}
                  >
                    <i className="bi bi-arrow-clockwise me-2"></i>
                    Refresh System Health
                  </button>
                  
                  <button 
                    className="btn btn-outline-info"
                    onClick={() => window.open('/api/super-admin/system/logs', '_blank')}
                  >
                    <i className="bi bi-file-text me-2"></i>
                    View System Logs
                  </button>
                  
                  <button 
                    className="btn btn-outline-warning"
                    onClick={() => {
                      if (window.confirm('This will log you out. Continue?')) {
                        localStorage.clear();
                        window.location.href = '/login';
                      }
                    }}
                  >
                    <i className="bi bi-box-arrow-right me-2"></i>
                    Emergency Logout
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Tab - Phase 3 Security & Compliance */}
      {activeTab === 'security' && (
        <div className="row">
          <div className="col-12">
            <div className="card mb-4">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-shield-check me-2"></i>
                  Security & Compliance Dashboard
                  <span className="badge bg-success ms-2">Phase 3</span>
                </h5>
              </div>
              <div className="card-body">
                {securityData ? (
                  <div className="row">
                    <div className="col-md-3">
                      <div className="card text-center">
                        <div className="card-body">
                          <h6 className="card-title">Audit Entries</h6>
                          <h4 className="text-primary">{securityData.audit_statistics?.total_entries || 0}</h4>
                          <small className="text-muted">
                            {securityData.audit_statistics?.entries_24h || 0} in 24h
                          </small>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-3">
                      <div className="card text-center">
                        <div className="card-body">
                          <h6 className="card-title">Security Events</h6>
                          <h4 className="text-warning">{securityData.security_statistics?.total_events || 0}</h4>
                          <small className="text-muted">
                            {securityData.security_statistics?.unresolved_events || 0} unresolved
                          </small>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-3">
                      <div className="card text-center">
                        <div className="card-body">
                          <h6 className="card-title">Resolution Rate</h6>
                          <h4 className="text-success">{securityData.security_statistics?.resolution_rate || 0}%</h4>
                          <small className="text-muted">Security events resolved</small>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-3">
                      <div className="card text-center">
                        <div className="card-body">
                          <h6 className="card-title">Growth Rate</h6>
                          <h4 className="text-info">{securityData.audit_statistics?.growth_rate_24h || 0}%</h4>
                          <small className="text-muted">24h activity growth</small>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-3">
                    <div className="spinner-border" role="status">
                      <span className="visually-hidden">Loading security data...</span>
                    </div>
                    <div className="mt-2">Loading security dashboard...</div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h6 className="mb-0">
                  <i className="bi bi-list-ul me-2"></i>
                  Recent Audit Logs
                </h6>
                <button 
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => loadAuditLogs()}
                >
                  <i className="bi bi-arrow-clockwise"></i>
                </button>
              </div>
              <div className="card-body">
                {auditLogs ? (
                  <>
                    <div className="table-responsive" style={{maxHeight: '400px', overflowY: 'auto'}}>
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>User</th>
                            <th>Action</th>
                            <th>Resource</th>
                            <th>Time</th>
                          </tr>
                        </thead>
                        <tbody>
                          {auditLogs.audit_logs?.slice(0, 10).map(log => (
                            <tr key={log.id}>
                              <td>
                                <small>{log.username || 'System'}</small>
                              </td>
                              <td>
                                <span className="badge bg-secondary">{log.action_type}</span>
                              </td>
                              <td>
                                <small>{log.resource_type}</small>
                              </td>
                              <td>
                                <small>{new Date(log.timestamp).toLocaleString()}</small>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="mt-2">
                      <small className="text-muted">
                        Showing {auditLogs.audit_logs?.length || 0} of {auditLogs.summary?.total_entries || 0} entries
                      </small>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-3">
                    <div className="spinner-border spinner-border-sm" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <div className="mt-2">Loading audit logs...</div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h6 className="mb-0">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  Security Events
                </h6>
                <button 
                  className="btn btn-sm btn-outline-primary"
                  onClick={() => loadSecurityEvents()}
                >
                  <i className="bi bi-arrow-clockwise"></i>
                </button>
              </div>
              <div className="card-body">
                {securityEvents ? (
                  <>
                    <div className="table-responsive" style={{maxHeight: '400px', overflowY: 'auto'}}>
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>Event</th>
                            <th>Severity</th>
                            <th>Status</th>
                            <th>Time</th>
                          </tr>
                        </thead>
                        <tbody>
                          {securityEvents.security_events?.slice(0, 10).map(event => (
                            <tr key={event.id}>
                              <td>
                                <small>{event.event_type}</small>
                              </td>
                              <td>
                                <span className={`badge ${
                                  event.severity === 'critical' ? 'bg-danger' :
                                  event.severity === 'high' ? 'bg-warning' :
                                  event.severity === 'medium' ? 'bg-info' : 'bg-secondary'
                                }`}>
                                  {event.severity}
                                </span>
                              </td>
                              <td>
                                <span className={`badge ${event.resolved ? 'bg-success' : 'bg-warning'}`}>
                                  {event.resolved ? 'Resolved' : 'Open'}
                                </span>
                              </td>
                              <td>
                                <small>{new Date(event.timestamp).toLocaleString()}</small>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="mt-2">
                      <small className="text-muted">
                        Showing {securityEvents.security_events?.length || 0} of {securityEvents.summary?.total_events || 0} events
                      </small>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-3">
                    <div className="spinner-border spinner-border-sm" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <div className="mt-2">Loading security events...</div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="col-12 mt-4">
            <div className="card">
              <div className="card-header">
                <h6 className="mb-0">
                  <i className="bi bi-tools me-2"></i>
                  Security Management Tools
                </h6>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-4">
                    <div className="d-grid gap-2">
                      <button 
                        className="btn btn-outline-primary"
                        onClick={() => {
                          loadSecurity();
                          loadAuditLogs();
                          loadSecurityEvents();
                        }}
                      >
                        <i className="bi bi-arrow-clockwise me-2"></i>
                        Refresh Security Data
                      </button>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="d-grid gap-2">
                      <button 
                        className="btn btn-outline-info"
                        onClick={() => window.open('/api/super-admin/security/audit-log?per_page=100', '_blank')}
                      >
                        <i className="bi bi-download me-2"></i>
                        Export Audit Logs
                      </button>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="d-grid gap-2">
                      <button 
                        className="btn btn-outline-success"
                        onClick={() => {
                          fetch(`${getApiUrl()}/super-admin/security/status`, {
                            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                          }).then(r => r.json()).then(data => {
                            alert(`Security Status: ${data.phase3_status}\nFeatures: ${Object.entries(data.security_features).map(([k,v]) => `${k}: ${v}`).join(', ')}`);
                          });
                        }}
                      >
                        <i className="bi bi-info-circle me-2"></i>
                        Security Status
                      </button>
                    </div>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="alert alert-info">
                    <i className="bi bi-info-circle me-2"></i>
                    <strong>Phase 3 Security & Compliance:</strong> Advanced audit trails, security monitoring, and data privacy features are now operational. 
                    This dashboard provides real-time insights into system security and compliance metrics.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Organization Details Modal */}
      {selectedOrg && orgDetails && (
        <div className="modal show d-block" tabIndex="-1" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-building me-2"></i>
                  {orgDetails.organization.name} Details
                </h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => {setSelectedOrg(null); setOrgDetails(null);}}
                ></button>
              </div>
              <div className="modal-body">
                <div className="row">
                  <div className="col-md-6">
                    <h6>Users ({orgDetails.users.length})</h6>
                    <div className="table-responsive" style={{maxHeight: '300px', overflowY: 'auto'}}>
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Email</th>
                          </tr>
                        </thead>
                        <tbody>
                          {orgDetails.users.map(user => (
                            <tr key={user.id}>
                              <td>{user.username}</td>
                              <td>
                                <span className={`badge ${user.role === 'Admin' ? 'bg-warning' : 'bg-secondary'}`}>
                                  {user.role}
                                </span>
                              </td>
                              <td>{user.email}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <h6>Recent Events ({orgDetails.events.length})</h6>
                    <div className="table-responsive" style={{maxHeight: '300px', overflowY: 'auto'}}>
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>Title</th>
                            <th>Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {orgDetails.events.map(event => (
                            <tr key={event.id}>
                              <td>{event.title}</td>
                              <td>{new Date(event.date).toLocaleDateString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => {setSelectedOrg(null); setOrgDetails(null);}}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default SuperAdminPage;
