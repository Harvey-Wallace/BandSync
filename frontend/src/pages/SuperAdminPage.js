import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../utils/apiUrl';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

function SuperAdminPage() {
  const [overview, setOverview] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [orgDetails, setOrgDetails] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [bulkOperation, setBulkOperation] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [orgPerformance, setOrgPerformance] = useState(null);
  const [securityData, setSecurityData] = useState(null);
  const [auditLogs, setAuditLogs] = useState(null);
  const [securityEvents, setSecurityEvents] = useState(null);
  const navigate = useNavigate();

  const isSuperAdmin = localStorage.getItem('super_admin') === 'true';

  useEffect(() => {
    if (!isSuperAdmin) {
      navigate('/dashboard');
      return;
    }
    loadOverview();
    loadSystemHealth();
    loadAnalytics();
  }, [isSuperAdmin, navigate]);

  const loadSystemHealth = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/system/health`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('System health data:', data);
        setSystemHealth(data);
      } else {
        const errorData = await response.text();
        console.error('System health error:', response.status, errorData);
        setError(`Failed to load system health: ${response.status}`);
      }
    } catch (err) {
      console.error('Error loading system health:', err);
      setError(`Error loading system health: ${err.message}`);
    }
  };

  const loadAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Load analytics overview
      const analyticsResponse = await fetch(`${getApiUrl()}/super-admin/analytics/overview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (analyticsResponse.ok) {
        const data = await analyticsResponse.json();
        console.log('Analytics data:', data);
        setAnalyticsData(data);
      } else {
        console.error('Analytics error:', analyticsResponse.status);
      }
      
      // Load organization performance
      const perfResponse = await fetch(`${getApiUrl()}/super-admin/analytics/organizations/performance`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (perfResponse.ok) {
        const perfData = await perfResponse.json();
        console.log('Organization performance data:', perfData);
        setOrgPerformance(perfData);
      } else {
        console.error('Organization performance error:', perfResponse.status);
      }
      
    } catch (err) {
      console.error('Error loading analytics:', err);
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
  const loadSecurity = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Load security summary
      const summaryResponse = await fetch(`${getApiUrl()}/super-admin/security/audit-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (summaryResponse.ok) {
        const data = await summaryResponse.json();
        console.log('Security summary data:', data);
        setSecurityData(data);
      } else {
        console.error('Security summary error:', summaryResponse.status);
      }
      
    } catch (err) {
      console.error('Error loading security data:', err);
    }
  };

  const loadAuditLogs = async (page = 1, filters = {}) => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '10',
        ...filters
      });
      
      const response = await fetch(`${getApiUrl()}/super-admin/security/audit-log?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Audit logs data:', data);
        setAuditLogs(data);
      } else {
        console.error('Audit logs error:', response.status);
      }
    } catch (err) {
      console.error('Error loading audit logs:', err);
    }
  };

  const loadSecurityEvents = async (page = 1, filters = {}) => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '10',
        ...filters
      });
      
      const response = await fetch(`${getApiUrl()}/super-admin/security/security-events?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Security events data:', data);
        setSecurityEvents(data);
      } else {
        console.error('Security events error:', response.status);
      }
    } catch (err) {
      console.error('Error loading security events:', err);
    }
  };

  const loadOverview = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/overview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Overview data:', data);
        setOverview(data);
      } else {
        const errorData = await response.text();
        console.error('Overview error:', response.status, errorData);
        setError(`Failed to load overview: ${response.status}`);
      }
    } catch (err) {
      console.error('Error loading overview:', err);
      setError(`Error loading overview: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadOrgDetails = async (orgId) => {
    try {
      const token = localStorage.getItem('token');
      console.log('Loading org details for ID:', orgId);
      const response = await fetch(`${getApiUrl()}/super-admin/organization/${orgId}/details`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Organization details data:', data);
        setOrgDetails(data);
        setSelectedOrg(orgId);
      } else {
        const errorData = await response.text();
        console.error('Organization details error:', response.status, errorData);
        setError(`Failed to load organization details: ${response.status} - ${errorData}`);
      }
    } catch (err) {
      console.error('Error loading organization details:', err);
      setError(`Error loading organization details: ${err.message}`);
    }
  };

  const searchUsers = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      console.log('Searching users with term:', searchTerm);
      const response = await fetch(`${getApiUrl()}/super-admin/users/search?q=${encodeURIComponent(searchTerm)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('User search results:', data);
        setSearchResults(data.users || []);
      } else {
        const errorData = await response.text();
        console.error('User search error:', response.status, errorData);
        setError(`Failed to search users: ${response.status} - ${errorData}`);
      }
    } catch (err) {
      console.error('Error searching users:', err);
      setError(`Error searching users: ${err.message}`);
    }
  };

  const troubleshootUser = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/troubleshoot/user/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('User troubleshooting data:', data);
        // Could open a modal or navigate to a detailed view
        alert(`User troubleshooting data logged to console for ${data.user.username}`);
      } else {
        setError('Failed to troubleshoot user');
      }
    } catch (err) {
      setError('Error troubleshooting user');
      console.error(err);
    }
  };

  const resetUserPassword = async (userId, username) => {
    if (!window.confirm(`Reset password for ${username}? This will generate a temporary password.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/super-admin/user/${userId}/reset-password`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Password reset for ${username}!\nNew password: ${data.new_password}\n\nUser will need to change this on next login.`);
      } else {
        setError('Failed to reset password');
      }
    } catch (err) {
      setError('Error resetting password');
      console.error(err);
    }
  };

  const impersonateUser = async (userId, username) => {
    if (!window.confirm(`Impersonate user ${username}? This will log you in as them.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      console.log('Attempting to impersonate user:', userId, username);
      const response = await fetch(`${getApiUrl()}/super-admin/user/${userId}/impersonate`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Impersonation successful:', data);
        
        // Store the impersonation token
        localStorage.setItem('token', data.impersonation_token);
        localStorage.setItem('organization', data.organization.name);
        localStorage.setItem('organization_id', data.organization.id);
        localStorage.setItem('role', data.role);
        localStorage.setItem('impersonating', 'true');
        localStorage.setItem('original_admin', 'Harvey258');
        
        alert(`Now impersonating ${username}. You can return to Super Admin mode by logging out and back in.`);
        window.location.href = '/dashboard';
      } else {
        const errorData = await response.text();
        console.error('Impersonation error:', response.status, errorData);
        setError(`Failed to impersonate user: ${response.status} - ${errorData}`);
      }
    } catch (err) {
      console.error('Error impersonating user:', err);
      setError(`Error impersonating user: ${err.message}`);
    }
  };

  const handleBulkOperation = async () => {
    if (!bulkOperation || selectedUsers.length === 0) {
      alert('Please select an operation and at least one user.');
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
        alert(`Bulk operation completed!\n${data.results.join('\n')}`);
        setSelectedUsers([]);
        setBulkOperation('');
        // Refresh search results
        if (searchTerm) {
          searchUsers();
        }
      } else {
        setError('Failed to perform bulk operation');
      }
    } catch (err) {
      setError('Error performing bulk operation');
      console.error(err);
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
      <div className="container mt-4">
        <div className="row">
          <div className="col-12">
            <h2 className="mb-4">
              <i className="bi bi-shield-check me-2"></i>
              Super Admin Dashboard
            </h2>

          {/* Navigation Tabs */}
          <ul className="nav nav-tabs mb-4">
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                <i className="bi bi-graph-up me-1"></i>
                Overview
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'analytics' ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab('analytics');
                  if (!analyticsData) loadAnalytics();
                }}
              >
                <i className="bi bi-bar-chart me-1"></i>
                Analytics
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'users' ? 'active' : ''}`}
                onClick={() => setActiveTab('users')}
              >
                <i className="bi bi-people me-1"></i>
                User Management
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'system' ? 'active' : ''}`}
                onClick={() => setActiveTab('system')}
              >
                <i className="bi bi-cpu me-1"></i>
                System Health
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'security' ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab('security');
                  if (!securityData) loadSecurity();
                  if (!auditLogs) loadAuditLogs();
                  if (!securityEvents) loadSecurityEvents();
                }}
              >
                <i className="bi bi-shield-check me-1"></i>
                Security
              </button>
            </li>
          </ul>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && overview && (
        <>
          {/* Overview Stats */}
          <div className="row mb-4">
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title">Total Organizations</h5>
                  <h3 className="text-primary">{overview.stats.total_organizations}</h3>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title">Total Users</h5>
                  <h3 className="text-success">{overview.stats.total_users}</h3>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title">Total Events</h5>
                  <h3 className="text-info">{overview.stats.total_events}</h3>
                </div>
              </div>
            </div>
            <div className="col-md-3">
              <div className="card text-center">
                <div className="card-body">
                  <h5 className="card-title">System Status</h5>
                  <h3 className={`${systemHealth?.status === 'healthy' ? 'text-success' : 'text-warning'}`}>
                    {systemHealth?.status === 'healthy' ? '✅ Healthy' : '⚠️ Limited'}
                  </h3>
                </div>
              </div>
            </div>
          </div>

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
    </>
  );
}

export default SuperAdminPage;
