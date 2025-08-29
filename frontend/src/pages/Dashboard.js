import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, Modal } from 'react-bootstrap';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

const Dashboard = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [user, setUser] = useState(null);
    const [events, setEvents] = useState([]);
    
    // Templates functionality
    const [templates, setTemplates] = useState([]);
    const [showTemplatesModal, setShowTemplatesModal] = useState(false);
    const [showTemplateCreateModal, setShowTemplateCreateModal] = useState(false);
    const [selectedTemplate, setSelectedTemplate] = useState(null);
    const [templateDate, setTemplateDate] = useState('');
    const [templateLocation, setTemplateLocation] = useState('');
    const [templateLoading, setTemplateLoading] = useState(false);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const username = localStorage.getItem('username');
            
            if (!token || !username) {
                window.location.href = '/login';
                return;
            }

            const headers = { Authorization: `Bearer ${token}` };
            
            // Load user profile and recent events
            const [userResponse, eventsResponse] = await Promise.all([
                axios.get(`${getApiUrl()}/auth/profile`, { headers }),
                axios.get(`${getApiUrl()}/events`, { headers }).catch(() => ({ data: [] }))
            ]);

            setUser(userResponse.data);
            
            // Remove automatic admin redirect - let admins use dashboard too
            
            setEvents(Array.isArray(eventsResponse.data) ? eventsResponse.data.slice(0, 5) : []);
            
            // Load templates if user is admin
            if (userResponse.data.role === 'Admin') {
                loadTemplates();
            }
            
        } catch (err) {
            console.error('Dashboard load error:', err);
            setError('Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    const loadTemplates = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${getApiUrl()}/events/templates`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTemplates(response.data);
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    };

    const createEventFromTemplate = async () => {
        if (!selectedTemplate || !templateDate) {
            alert('Please select a date for the event');
            return;
        }

        setTemplateLoading(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`${getApiUrl()}/events/from-template/${selectedTemplate.id}`, {
                date: templateDate,
                location_address: templateLocation,
                title: selectedTemplate.template_name || selectedTemplate.title
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            alert('Event created successfully from template!');
            setShowTemplateCreateModal(false);
            setSelectedTemplate(null);
            setTemplateDate('');
            setTemplateLocation('');
            
            // Refresh events
            loadDashboardData();
        } catch (error) {
            console.error('Error creating event from template:', error);
            alert('Failed to create event from template');
        } finally {
            setTemplateLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-vh-100 bg-light">
                <Navbar />
                <NotificationSystem />
                <Container className="mt-5 text-center">
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-3">Loading dashboard...</p>
                </Container>
            </div>
        );
    }

    return (
        <div className="min-vh-100 bg-light">
            <Navbar />
            <NotificationSystem />
            
            <Container fluid className="mt-4">
                <Row>
                    <Col>
                        <h2 className="mb-4">📊 Dashboard</h2>
                        
                        {error && (
                            <Alert variant="danger" dismissible onClose={() => setError('')}>
                                {error}
                            </Alert>
                        )}

                        <Row>
                            <Col md={6}>
                                <Card className="mb-4">
                                    <Card.Header>
                                        <Card.Title className="mb-0">👋 Welcome</Card.Title>
                                    </Card.Header>
                                    <Card.Body>
                                        {user ? (
                                            <>
                                                <p><strong>Name:</strong> {user.name || 'Not set'}</p>
                                                <p><strong>Email:</strong> {user.email || 'Not set'}</p>
                                                <p><strong>Role:</strong> {user.role || 'Member'}</p>
                                                {user.organization && (
                                                    <p><strong>Organization:</strong> {user.organization}</p>
                                                )}
                                            </>
                                        ) : (
                                            <p>User information not available</p>
                                        )}
                                    </Card.Body>
                                </Card>
                            </Col>

                            <Col md={6}>
                                <Card className="mb-4">
                                    <Card.Header>
                                        <Card.Title className="mb-0">📅 Recent Events</Card.Title>
                                    </Card.Header>
                                    <Card.Body>
                                        {events && events.length > 0 ? (
                                            <div>
                                                {events.map((event, index) => (
                                                    <div key={event.id || index} className="border-bottom pb-2 mb-2">
                                                        <strong>{event.title || 'Untitled Event'}</strong>
                                                        {event.date && (
                                                            <div className="text-muted small">
                                                                {new Date(event.date).toLocaleDateString()}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                                <Button 
                                                    variant="primary" 
                                                    size="sm" 
                                                    onClick={() => window.location.href = '/events'}
                                                >
                                                    View All Events
                                                </Button>
                                            </div>
                                        ) : (
                                            <div>
                                                <p className="text-muted">No recent events</p>
                                                <Button 
                                                    variant="outline-primary" 
                                                    size="sm"
                                                    onClick={() => window.location.href = '/events'}
                                                >
                                                    Go to Events
                                                </Button>
                                            </div>
                                        )}
                                    </Card.Body>
                                </Card>
                            </Col>
                        </Row>

                        <Row>
                            <Col>
                                <Card>
                                    <Card.Header>
                                        <Card.Title className="mb-0">🚀 Quick Actions</Card.Title>
                                    </Card.Header>
                                    <Card.Body>
                                        <div className="d-flex gap-2 flex-wrap">
                                            <Button 
                                                variant="primary"
                                                onClick={() => window.location.href = '/events'}
                                            >
                                                📅 View Events
                                            </Button>
                                            {user?.role === 'Admin' && (
                                                <Button 
                                                    variant="success"
                                                    onClick={() => setShowTemplatesModal(true)}
                                                >
                                                    📝 Event Templates
                                                </Button>
                                            )}
                                            <Button 
                                                variant="outline-primary"
                                                onClick={() => window.location.href = '/profile'}
                                            >
                                                👤 Edit Profile
                                            </Button>
                                            {user?.role === 'Admin' && (
                                                <Button 
                                                    variant="outline-secondary"
                                                    onClick={() => window.location.href = '/admin'}
                                                >
                                                    ⚙️ Admin Panel
                                                </Button>
                                            )}
                                        </div>
                                    </Card.Body>
                                </Card>
                            </Col>
                        </Row>
                    </Col>
                </Row>
            </Container>

            {/* Templates Modal */}
            <Modal show={showTemplatesModal} onHide={() => setShowTemplatesModal(false)} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>📝 Event Templates</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {templates.length === 0 ? (
                        <div className="text-center text-muted">
                            <p>No templates found. Create an event and save it as a template.</p>
                        </div>
                    ) : (
                        <Row>
                            {templates.map(template => (
                                <Col md={6} lg={4} key={template.id} className="mb-3">
                                    <Card className="h-100">
                                        <Card.Body>
                                            <Card.Title className="h6">
                                                {template.template_name || 'Untitled Template'}
                                            </Card.Title>
                                            <Card.Text className="small text-muted">
                                                {template.description || 'No description'}
                                            </Card.Text>
                                            {template.category && (
                                                <div className="mb-2">
                                                    <small className="badge bg-secondary">{template.category}</small>
                                                </div>
                                            )}
                                            <Button 
                                                variant="primary" 
                                                size="sm"
                                                onClick={() => {
                                                    setSelectedTemplate(template);
                                                    setShowTemplatesModal(false);
                                                    setShowTemplateCreateModal(true);
                                                }}
                                                className="w-100"
                                            >
                                                Use Template
                                            </Button>
                                        </Card.Body>
                                    </Card>
                                </Col>
                            ))}
                        </Row>
                    )}
                </Modal.Body>
            </Modal>

            {/* Create Event from Template Modal */}
            <Modal show={showTemplateCreateModal} onHide={() => {
                setShowTemplateCreateModal(false);
                setSelectedTemplate(null);
                setTemplateDate('');
                setTemplateLocation('');
            }}>
                <Modal.Header closeButton>
                    <Modal.Title>📅 Create Event from Template</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {selectedTemplate && (
                        <>
                            <div className="mb-3">
                                <h6 className="fw-bold">{selectedTemplate.template_name || selectedTemplate.title}</h6>
                                <p className="text-muted small mb-0">{selectedTemplate.description}</p>
                                {selectedTemplate.category && (
                                    <span className="badge bg-secondary mt-1">{selectedTemplate.category}</span>
                                )}
                            </div>
                            
                            <div className="mb-3">
                                <label htmlFor="template-date" className="form-label">
                                    📅 Event Date & Time *
                                </label>
                                <input
                                    type="datetime-local"
                                    className="form-control"
                                    id="template-date"
                                    value={templateDate}
                                    onChange={(e) => setTemplateDate(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="mb-3">
                                <label htmlFor="template-location" className="form-label">
                                    📍 Location (Optional)
                                </label>
                                <input
                                    type="text"
                                    className="form-control"
                                    id="template-location"
                                    value={templateLocation}
                                    onChange={(e) => setTemplateLocation(e.target.value)}
                                    placeholder="Enter event location"
                                />
                            </div>

                            <div className="alert alert-info">
                                <i className="bi bi-info-circle me-2"></i>
                                <strong>Note:</strong> This will create a new event using the template's settings. 
                                You can modify the event details after creation.
                            </div>
                        </>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button 
                        variant="secondary" 
                        onClick={() => {
                            setShowTemplateCreateModal(false);
                            setSelectedTemplate(null);
                            setTemplateDate('');
                            setTemplateLocation('');
                        }}
                        disabled={templateLoading}
                    >
                        Cancel
                    </Button>
                    <Button 
                        variant="primary"
                        onClick={createEventFromTemplate}
                        disabled={templateLoading || !templateDate}
                    >
                        {templateLoading ? (
                            <>
                                <span className="spinner-border spinner-border-sm me-2"></span>
                                Creating...
                            </>
                        ) : (
                            <>📅 Create Event</>
                        )}
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default Dashboard;