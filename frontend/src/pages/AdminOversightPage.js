import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

const AdminOversightPage = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [organizations, setOrganizations] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('dashboard');
    
    // Modal states
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingOrg, setEditingOrg] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deletingOrg, setDeletingOrg] = useState(null);
    const [showDeleteUserModal, setShowDeleteUserModal] = useState(false);
    const [deletingUser, setDeletingUser] = useState(null);
    
    // Debug states
    const [debugUser, setDebugUser] = useState('');
    const [debugResult, setDebugResult] = useState(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const getAuthHeaders = () => {
        const token = localStorage.getItem('token');
        console.log('Auth token:', token ? `${token.substring(0, 20)}...` : 'null');
        return {
            headers: { Authorization: `Bearer ${token}` }
        };
    };

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            setError(''); // Clear previous errors
            
            console.log('Loading dashboard data...');
            console.log('API URL:', getApiUrl());
            console.log('Token exists:', !!localStorage.getItem('token'));
            
            const response = await axios.get(`${getApiUrl()}/admin-oversight/dashboard`, getAuthHeaders());
            console.log('Dashboard response:', response.data);
            setDashboardData(response.data);
        } catch (err) {
            console.error('Dashboard load error:', err);
            console.error('Error response:', err.response?.data);
            console.error('Error status:', err.response?.status);
            
            let errorMsg = 'Failed to load dashboard';
            if (err.response?.data?.error) {
                errorMsg = err.response.data.error;
            } else if (err.response?.status === 403) {
                errorMsg = 'Access denied - Harvey258 only';
            } else if (err.response?.status === 401) {
                errorMsg = 'Authentication required - please login';
            } else if (err.message) {
                errorMsg = `Connection error: ${err.message}`;
            }
            
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const loadOrganizations = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${getApiUrl()}/admin-oversight/organizations`, getAuthHeaders());
            setOrganizations(response.data.organizations);
        } catch (err) {
            console.error('Organizations load error:', err);
            setError(err.response?.data?.error || 'Failed to load organizations');
        } finally {
            setLoading(false);
        }
    };

    const loadUsers = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${getApiUrl()}/admin-oversight/users`, getAuthHeaders());
            setUsers(response.data.users);
        } catch (err) {
            console.error('Users load error:', err);
            setError(err.response?.data?.error || 'Failed to load users');
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        if (tab === 'organizations' && organizations.length === 0) {
            loadOrganizations();
        } else if (tab === 'users' && users.length === 0) {
            loadUsers();
        }
    };

    const handleEditOrg = (org) => {
        setEditingOrg({ ...org });
        setShowEditModal(true);
    };

    const handleSaveOrg = async () => {
        try {
            await axios.put(
                `${getApiUrl()}/admin-oversight/organizations/${editingOrg.id}`,
                {
                    name: editingOrg.name,
                    description: editingOrg.description
                },
                getAuthHeaders()
            );
            setShowEditModal(false);
            setEditingOrg(null);
            loadOrganizations(); // Reload data
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to update organization');
        }
    };

    const handleDeleteOrg = async () => {
        try {
            await axios.delete(
                `${getApiUrl()}/admin-oversight/organizations/${deletingOrg.id}`,
                getAuthHeaders()
            );
            setShowDeleteModal(false);
            setDeletingOrg(null);
            loadOrganizations(); // Reload data
            loadDashboardData(); // Update stats
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to delete organization');
        }
    };

    const handleDeleteUser = async () => {
        try {
            const response = await axios.delete(
                `${getApiUrl()}/admin-oversight/delete-user`,
                {
                    ...getAuthHeaders(),
                    data: { username: deletingUser.username }
                }
            );
            alert(`✅ ${response.data.message}\n\nDeletion Details:\n` +
                `- RSVPs deleted: ${response.data.deletion_details.rsvps_deleted}\n` +
                `- Survey responses deleted: ${response.data.deletion_details.survey_responses_deleted}\n` +
                `- Events transferred: ${response.data.deletion_details.events_transferred}\n` +
                `- Organization memberships removed: ${response.data.deletion_details.user_organizations_deleted}`
            );
            setShowDeleteUserModal(false);
            setDeletingUser(null);
            loadUsers(); // Reload data
            loadDashboardData(); // Update stats
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to delete user');
        }
    };

    const debugUserOrganizations = async () => {
        if (!debugUser.trim()) return;
        
        try {
            const response = await axios.get(`${getApiUrl()}/admin-oversight/debug/user/${debugUser}`, getAuthHeaders());
            setDebugResult(response.data);
        } catch (err) {
            console.error('Debug error:', err);
            setError(err.response?.data?.error || 'Debug failed');
        }
    };

    const fixUserOrganization = async (username, orgName) => {
        try {
            const response = await axios.post(
                `${getApiUrl()}/admin-oversight/fix/add-user-to-org`,
                {
                    username: username,
                    organization_name: orgName,
                    role: 'Member'
                },
                getAuthHeaders()
            );
            alert(response.data.message);
            // Refresh debug data
            debugUserOrganizations();
        } catch (err) {
            console.error('Fix error:', err);
            setError(err.response?.data?.error || 'Fix failed');
        }
    };

    const updateUserRole = async (username, orgName, newRole) => {
        try {
            const response = await axios.post(
                `${getApiUrl()}/admin-oversight/fix/update-user-role`,
                {
                    username: username,
                    organization_name: orgName,
                    role: newRole
                },
                getAuthHeaders()
            );
            alert(response.data.message);
            // Refresh debug data
            debugUserOrganizations();
        } catch (err) {
            console.error('Role update error:', err);
            setError(err.response?.data?.error || 'Role update failed');
        }
    };

    const debugTokenInfo = async () => {
        try {
            const response = await axios.get(
                `${getApiUrl()}/admin-oversight/debug/token-info`,
                getAuthHeaders()
            );
            alert(`Token Debug Info:\n${JSON.stringify(response.data, null, 2)}`);
        } catch (err) {
            console.error('Token debug error:', err);
            setError(err.response?.data?.error || 'Token debug failed');
        }
    };

    const fixUserContext = async (username) => {
        try {
            const response = await axios.post(
                `${getApiUrl()}/admin-oversight/fix/update-user-context`,
                {
                    username: username
                },
                getAuthHeaders()
            );
            alert(response.data.message + '\n\n' + response.data.note);
            // Refresh debug data
            debugUserOrganizations();
        } catch (err) {
            console.error('Context fix error:', err);
            setError(err.response?.data?.error || 'Context fix failed');
        }
    };

    const debugAllRelationships = async () => {
        try {
            const response = await axios.get(
                `${getApiUrl()}/admin-oversight/debug/all-relationships`,
                getAuthHeaders()
            );
            setDebugResult({
                ...response.data,
                type: 'all_relationships'
            });
        } catch (err) {
            console.error('Debug all relationships error:', err);
            setError(err.response?.data?.error || 'Debug all relationships failed');
        }
    };

    if (loading && !dashboardData) {
        return (
            <div className="min-vh-100 bg-light">
                <Navbar />
                <NotificationSystem />
                <Container className="mt-5 text-center">
                    <Spinner animation="border" variant="primary" />
                    <p className="mt-3">Loading admin oversight...</p>
                </Container>
            </div>
        );
    }

    return (
        <div className="min-vh-100 bg-light">
            <Navbar />
            <NotificationSystem />
            <Container fluid className="mt-4">
                <h2 className="mb-4">🔍 Admin Oversight Dashboard</h2>
                
                {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

            {/* Navigation Tabs */}
            <Row className="mb-4">
                <Col>
                    <div className="d-flex gap-2">
                        <Button 
                            variant={activeTab === 'dashboard' ? 'primary' : 'outline-primary'}
                            onClick={() => handleTabChange('dashboard')}
                        >
                            📊 Dashboard
                        </Button>
                        <Button 
                            variant={activeTab === 'organizations' ? 'primary' : 'outline-primary'}
                            onClick={() => handleTabChange('organizations')}
                        >
                            🏢 Organizations
                        </Button>
                        <Button 
                            variant={activeTab === 'users' ? 'primary' : 'outline-primary'}
                            onClick={() => handleTabChange('users')}
                        >
                            👥 Users
                        </Button>
                        <Button 
                            variant={activeTab === 'debug' ? 'primary' : 'outline-primary'}
                            onClick={() => handleTabChange('debug')}
                        >
                            🔧 Debug
                        </Button>
                    </div>
                </Col>
            </Row>

            {/* Dashboard Tab */}
            {activeTab === 'dashboard' && dashboardData && (
                <>
                    <Row className="mb-4">
                        <Col md={4}>
                            <Card className="h-100">
                                <Card.Body>
                                    <Card.Title>📈 System Stats</Card.Title>
                                    <h3 className="text-primary">{dashboardData.stats.total_organizations}</h3>
                                    <p className="text-muted">Total Organizations</p>
                                    <h3 className="text-success">{dashboardData.stats.total_users}</h3>
                                    <p className="text-muted">Total Users</p>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col md={8}>
                            <Card className="h-100">
                                <Card.Body>
                                    <Card.Title>🏢 Recent Organizations</Card.Title>
                                    {dashboardData.recent_organizations.length > 0 ? (
                                        <Table striped size="sm">
                                            <thead>
                                                <tr>
                                                    <th>Name</th>
                                                    <th>Created</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {dashboardData.recent_organizations.map(org => (
                                                    <tr key={org.id}>
                                                        <td>{org.name}</td>
                                                        <td>{new Date(org.created_at).toLocaleDateString()}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </Table>
                                    ) : (
                                        <p className="text-muted">No organizations found</p>
                                    )}
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Row>
                        <Col>
                            <Card>
                                <Card.Body>
                                    <Card.Title>📊 Organization Statistics</Card.Title>
                                    {dashboardData.organization_stats.length > 0 ? (
                                        <Table striped hover>
                                            <thead>
                                                <tr>
                                                    <th>Organization</th>
                                                    <th>Members</th>
                                                    <th>Created</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {dashboardData.organization_stats.map(org => (
                                                    <tr key={org.id}>
                                                        <td>{org.name}</td>
                                                        <td>{org.user_count}</td>
                                                        <td>{new Date(org.created_at).toLocaleDateString()}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </Table>
                                    ) : (
                                        <p className="text-muted">No organization data available</p>
                                    )}
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>
                </>
            )}

            {/* Organizations Tab */}
            {activeTab === 'organizations' && (
                <Card>
                    <Card.Body>
                        <div className="d-flex justify-content-between align-items-center mb-3">
                            <Card.Title>🏢 All Organizations ({organizations.length})</Card.Title>
                            <Button variant="outline-primary" onClick={loadOrganizations}>
                                🔄 Refresh
                            </Button>
                        </div>
                        
                        {loading ? (
                            <div className="text-center">
                                <Spinner animation="border" />
                            </div>
                        ) : organizations.length > 0 ? (
                            <Table striped hover responsive>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Members</th>
                                        <th>Created</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {organizations.map(org => (
                                        <tr key={org.id}>
                                            <td>
                                                <strong>{org.name}</strong>
                                                {org.description && (
                                                    <div className="text-muted small">{org.description}</div>
                                                )}
                                            </td>
                                            <td>{org.user_count}</td>
                                            <td>{new Date(org.created_at).toLocaleDateString()}</td>
                                            <td>
                                                <Button
                                                    size="sm"
                                                    variant="outline-primary"
                                                    className="me-2"
                                                    onClick={() => handleEditOrg(org)}
                                                >
                                                    ✏️ Edit
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="outline-danger"
                                                    onClick={() => {
                                                        setDeletingOrg(org);
                                                        setShowDeleteModal(true);
                                                    }}
                                                >
                                                    🗑️ Delete
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>
                        ) : (
                            <p className="text-muted">No organizations found</p>
                        )}
                    </Card.Body>
                </Card>
            )}

            {/* Users Tab */}
            {activeTab === 'users' && (
                <Card>
                    <Card.Body>
                        <div className="d-flex justify-content-between align-items-center mb-3">
                            <Card.Title>👥 All Users ({users.length})</Card.Title>
                            <Button variant="outline-primary" onClick={loadUsers}>
                                🔄 Refresh
                            </Button>
                        </div>
                        
                        {loading ? (
                            <div className="text-center">
                                <Spinner animation="border" />
                            </div>
                        ) : users.length > 0 ? (
                            <Table striped hover responsive>
                                <thead>
                                    <tr>
                                        <th>Username</th>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Organizations</th>
                                        <th>Joined</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.map(user => (
                                        <tr key={user.id}>
                                            <td><strong>{user.username}</strong></td>
                                            <td>{user.name || 'N/A'}</td>
                                            <td>{user.email}</td>
                                            <td>
                                                {user.organizations.map((org, index) => (
                                                    <div key={index} className="small">
                                                        {org.name} ({org.role})
                                                    </div>
                                                ))}
                                            </td>
                                            <td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                                            <td>
                                                {user.username !== 'Harvey258' && (
                                                    <Button
                                                        variant="outline-danger"
                                                        size="sm"
                                                        onClick={() => {
                                                            setDeletingUser(user);
                                                            setShowDeleteUserModal(true);
                                                        }}
                                                        title="Delete User"
                                                    >
                                                        🗑️
                                                    </Button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>
                        ) : (
                            <p className="text-muted">No users found</p>
                        )}
                    </Card.Body>
                </Card>
            )}

            {/* Debug Tab */}
            {activeTab === 'debug' && (
                <Row>
                    <Col md={6}>
                        <Card>
                            <Card.Body>
                                <Card.Title>🔧 Debug User Organizations</Card.Title>
                                <div className="mb-3">
                                    <Form.Group>
                                        <Form.Label>Username</Form.Label>
                                        <Form.Control
                                            type="text"
                                            value={debugUser}
                                            onChange={(e) => setDebugUser(e.target.value)}
                                            placeholder="Enter username (e.g., Rob123)"
                                        />
                                    </Form.Group>
                                    <div className="d-flex gap-2 mt-2">
                                        <Button 
                                            variant="primary" 
                                            onClick={debugUserOrganizations}
                                            disabled={!debugUser.trim()}
                                            size="sm"
                                        >
                                            🔍 Check Organizations
                                        </Button>
                                        <Button 
                                            variant="info" 
                                            onClick={debugTokenInfo}
                                            disabled={!debugUser.trim()}
                                            size="sm"
                                        >
                                            🔍 Debug Token Info
                                        </Button>
                                        <Button 
                                            variant="warning" 
                                            onClick={fixUserContext}
                                            disabled={!debugUser.trim()}
                                            size="sm"
                                        >
                                            🔧 Fix User Context
                                        </Button>
                                    </div>
                                    <div className="mt-3">
                                        <Button 
                                            variant="success" 
                                            onClick={debugAllRelationships}
                                            size="sm"
                                        >
                                            🔍 Debug ALL User-Organization Relationships
                                        </Button>
                                    </div>
                                </div>
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col md={6}>
                        {debugResult && (
                            <Card>
                                <Card.Body>
                                    {debugResult.type === 'all_relationships' ? (
                                        <div>
                                            <Card.Title>🔍 All User-Organization Relationships</Card.Title>
                                            
                                            <div className="mb-3">
                                                <strong>Summary:</strong>
                                                <ul>
                                                    <li>Total Users: {debugResult.total_users}</li>
                                                    <li>Total Organizations: {debugResult.total_organizations}</li>
                                                    <li>Total Relationships: {debugResult.total_relationships}</li>
                                                </ul>
                                            </div>
                                            
                                            <div className="mb-3">
                                                <strong>Users and Their Organizations:</strong>
                                                <div style={{maxHeight: '400px', overflowY: 'auto'}}>
                                                    {debugResult.users.map(user => (
                                                        <div key={user.user_id} className="mb-2 p-2 border rounded">
                                                            <strong>{user.username}</strong> (ID: {user.user_id})
                                                            <div className="small text-muted">{user.email}</div>
                                                            {user.organizations.length > 0 ? (
                                                                <div className="mt-1">
                                                                    {user.organizations.map((org, idx) => (
                                                                        <span key={idx} className="badge bg-primary me-1">
                                                                            {org.organization_name} ({org.role})
                                                                        </span>
                                                                    ))}
                                                                </div>
                                                            ) : (
                                                                <div className="text-warning">No organizations</div>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                            
                                            <div className="mb-3">
                                                <strong>Organizations and Their Members:</strong>
                                                <div style={{maxHeight: '400px', overflowY: 'auto'}}>
                                                    {debugResult.organizations.map(org => (
                                                        <div key={org.organization_id} className="mb-2 p-2 border rounded">
                                                            <strong>{org.organization_name}</strong> (ID: {org.organization_id})
                                                            <div className="small text-muted">Members: {org.member_count}</div>
                                                            {org.members.length > 0 ? (
                                                                <div className="mt-1">
                                                                    {org.members.map((member, idx) => (
                                                                        <span key={idx} className="badge bg-success me-1">
                                                                            {member.username} ({member.role})
                                                                        </span>
                                                                    ))}
                                                                </div>
                                                            ) : (
                                                                <div className="text-warning">No members</div>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div>
                                            <Card.Title>🔍 Debug Results for {debugResult.user.username}</Card.Title>
                                    
                                    <div className="mb-3">
                                        <strong>User Info:</strong>
                                        <ul>
                                            <li>ID: {debugResult.user.id}</li>
                                            <li>Name: {debugResult.user.name || 'N/A'}</li>
                                            <li>Email: {debugResult.user.email}</li>
                                        </ul>
                                    </div>
                                    
                                    <div className="mb-3">
                                        <strong>Legacy Organization Fields:</strong>
                                        <ul>
                                            <li>Legacy Org: {debugResult.legacy_organization || 'None'}</li>
                                            <li>Current Org: {debugResult.current_organization || 'None'}</li>
                                            <li>Primary Org: {debugResult.primary_organization || 'None'}</li>
                                        </ul>
                                    </div>
                                    
                                    <div className="mb-3">
                                        <strong>Organization Memberships:</strong>
                                        {debugResult.user_organization_relationships.length > 0 ? (
                                            <ul>
                                                {debugResult.user_organization_relationships.map((rel, index) => (
                                                    <li key={index} className="mb-2">
                                                        <div className="d-flex align-items-center justify-content-between">
                                                            <span>
                                                                {rel.organization_name} ({rel.role}) 
                                                                {rel.is_active ? ' ✅' : ' ❌'}
                                                            </span>
                                                            {rel.role !== 'Admin' && (
                                                                <Button
                                                                    size="sm"
                                                                    variant="warning"
                                                                    onClick={() => updateUserRole(debugResult.user.username, rel.organization_name, 'Admin')}
                                                                >
                                                                    Make Admin
                                                                </Button>
                                                            )}
                                                        </div>
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <div>
                                                <Alert variant="warning">No organization memberships found!</Alert>
                                                <div className="mt-2">
                                                    <strong>Available Organizations:</strong>
                                                    <ul>
                                                        {debugResult.all_organizations.map(org => (
                                                            <li key={org.id}>
                                                                {org.name}
                                                                <Button
                                                                    size="sm"
                                                                    variant="success"
                                                                    className="ms-2"
                                                                    onClick={() => fixUserOrganization(debugResult.user.username, org.name)}
                                                                >
                                                                    Add User
                                                                </Button>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                        </div>
                                    )}
                                </Card.Body>
                            </Card>
                        )}
                    </Col>
                </Row>
            )}

            {/* Edit Organization Modal */}
            <Modal show={showEditModal} onHide={() => setShowEditModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>✏️ Edit Organization</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {editingOrg && (
                        <Form>
                            <Form.Group className="mb-3">
                                <Form.Label>Name</Form.Label>
                                <Form.Control
                                    type="text"
                                    value={editingOrg.name}
                                    onChange={(e) => setEditingOrg({...editingOrg, name: e.target.value})}
                                />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Description</Form.Label>
                                <Form.Control
                                    as="textarea"
                                    rows={3}
                                    value={editingOrg.description || ''}
                                    onChange={(e) => setEditingOrg({...editingOrg, description: e.target.value})}
                                />
                            </Form.Group>
                        </Form>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowEditModal(false)}>
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleSaveOrg}>
                        Save Changes
                    </Button>
                </Modal.Footer>
            </Modal>

            {/* Delete Organization Modal */}
            <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>🗑️ Delete Organization</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {deletingOrg && (
                        <div>
                            <p>Are you sure you want to delete <strong>{deletingOrg.name}</strong>?</p>
                            <Alert variant="warning">
                                <strong>Warning:</strong> This action cannot be undone. All events, RSVPs, and user memberships for this organization will be permanently deleted.
                            </Alert>
                        </div>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
                        Cancel
                    </Button>
                    <Button variant="danger" onClick={handleDeleteOrg}>
                        Delete Organization
                    </Button>
                </Modal.Footer>
            </Modal>

            {/* Delete User Modal */}
            <Modal show={showDeleteUserModal} onHide={() => setShowDeleteUserModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>🗑️ Delete User</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {deletingUser && (
                        <div>
                            <p>Are you sure you want to delete <strong>{deletingUser.username}</strong>?</p>
                            <Alert variant="warning">
                                <strong>Warning:</strong> This action cannot be undone. The user and all their data will be permanently deleted:
                                <ul className="mt-2 mb-0">
                                    <li>User account and profile</li>
                                    <li>All RSVPs and survey responses</li>
                                    <li>Organization memberships</li>
                                    <li>Events created by this user will be transferred to organization admins</li>
                                </ul>
                            </Alert>
                        </div>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowDeleteUserModal(false)}>
                        Cancel
                    </Button>
                    <Button variant="danger" onClick={handleDeleteUser}>
                        Delete User
                    </Button>
                </Modal.Footer>
            </Modal>
            </Container>
        </div>
    );
};

export default AdminOversightPage;
