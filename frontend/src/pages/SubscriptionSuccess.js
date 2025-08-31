/**
 * Subscription Success Page
 * Displayed after successful Stripe checkout
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Card, Alert, Spinner, Button } from 'react-bootstrap';
import Navbar from '../components/Navbar';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

const SubscriptionSuccess = () => {
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    // Wait a moment for webhook processing, then fetch updated subscription
    const timer = setTimeout(() => {
      fetchSubscriptionStatus();
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${getApiUrl()}/subscription/status`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.data.success) {
        setSubscription(response.data.subscription);
      } else {
        setError('Failed to fetch subscription status');
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
      setError('Error fetching subscription status');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <Container className="mt-4">
        <Row className="justify-content-center">
          <Col md={8}>
            <Card>
              <Card.Header className="text-center bg-success text-white">
                <h2>🎉 Payment Successful!</h2>
              </Card.Header>
              <Card.Body className="text-center">
                {loading ? (
                  <div>
                    <Spinner animation="border" className="me-2" />
                    <p>Processing your subscription...</p>
                  </div>
                ) : error ? (
                  <Alert variant="warning">
                    <p>{error}</p>
                    <Button as={Link} to="/subscription" variant="primary">
                      View Subscription Details
                    </Button>
                  </Alert>
                ) : subscription ? (
                  <div>
                    <Alert variant="success">
                      <h4>Welcome to BandSync Pro! 🚀</h4>
                      <p>Your subscription has been activated successfully.</p>
                    </Alert>
                    
                    <div className="subscription-details mb-4">
                      <h5>Subscription Details</h5>
                      <p><strong>Plan:</strong> {subscription.tier === 'pro' ? 'Pro' : 'Free'}</p>
                      <p><strong>Status:</strong> <span className="text-success">{subscription.status}</span></p>
                      {subscription.tier === 'pro' && (
                        <>
                          <p><strong>Users:</strong> Unlimited</p>
                          <p><strong>Billing Period:</strong> {
                            subscription.billing_period_start ? 
                            `${new Date(subscription.billing_period_start).toLocaleDateString()} - ${new Date(subscription.billing_period_end).toLocaleDateString()}` :
                            'Processing...'
                          }</p>
                        </>
                      )}
                    </div>
                    
                    <div className="action-buttons">
                      <Button as={Link} to="/dashboard" variant="primary" className="me-3">
                        Go to Dashboard
                      </Button>
                      <Button as={Link} to="/subscription" variant="outline-secondary">
                        Manage Subscription
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Alert variant="info">
                    <p>No subscription information available.</p>
                    <Button as={Link} to="/subscription" variant="primary">
                      View Subscription Details
                    </Button>
                  </Alert>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default SubscriptionSuccess;
