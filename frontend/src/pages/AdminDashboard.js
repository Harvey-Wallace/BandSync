import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import Spinner from '../components/Spinner';
import Toast from '../components/Toast';
import UserAvatar from '../components/UserAvatar';
import GroupEmailManager from '../components/GroupEmailManager';
import BulkOperations from '../components/BulkOperations';
import DebugEnv from '../components/DebugEnv';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import { getApiUrl } from '../utils/apiUrl';

function AdminDashboard() {
  const [org, setOrg] = useState({ 
    name: '', 
    logo_url: '', 
    theme_color: '#007bff',
    rehearsal_address: '',
    contact_phone: '',
    contact_email: '',
    website: '',
    facebook_url: '',
    instagram_url: '',
    twitter_url: '',
    tiktok_url: ''
  });
  const [orgEdit, setOrgEdit] = useState({ 
    name: '', 
    theme_color: '',
    rehearsal_address: '',
    contact_phone: '',
    contact_email: '',
    website: '',
    facebook_url: '',
    instagram_url: '',
    twitter_url: '',
    tiktok_url: ''
  });
  const [orgLoading, setOrgLoading] = useState(false);
  const [logoLoading, setLogoLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    name: '',
    phone: '',
    role: 'Member',
    password: '',
    send_invitation: false,
    section_id: null
  });
  const [createUserLoading, setCreateUserLoading] = useState(false);
  const [showAddExistingUser, setShowAddExistingUser] = useState(false);
  const [addExistingUser, setAddExistingUser] = useState({
    username: '',
    email: '',
    role: 'Member',
    send_invitation: false,
    section_id: null
  });
  const [addExistingUserLoading, setAddExistingUserLoading] = useState(false);
  const [showEditUser, setShowEditUser] = useState(false);
  const [editUser, setEditUser] = useState({
    id: null,
    username: '',
    email: '',
    name: '',
    phone: '',
    address: '',
    role: 'Member',
    avatar_url: '',
    section_id: null
  });
  const [editUserLoading, setEditUserLoading] = useState(false);
  const [sections, setSections] = useState([]);
  const [sectionsLoading, setSectionsLoading] = useState(false);
  const [showCreateSection, setShowCreateSection] = useState(false);
  const [newSection, setNewSection] = useState({
    name: '',
    description: ''
  });
  const [createSectionLoading, setCreateSectionLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const [activeTab, setActiveTab] = useState('organization');
  
  // Email management state
  const [emailStats, setEmailStats] = useState({});
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailLogs, setEmailLogs] = useState([]);
  const [emailLogsLoading, setEmailLogsLoading] = useState(false);
  const [scheduledJobs, setScheduledJobs] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  
  // Calendar management state
  const [calendarStats, setCalendarStats] = useState({});
  const [calendarLoading, setCalendarLoading] = useState(false);
  const [calendarInfo, setCalendarInfo] = useState({});

  const API_BASE_URL = getApiUrl();

  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
  };

  const fetchOrg = async () => {
    setOrgLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/organization`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setOrg(data);
        setOrgEdit({ 
          name: data.name || '', 
          theme_color: data.theme_color || '#007bff',
          rehearsal_address: data.rehearsal_address || '',
          contact_phone: data.contact_phone || '',
          contact_email: data.contact_email || '',
          website: data.website || '',
          facebook_url: data.facebook_url || '',
          instagram_url: data.instagram_url || '',
          twitter_url: data.twitter_url || '',
          tiktok_url: data.tiktok_url || ''
        });
      } else {
        const errorData = await response.json();
        console.error('Failed to fetch organization data:', errorData);
        showToast('Failed to fetch organization data', 'danger');
      }
    } catch (error) {
      console.error('Error fetching organization:', error);
      showToast('Error fetching organization data', 'danger');
    }
    setOrgLoading(false);
  };

  const fetchUsers = async () => {
    setUsersLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        showToast('Failed to fetch users', 'danger');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      showToast('Error fetching users', 'danger');
    }
    setUsersLoading(false);
  };

  const fetchSections = async () => {
    setSectionsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/sections`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSections(data);
      } else {
        showToast('Failed to fetch sections', 'danger');
      }
    } catch (error) {
      console.error('Error fetching sections:', error);
      showToast('Error fetching sections', 'danger');
    }
    setSectionsLoading(false);
  };

  const fetchEmailStats = async () => {
    setEmailLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/email-stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEmailStats(data);
      } else {
        showToast('Failed to fetch email statistics', 'danger');
      }
    } catch (error) {
      console.error('Error fetching email stats:', error);
      showToast('Error fetching email statistics', 'danger');
    }
    setEmailLoading(false);
  };

  const fetchEmailLogs = async () => {
    setEmailLogsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/email-logs?per_page=20`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEmailLogs(data.logs || []);
      } else {
        showToast('Failed to fetch email logs', 'danger');
      }
    } catch (error) {
      console.error('Error fetching email logs:', error);
      showToast('Error fetching email logs', 'danger');
    }
    setEmailLogsLoading(false);
  };

  const fetchScheduledJobs = async () => {
    setJobsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/scheduled-jobs`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setScheduledJobs(data.jobs || []);
      } else {
        showToast('Failed to fetch scheduled jobs', 'danger');
      }
    } catch (error) {
      console.error('Error fetching scheduled jobs:', error);
      showToast('Error fetching scheduled jobs', 'danger');
    }
    setJobsLoading(false);
  };

  const fetchCalendarStats = async () => {
    setCalendarLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/calendar-stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCalendarStats(data);
        setCalendarInfo(data.calendar_info || {});
      } else {
        showToast('Failed to fetch calendar statistics', 'danger');
      }
    } catch (error) {
      console.error('Error fetching calendar stats:', error);
      showToast('Error fetching calendar statistics', 'danger');
    }
    setCalendarLoading(false);
  };

  const sendTestEmail = async () => {
    setEmailLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/test-email`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        showToast('Test email sent successfully');
        fetchEmailStats(); // Refresh stats
      } else {
        showToast('Failed to send test email', 'danger');
      }
    } catch (error) {
      console.error('Error sending test email:', error);
      showToast('Error sending test email', 'danger');
    }
    setEmailLoading(false);
  };

  const testCalendarFeed = async () => {
    setCalendarLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/test-calendar-feed`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        showToast('Calendar feed test successful');
        fetchCalendarStats(); // Refresh stats
      } else {
        showToast('Calendar feed test failed', 'danger');
      }
    } catch (error) {
      console.error('Error testing calendar feed:', error);
      showToast('Error testing calendar feed', 'danger');
    }
    setCalendarLoading(false);
  };

  const handleOrgEdit = (field, value) => {
    setOrgEdit(prev => ({ ...prev, [field]: value }));
  };

  const saveOrgSettings = async () => {
    setOrgLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/organization`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(orgEdit)
      });

      if (response.ok) {
        const data = await response.json();
        setOrg(prev => ({ 
          ...prev, 
          name: data.name, 
          theme_color: data.theme_color,
          rehearsal_address: data.rehearsal_address,
          contact_phone: data.contact_phone,
          contact_email: data.contact_email,
          website: data.website,
          facebook_url: data.facebook_url,
          instagram_url: data.instagram_url,
          twitter_url: data.twitter_url,
          tiktok_url: data.tiktok_url
        }));
        showToast('Organization settings updated successfully');
        // Update localStorage organization name if it changed
        if (data.name) {
          localStorage.setItem('organization', data.name);
        }
        
        // Refresh navbar theme immediately
        window.dispatchEvent(new CustomEvent('organizationUpdated', {
          detail: { theme_color: data.theme_color, name: data.name }
        }));
      } else {
        const errorData = await response.json();
        console.error('Failed to update organization settings:', errorData);
        showToast(`Failed to update organization settings: ${errorData.msg || 'Unknown error'}`, 'danger');
      }
    } catch (error) {
      console.error('Error updating organization:', error);
      showToast('Error updating organization settings', 'danger');
    }
    setOrgLoading(false);
  };

  const handleLogoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      showToast('Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed', 'danger');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      showToast('File size too large. Maximum size is 5MB', 'danger');
      return;
    }

    setLogoLoading(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/admin/upload-logo`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setOrg(prev => ({ ...prev, logo_url: data.logo_url }));
        showToast('Logo uploaded successfully');
        
        // Refresh navbar logo immediately
        window.dispatchEvent(new CustomEvent('organizationUpdated', {
          detail: { logo_url: data.logo_url }
        }));
      } else {
        const errorData = await response.json();
        showToast(errorData.error || 'Failed to upload logo', 'danger');
      }
    } catch (error) {
      console.error('Error uploading logo:', error);
      showToast('Error uploading logo', 'danger');
    }
    setLogoLoading(false);
    // Reset file input
    event.target.value = '';
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role: newRole })
      });

      if (response.ok) {
        setUsers(prev => prev.map(user => 
          user.id === userId ? { ...user, role: newRole } : user
        ));
        showToast('User role updated successfully');
      } else {
        showToast('Failed to update user role', 'danger');
      }
    } catch (error) {
      console.error('Error updating user role:', error);
      showToast('Error updating user role', 'danger');
    }
  };

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setUsers(prev => prev.filter(user => user.id !== userId));
        showToast('User deleted successfully');
      } else {
        const errorData = await response.json();
        showToast(errorData.error || 'Failed to delete user', 'danger');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      showToast('Error deleting user', 'danger');
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setCreateUserLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/users`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newUser)
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(prev => [...prev, data.user]);
        setShowCreateUser(false);
        setNewUser({
          username: '',
          email: '',
          name: '',
          phone: '',
          role: 'Member',
          password: '',
          send_invitation: false,
          section_id: null
        });
        
        let message = 'User created successfully';
        if (data.temporary_password) {
          message += `. Temporary password: ${data.temporary_password}`;
        }
        if (newUser.send_invitation) {
          message += '. Invitation email sent.';
        }
        
        showToast(message);
        fetchUsers(); // Refresh the list
      } else {
        const errorData = await response.json();
        showToast(errorData.error || 'Failed to create user', 'danger');
      }
    } catch (error) {
      console.error('Error creating user:', error);
      showToast('Error creating user', 'danger');
    }
    
    setCreateUserLoading(false);
  };

  const handleAddExistingUser = async (e) => {
    e.preventDefault();
    setAddExistingUserLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/users/add-existing`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(addExistingUser)
      });

      if (response.ok) {
        const data = await response.json();
        setShowAddExistingUser(false);
        setAddExistingUser({
          username: '',
          email: '',
          role: 'Member',
          send_invitation: false,
          section_id: null
        });
        
        let message = 'User added to organization successfully';
        if (addExistingUser.send_invitation) {
          message += '. Invitation email sent.';
        }
        
        showToast(message);
        fetchUsers(); // Refresh the list
      } else {
        const errorData = await response.json();
        showToast(errorData.error || 'Failed to add user', 'danger');
      }
    } catch (error) {
      console.error('Error adding existing user:', error);
      showToast('Error adding existing user', 'danger');
    }
    
    setAddExistingUserLoading(false);
  };

  const sendInvitation = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/invite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        showToast('Invitation sent successfully');
      } else {
        showToast('Failed to send invitation', 'danger');
      }
    } catch (error) {
      console.error('Error sending invitation:', error);
      showToast('Error sending invitation', 'danger');
    }
  };

  const handleEditUser = (user) => {
    setEditUser({
      id: user.id,
      username: user.username,
      email: user.email,
      name: user.name,
      phone: user.phone || '',
      address: user.address || '',
      role: user.role,
      avatar_url: user.avatar_url || '',
      section_id: user.section_id
    });
    setShowEditUser(true);
  };

  const saveEditUser = async (e) => {
    e.preventDefault();
    setEditUserLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/users/${editUser.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: editUser.username,
          email: editUser.email,
          name: editUser.name,
          phone: editUser.phone,
          address: editUser.address,
          role: editUser.role,
          section_id: editUser.section_id
        })
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(prev => prev.map(user => 
          user.id === editUser.id ? { ...user, ...data } : user
        ));
        setShowEditUser(false);
        showToast('User updated successfully');
        fetchUsers(); // Refresh the list
      } else {
        const errorData = await response.json();
        showToast(errorData.error || 'Failed to update user', 'danger');
      }
    } catch (error) {
      console.error('Error updating user:', error);
      showToast('Error updating user', 'danger');
    }
    
    setEditUserLoading(false);
  };

  const handleCreateSection = async (e) => {
    e.preventDefault();
    setCreateSectionLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/sections`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newSection)
      });

      if (response.ok) {
        const data = await response.json();
        setSections(prev => [...prev, data]);
        setShowCreateSection(false);
        setNewSection({
          name: '',
          description: ''
        });
        showToast('Section created successfully');
        fetchSections(); // Refresh the list
      } else {
        const errorData = await response.json();
        showToast(errorData.error || 'Failed to create section', 'danger');
      }
    } catch (error) {
      console.error('Error creating section:', error);
      showToast('Error creating section', 'danger');
    }
    
    setCreateSectionLoading(false);
  };

  const deleteSection = async (sectionId) => {
    if (!window.confirm('Are you sure you want to delete this section?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/admin/sections/${sectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setSections(prev => prev.filter(section => section.id !== sectionId));
        showToast('Section deleted successfully');
      } else {
        showToast('Failed to delete section', 'danger');
      }
    } catch (error) {
      console.error('Error deleting section:', error);
      showToast('Error deleting section', 'danger');
    }
  };

  useEffect(() => {
    fetchOrg();
    fetchUsers();
    fetchSections();
    fetchEmailStats();
    fetchEmailLogs();
    fetchScheduledJobs();
    fetchCalendarStats();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    // Refresh data when tab changes
    if (activeTab === 'email') {
      fetchEmailStats();
      fetchEmailLogs();
      fetchScheduledJobs();
    } else if (activeTab === 'calendar') {
      fetchCalendarStats();
    }
  }, [activeTab]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div>
      <Navbar />
      <div className="container-fluid mt-4">
        <div className="row">
          <div className="col-12">
            <h2>Admin Dashboard</h2>
          </div>
        </div>

        {/* Tab Navigation */}
        <ul className="nav nav-tabs mb-4">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'organization' ? 'active' : ''}`}
              onClick={() => setActiveTab('organization')}
            >
              Organization
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              Users
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'sections' ? 'active' : ''}`}
              onClick={() => setActiveTab('sections')}
            >
              Sections
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
            >
              Analytics
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'groupemail' ? 'active' : ''}`}
              onClick={() => setActiveTab('groupemail')}
            >
              Group Email
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'email' ? 'active' : ''}`}
              onClick={() => setActiveTab('email')}
            >
              Email Management
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'calendar' ? 'active' : ''}`}
              onClick={() => setActiveTab('calendar')}
            >
              Calendar Management
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'bulkops' ? 'active' : ''}`}
              onClick={() => setActiveTab('bulkops')}
            >
              Bulk Operations
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'debug' ? 'active' : ''}`}
              onClick={() => setActiveTab('debug')}
            >
              Debug
            </button>
          </li>
        </ul>

        {/* Organization Tab */}
        {activeTab === 'organization' && (
          <div className="row">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5>Basic Information</h5>
                </div>
                <div className="card-body">
                  <form onSubmit={(e) => { e.preventDefault(); saveOrgSettings(); }}>
                    <div className="mb-3">
                      <label className="form-label">Organization Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={orgEdit.name}
                        onChange={(e) => handleOrgEdit('name', e.target.value)}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Theme Color</label>
                      <input
                        type="color"
                        className="form-control form-control-color"
                        value={orgEdit.theme_color}
                        onChange={(e) => handleOrgEdit('theme_color', e.target.value)}
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Rehearsal Address</label>
                      <textarea
                        className="form-control"
                        rows="3"
                        value={orgEdit.rehearsal_address}
                        onChange={(e) => handleOrgEdit('rehearsal_address', e.target.value)}
                        placeholder="Enter your rehearsal venue address"
                      />
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={orgLoading}>
                      {orgLoading ? <Spinner size={20} /> : 'Save Changes'}
                    </button>
                  </form>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5>Organization Logo</h5>
                </div>
                <div className="card-body">
                  {org.logo_url && (
                    <div className="mb-3">
                      <img
                        src={org.logo_url}
                        alt="Organization Logo"
                        className="img-fluid"
                        style={{ maxHeight: '200px' }}
                      />
                    </div>
                  )}
                  <div className="mb-3">
                    <label className="form-label">Upload New Logo</label>
                    <input
                      type="file"
                      className="form-control"
                      accept="image/*"
                      onChange={handleLogoUpload}
                      disabled={logoLoading}
                    />
                    <div className="form-text">
                      Supported formats: PNG, JPG, JPEG, GIF, WebP. Max size: 5MB
                    </div>
                  </div>
                  {logoLoading && (
                    <div className="text-center">
                      <Spinner size={30} />
                      <div className="mt-2">Uploading...</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Contact Information Row */}
        {activeTab === 'organization' && (
          <div className="row mt-4">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5>Contact Information</h5>
                </div>
                <div className="card-body">
                  <form onSubmit={(e) => { e.preventDefault(); saveOrgSettings(); }}>
                    <div className="mb-3">
                      <label className="form-label">Contact Phone</label>
                      <input
                        type="tel"
                        className="form-control"
                        value={orgEdit.contact_phone}
                        onChange={(e) => handleOrgEdit('contact_phone', e.target.value)}
                        placeholder="e.g., +1 (555) 123-4567"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Contact Email</label>
                      <input
                        type="email"
                        className="form-control"
                        value={orgEdit.contact_email}
                        onChange={(e) => handleOrgEdit('contact_email', e.target.value)}
                        placeholder="e.g., info@yourband.com"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Website</label>
                      <input
                        type="url"
                        className="form-control"
                        value={orgEdit.website}
                        onChange={(e) => handleOrgEdit('website', e.target.value)}
                        placeholder="e.g., https://www.yourband.com"
                      />
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={orgLoading}>
                      {orgLoading ? <Spinner size={20} /> : 'Save Changes'}
                    </button>
                  </form>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5>Social Media Links</h5>
                </div>
                <div className="card-body">
                  <form onSubmit={(e) => { e.preventDefault(); saveOrgSettings(); }}>
                    <div className="mb-3">
                      <label className="form-label">
                        <i className="bi bi-facebook text-primary me-2"></i>Facebook URL
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        value={orgEdit.facebook_url}
                        onChange={(e) => handleOrgEdit('facebook_url', e.target.value)}
                        placeholder="https://facebook.com/yourband"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">
                        <i className="bi bi-instagram text-danger me-2"></i>Instagram URL
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        value={orgEdit.instagram_url}
                        onChange={(e) => handleOrgEdit('instagram_url', e.target.value)}
                        placeholder="https://instagram.com/yourband"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">
                        <i className="bi bi-twitter text-info me-2"></i>Twitter/X URL
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        value={orgEdit.twitter_url}
                        onChange={(e) => handleOrgEdit('twitter_url', e.target.value)}
                        placeholder="https://twitter.com/yourband"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">
                        <i className="bi bi-tiktok text-dark me-2"></i>TikTok URL
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        value={orgEdit.tiktok_url}
                        onChange={(e) => handleOrgEdit('tiktok_url', e.target.value)}
                        placeholder="https://tiktok.com/@yourband"
                      />
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={orgLoading}>
                      {orgLoading ? <Spinner size={20} /> : 'Save Changes'}
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="row">
            <div className="col-12">
              <div className="card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h5>Users</h5>
                  <div>
                    <button
                      className="btn btn-primary btn-sm me-2"
                      onClick={() => setShowAddExistingUser(true)}
                    >
                      <i className="bi bi-person-plus me-2"></i>Add Existing User
                    </button>
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() => setShowCreateUser(true)}
                    >
                      <i className="bi bi-plus-lg me-2"></i>Create User
                    </button>
                  </div>
                </div>
                <div className="card-body">
                  {usersLoading ? (
                    <div className="text-center">
                      <Spinner size={50} />
                    </div>
                  ) : (
                    <div className="table-responsive">
                      <table className="table table-striped">
                        <thead>
                          <tr>
                            <th>Avatar</th>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Role</th>
                            <th>Section</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {users.map(user => (
                            <tr key={user.id}>
                              <td>
                                <UserAvatar user={user} size={40} />
                              </td>
                              <td>{user.name}</td>
                              <td>{user.username}</td>
                              <td>{user.email}</td>
                              <td>
                                <select
                                  className="form-select form-select-sm"
                                  value={user.role}
                                  onChange={(e) => updateUserRole(user.id, e.target.value)}
                                >
                                  <option value="Member">Member</option>
                                  <option value="Admin">Admin</option>
                                </select>
                              </td>
                              <td>
                                {sections.find(s => s.id === user.section_id)?.name || 'None'}
                              </td>
                              <td>
                                <button
                                  className="btn btn-sm btn-outline-primary me-2"
                                  onClick={() => handleEditUser(user)}
                                >
                                  <i className="bi bi-pencil-square"></i>
                                </button>
                                <button
                                  className="btn btn-sm btn-outline-success me-2"
                                  onClick={() => sendInvitation(user.id)}
                                >
                                  <i className="bi bi-envelope"></i>
                                </button>
                                <button
                                  className="btn btn-sm btn-outline-danger"
                                  onClick={() => deleteUser(user.id)}
                                >
                                  <i className="bi bi-trash"></i>
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Sections Tab */}
        {activeTab === 'sections' && (
          <div className="row">
            <div className="col-12">
              <div className="card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h5>Sections</h5>
                  <button
                    className="btn btn-success btn-sm"
                    onClick={() => setShowCreateSection(true)}
                  >
                    <i className="bi bi-plus-lg me-2"></i>Create Section
                  </button>
                </div>
                <div className="card-body">
                  {sectionsLoading ? (
                    <div className="text-center">
                      <Spinner size={50} />
                    </div>
                  ) : (
                    <div className="table-responsive">
                      <table className="table table-striped">
                        <thead>
                          <tr>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Members</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sections.map(section => (
                            <tr key={section.id}>
                              <td>{section.name}</td>
                              <td>{section.description}</td>
                              <td>
                                {users.filter(u => u.section_id === section.id).length}
                              </td>
                              <td>
                                <button
                                  className="btn btn-sm btn-outline-danger"
                                  onClick={() => deleteSection(section.id)}
                                >
                                  <i className="bi bi-trash"></i>
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Email Management Tab */}
        {activeTab === 'email' && (
          <div className="row">
            <div className="col-12">
              <div className="card">
                <div className="card-header">
                  <h5>Email Management</h5>
                </div>
                <div className="card-body">
                  {/* Email Stats */}
                  <div className="mb-4">
                    <h6>Email Statistics</h6>
                    {emailLoading ? (
                      <div className="text-center">
                        <Spinner size={20} />
                      </div>
                    ) : (
                      <div className="row">
                        <div className="col-md-4">
                          <div className="card text-white bg-success mb-3">
                            <div className="card-header">Total Sent</div>
                            <div className="card-body">
                              <h5 className="card-title">{emailStats.total_sent || 0}</h5>
                            </div>
                          </div>
                        </div>
                        <div className="col-md-4">
                          <div className="card text-white bg-danger mb-3">
                            <div className="card-header">Total Failed</div>
                            <div className="card-body">
                              <h5 className="card-title">{emailStats.total_failed || 0}</h5>
                            </div>
                          </div>
                        </div>
                        <div className="col-md-4">
                          <div className="card text-white bg-info mb-3">
                            <div className="card-header">Total Pending</div>
                            <div className="card-body">
                              <h5 className="card-title">{emailStats.total_pending || 0}</h5>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Email Logs */}
                  <div className="mb-4">
                    <h6>Recent Email Logs</h6>
                    {emailLogsLoading ? (
                      <div className="text-center">
                        <Spinner size={20} />
                      </div>
                    ) : emailLogs.length === 0 ? (
                      <p>No email logs found.</p>
                    ) : (
                      <div className="table-responsive">
                        <table className="table table-striped">
                          <thead>
                            <tr>
                              <th>Date</th>
                              <th>To</th>
                              <th>Subject</th>
                              <th>Status</th>
                              <th>Error</th>
                            </tr>
                          </thead>
                          <tbody>
                            {emailLogs.map(log => (
                              <tr key={log.id}>
                                <td>{new Date(log.created_at).toLocaleString()}</td>
                                <td>{log.recipient}</td>
                                <td>{log.subject}</td>
                                <td>
                                  <span className={`badge ${log.status === 'sent' ? 'bg-success' : 'bg-danger'}`}>
                                    {log.status}
                                  </span>
                                </td>
                                <td>{log.error_message || '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Scheduled Jobs */}
                  <div className="mb-4">
                    <h6>Scheduled Email Jobs</h6>
                    {jobsLoading ? (
                      <div className="text-center">
                        <Spinner size={20} />
                      </div>
                    ) : scheduledJobs.length === 0 ? (
                      <p>No scheduled jobs found.</p>
                    ) : (
                      <div className="table-responsive">
                        <table className="table table-striped">
                          <thead>
                            <tr>
                              <th>Job Type</th>
                              <th>Status</th>
                              <th>Next Run</th>
                              <th>Last Run</th>
                            </tr>
                          </thead>
                          <tbody>
                            {scheduledJobs.map((job, index) => (
                              <tr key={index}>
                                <td>{job.type}</td>
                                <td>
                                  <span className={`badge ${job.status === 'active' ? 'bg-success' : 'bg-warning'}`}>
                                    {job.status}
                                  </span>
                                </td>
                                <td>{job.next_run ? new Date(job.next_run).toLocaleString() : '-'}</td>
                                <td>{job.last_run ? new Date(job.last_run).toLocaleString() : '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Send Test Email */}
                  <div className="mb-4">
                    <h6>Send Test Email</h6>
                    <button
                      className="btn btn-primary"
                      onClick={sendTestEmail}
                      disabled={emailLoading}
                    >
                      {emailLoading ? <Spinner size={20} /> : 'Send Test Email'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Calendar Management Tab */}
        {activeTab === 'calendar' && (
          <div className="row">
            <div className="col-12">
              <div className="card">
                <div className="card-header">
                  <h5>Calendar Management</h5>
                </div>
                <div className="card-body">
                  {/* Calendar Stats */}
                  <div className="mb-4">
                    <h6>Calendar Statistics</h6>
                    {calendarLoading ? (
                      <div className="text-center">
                        <Spinner size={20} />
                      </div>
                    ) : (
                      <div className="row">
                        <div className="col-md-4">
                          <div className="card text-white bg-success mb-3">
                            <div className="card-header">Total Events</div>
                            <div className="card-body">
                              <h5 className="card-title">{calendarStats.total_events || 0}</h5>
                            </div>
                          </div>
                        </div>
                        <div className="col-md-4">
                          <div className="card text-white bg-warning mb-3">
                            <div className="card-header">Past Events</div>
                            <div className="card-body">
                              <h5 className="card-title">{calendarStats.past_events || 0}</h5>
                            </div>
                          </div>
                        </div>
                        <div className="col-md-4">
                          <div className="card text-white bg-info mb-3">
                            <div className="card-header">Upcoming Events</div>
                            <div className="card-body">
                              <h5 className="card-title">{calendarStats.upcoming_events || 0}</h5>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Calendar Feed URLs */}
                  <div className="mb-4">
                    <h6>Calendar Feed URLs</h6>
                    <div className="row">
                      <div className="col-md-6">
                        <div className="card">
                          <div className="card-header">
                            <h6>Organization Feed</h6>
                          </div>
                          <div className="card-body">
                            <div className="input-group mb-2">
                              <input
                                type="text"
                                className="form-control"
                                value={calendarInfo.organization_feed || ''}
                                readOnly
                              />
                              <button
                                className="btn btn-outline-secondary"
                                onClick={() => navigator.clipboard.writeText(calendarInfo.organization_feed || '')}
                              >
                                <i className="bi bi-clipboard"></i>
                              </button>
                            </div>
                            <small className="text-muted">All organization events</small>
                          </div>
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="card">
                          <div className="card-header">
                            <h6>Public Feed</h6>
                          </div>
                          <div className="card-body">
                            <div className="input-group mb-2">
                              <input
                                type="text"
                                className="form-control"
                                value={calendarInfo.public_feed || ''}
                                readOnly
                              />
                              <button
                                className="btn btn-outline-secondary"
                                onClick={() => navigator.clipboard.writeText(calendarInfo.public_feed || '')}
                              >
                                <i className="bi bi-clipboard"></i>
                              </button>
                            </div>
                            <small className="text-muted">Public events only</small>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Calendar Integration Info */}
                  <div className="mb-4">
                    <h6>Calendar Integration</h6>
                    <div className="alert alert-info">
                      <h6>How to use calendar feeds:</h6>
                      <ul className="mb-0">
                        <li><strong>Google Calendar:</strong> Add by URL in "Other calendars" section</li>
                        <li><strong>Apple Calendar:</strong> File → New Calendar Subscription</li>
                        <li><strong>Outlook:</strong> Add calendar → Subscribe from web</li>
                        <li><strong>Thunderbird:</strong> Right-click calendar list → New Calendar → On the Network</li>
                      </ul>
                    </div>
                  </div>

                  {/* Test Calendar Feed */}
                  <div className="mb-4">
                    <h6>Test Calendar Feed</h6>
                    <button
                      className="btn btn-primary"
                      onClick={testCalendarFeed}
                      disabled={calendarLoading}
                    >
                      {calendarLoading ? <Spinner size={20} /> : 'Test Calendar Feed'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Group Email Tab */}
        {activeTab === 'groupemail' && (
          <div className="row">
            <div className="col-12">
              <GroupEmailManager showToast={showToast} />
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="row">
            <div className="col-12">
              <AnalyticsDashboard showToast={showToast} />
            </div>
          </div>
        )}

        {/* Bulk Operations Tab */}
        {activeTab === 'bulkops' && (
          <div className="row">
            <div className="col-12">
              <BulkOperations showToast={showToast} />
            </div>
          </div>
        )}

        {/* Debug Tab */}
        {activeTab === 'debug' && (
          <div className="row">
            <div className="col-12">
              <DebugEnv />
            </div>
          </div>
        )}

        {/* Add Existing User Modal */}
        {showAddExistingUser && (
          <div className="modal show d-block">
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Add Existing User to Organization</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowAddExistingUser(false)}
                  ></button>
                </div>
                <form onSubmit={handleAddExistingUser}>
                  <div className="modal-body">
                    <div className="alert alert-info">
                      <i className="bi bi-info-circle me-2"></i>
                      Add an existing BandSync user to this organization. You can search by username or email.
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Username</label>
                      <input
                        type="text"
                        className="form-control"
                        value={addExistingUser.username}
                        onChange={(e) => setAddExistingUser({ ...addExistingUser, username: e.target.value, email: '' })}
                        placeholder="Enter username"
                      />
                    </div>
                    <div className="mb-3">
                      <div className="text-center">
                        <span className="text-muted">--- OR ---</span>
                      </div>
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        value={addExistingUser.email}
                        onChange={(e) => setAddExistingUser({ ...addExistingUser, email: e.target.value, username: '' })}
                        placeholder="Enter email address"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Role</label>
                      <select
                        className="form-select"
                        value={addExistingUser.role}
                        onChange={(e) => setAddExistingUser({ ...addExistingUser, role: e.target.value })}
                      >
                        <option value="Member">Member</option>
                        <option value="Admin">Admin</option>
                      </select>
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Section</label>
                      <select
                        className="form-select"
                        value={addExistingUser.section_id || ''}
                        onChange={(e) => setAddExistingUser({ ...addExistingUser, section_id: e.target.value || null })}
                      >
                        <option value="">No section</option>
                        {sections.map(section => (
                          <option key={section.id} value={section.id}>
                            {section.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="mb-3">
                      <div className="form-check">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          id="sendInvitationExisting"
                          checked={addExistingUser.send_invitation}
                          onChange={(e) => setAddExistingUser({ ...addExistingUser, send_invitation: e.target.checked })}
                        />
                        <label className="form-check-label" htmlFor="sendInvitationExisting">
                          Send invitation email with new temporary password
                        </label>
                      </div>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setShowAddExistingUser(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={addExistingUserLoading || (!addExistingUser.username && !addExistingUser.email)}
                    >
                      {addExistingUserLoading ? <Spinner size={20} /> : 'Add User'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Create User Modal */}
        {showCreateUser && (
          <div className="modal show d-block">
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Create New User</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowCreateUser(false)}
                  ></button>
                </div>
                <form onSubmit={handleCreateUser}>
                  <div className="modal-body">
                    <div className="mb-3">
                      <label className="form-label">Username</label>
                      <input
                        type="text"
                        className="form-control"
                        value={newUser.username}
                        onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        value={newUser.email}
                        onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Full Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={newUser.name}
                        onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Phone</label>
                      <input
                        type="text"
                        className="form-control"
                        value={newUser.phone}
                        onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Role</label>
                      <select
                        className="form-select"
                        value={newUser.role}
                        onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                      >
                        <option value="Member">Member</option>
                        <option value="Admin">Admin</option>
                      </select>
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Section</label>
                      <select
                        className="form-select"
                        value={newUser.section_id || ''}
                        onChange={(e) => setNewUser({ ...newUser, section_id: e.target.value ? parseInt(e.target.value) : null })}
                      >
                        <option value="">No Section</option>
                        {sections.map(section => (
                          <option key={section.id} value={section.id}>{section.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Password</label>
                      <input
                        type="password"
                        className="form-control"
                        value={newUser.password}
                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                        placeholder="Leave blank for auto-generated password"
                      />
                    </div>
                    <div className="mb-3 form-check">
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="sendInvitation"
                        checked={newUser.send_invitation}
                        onChange={(e) => setNewUser({ ...newUser, send_invitation: e.target.checked })}
                      />
                      <label className="form-check-label" htmlFor="sendInvitation">
                        Send invitation email
                      </label>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setShowCreateUser(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={createUserLoading}
                    >
                      {createUserLoading ? <Spinner size={20} /> : 'Create User'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Edit User Modal */}
        {showEditUser && (
          <div className="modal show d-block">
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Edit User</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowEditUser(false)}
                  ></button>
                </div>
                <form onSubmit={saveEditUser}>
                  <div className="modal-body">
                    <div className="mb-3">
                      <label className="form-label">Username</label>
                      <input
                        type="text"
                        className="form-control"
                        value={editUser.username}
                        onChange={(e) => setEditUser({ ...editUser, username: e.target.value })}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        value={editUser.email}
                        onChange={(e) => setEditUser({ ...editUser, email: e.target.value })}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Full Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={editUser.name}
                        onChange={(e) => setEditUser({ ...editUser, name: e.target.value })}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Phone</label>
                      <input
                        type="text"
                        className="form-control"
                        value={editUser.phone}
                        onChange={(e) => setEditUser({ ...editUser, phone: e.target.value })}
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Address</label>
                      <input
                        type="text"
                        className="form-control"
                        value={editUser.address}
                        onChange={(e) => setEditUser({ ...editUser, address: e.target.value })}
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Role</label>
                      <select
                        className="form-select"
                        value={editUser.role}
                        onChange={(e) => setEditUser({ ...editUser, role: e.target.value })}
                      >
                        <option value="Member">Member</option>
                        <option value="Admin">Admin</option>
                      </select>
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Section</label>
                      <select
                        className="form-select"
                        value={editUser.section_id || ''}
                        onChange={(e) => setEditUser({ ...editUser, section_id: e.target.value ? parseInt(e.target.value) : null })}
                      >
                        <option value="">No Section</option>
                        {sections.map(section => (
                          <option key={section.id} value={section.id}>{section.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setShowEditUser(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={editUserLoading}
                    >
                      {editUserLoading ? <Spinner size={20} /> : 'Save Changes'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Create Section Modal */}
        {showCreateSection && (
          <div className="modal show d-block">
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Create New Section</h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowCreateSection(false)}
                  ></button>
                </div>
                <form onSubmit={handleCreateSection}>
                  <div className="modal-body">
                    <div className="mb-3">
                      <label className="form-label">Section Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={newSection.name}
                        onChange={(e) => setNewSection({ ...newSection, name: e.target.value })}
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Description</label>
                      <textarea
                        className="form-control"
                        rows="3"
                        value={newSection.description}
                        onChange={(e) => setNewSection({ ...newSection, description: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setShowCreateSection(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={createSectionLoading}
                    >
                      {createSectionLoading ? <Spinner size={20} /> : 'Create Section'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        <Toast 
          show={toast.show}
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ ...toast, show: false })}
        />
      </div>
    </div>
  );
}

export default AdminDashboard;
