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
                                    <Button 
                                        variant="primary" 
                                        onClick={debugUserOrganizations}
                                        disabled={!debugUser.trim()}
                                        className="mt-2"
                                    >
                                        🔍 Check Organizations
                                    </Button>
                                </div>
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col md={6}>
                        {debugResult && (
                            <Card>
                                <Card.Body>
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
            </Container>
        </div>
    );
};

export default AdminOversightPage;
