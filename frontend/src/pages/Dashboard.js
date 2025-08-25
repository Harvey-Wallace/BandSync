import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert } from 'react-bootstrap';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

const Dashboard = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [user, setUser] = useState(null);
    const [events, setEvents] = useState([]);

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
            setEvents(Array.isArray(eventsResponse.data) ? eventsResponse.data.slice(0, 5) : []);
            
        } catch (err) {
            console.error('Dashboard load error:', err);
            setError('Failed to load dashboard data');
        } finally {
            setLoading(false);
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
                                            <Button 
                                                variant="outline-primary"
                                                onClick={() => window.location.href = '/profile'}
                                            >
                                                👤 Edit Profile
                                            </Button>
                                            {user?.role === 'Admin' && (
                                                <Button 
                                                    variant="success"
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
        </div>
    );
};

export default Dashboard;