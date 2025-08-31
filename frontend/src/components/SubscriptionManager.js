/**
 * Subscription Management Component
 * Handles organization subscription tiers, payments, and Stripe integration
 */

import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, Table, Badge, Spinner } from 'react-bootstrap';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

const SubscriptionManager = () => {
  const [user, setUser] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [tiers, setTiers] = useState({});
  const [loading, setLoading] = useState(true);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [showPaymentHistory, setShowPaymentHistory] = useState(false);

  useEffect(() => {
    // Get user info from token
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser(payload);
        fetchSubscriptionStatus();
        fetchSubscriptionTiers();
      } catch (error) {
        console.error('Error parsing token:', error);
      }
    }
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
      }
    } catch (error) {
      console.error('Error fetching subscription status:', error);
    }
  };

  const fetchSubscriptionTiers = async () => {
    try {
      const response = await axios.get(`${getApiUrl()}/subscription/tiers`);
      if (response.data.success) {
        setTiers(response.data.tiers);
      }
    } catch (error) {
      console.error('Error fetching subscription tiers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tier) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${getApiUrl()}/subscription/create-checkout-session`, {
        tier: tier
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.data.success) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to initiate payment. Please try again.');
    }
  };

  const handleManageBilling = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${getApiUrl()}/subscription/create-billing-portal-session`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.data.success) {
        window.location.href = response.data.portal_url;
      }
    } catch (error) {
      console.error('Error creating billing portal session:', error);
      alert('Failed to open billing portal. Please try again.');
    }
  };

  const fetchPaymentHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${getApiUrl()}/subscription/payment-history`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.data.success) {
        setPaymentHistory(response.data.payments);
        setShowPaymentHistory(true);
      }
    } catch (error) {
      console.error('Error fetching payment history:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatCurrency = (amount, currency = 'usd') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount / 100);
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <Spinner animation="border" />
          <p>Loading subscription information...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <h2>Subscription Management</h2>
          
          {/* Current Subscription */}
          <Card className="mb-4">
            <Card.Header>
              <h5>Current Subscription</h5>
            </Card.Header>
            <Card.Body>
              {subscription ? (
                <div>
                  <Row>
                    <Col md={6}>
                      <p><strong>Plan:</strong> {subscription.tier === 'pro' ? 'Professional' : 'Free'}</p>
                      <p><strong>Status:</strong> 
                        <Badge 
                          bg={subscription.status === 'active' ? 'success' : 'warning'}
                          className="ms-2"
                        >
                          {subscription.status}
                        </Badge>
                      </p>
                      <p><strong>Users:</strong> {subscription.current_user_count} / {subscription.tier === 'pro' ? 'Unlimited' : subscription.max_users}</p>
                    </Col>
                    <Col md={6}>
                      {subscription.tier === 'pro' && subscription.billing_period_start && (
                        <p><strong>Billing Period:</strong> {formatDate(subscription.billing_period_start)} - {formatDate(subscription.billing_period_end)}</p>
                      )}
                      {subscription.tier === 'free' && subscription.current_user_count >= subscription.max_users && (
                        <Alert variant="warning">
                          You've reached your user limit. Upgrade to Pro for unlimited users.
                        </Alert>
                      )}
                    </Col>
                  </Row>
                  
                  <div className="mt-3">
                    {subscription.tier === 'free' ? (
                      <Button onClick={() => handleUpgrade('pro')} variant="primary">
                        Upgrade to Pro
                      </Button>
                    ) : (
                      <div>
                        <Button onClick={handleManageBilling} variant="outline-primary" className="me-2">
                          Manage Billing
                        </Button>
                        <Button onClick={fetchPaymentHistory} variant="outline-secondary">
                          View Payment History
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <Alert variant="info">
                  No subscription information available.
                </Alert>
              )}
            </Card.Body>
          </Card>

          {/* Subscription Tiers */}
          <Card className="mb-4">
            <Card.Header>
              <h5>Available Plans</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Card className="mb-3">
                    <Card.Header className="text-center">
                      <h6>Free Plan</h6>
                    </Card.Header>
                    <Card.Body className="text-center">
                      <h4>$0<small className="text-muted">/month</small></h4>
                      <ul className="list-unstyled">
                        <li>✓ Up to 5 users</li>
                        <li>✓ Basic event management</li>
                        <li>✓ RSVP tracking</li>
                        <li>✓ Email notifications</li>
                      </ul>
                      {subscription?.tier === 'free' ? (
                        <Badge bg="success">Current Plan</Badge>
                      ) : (
                        <Button variant="outline-secondary" disabled>
                          Downgrade to Free
                        </Button>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
                
                <Col md={6}>
                  <Card className="mb-3 border-primary">
                    <Card.Header className="text-center bg-primary text-white">
                      <h6>Professional Plan</h6>
                    </Card.Header>
                    <Card.Body className="text-center">
                      <h4>$10<small className="text-muted">/month</small></h4>
                      <ul className="list-unstyled">
                        <li>✓ Unlimited users</li>
                        <li>✓ Advanced event management</li>
                        <li>✓ Calendar integration</li>
                        <li>✓ Analytics dashboard</li>
                        <li>✓ Priority support</li>
                      </ul>
                      {subscription?.tier === 'pro' ? (
                        <Badge bg="success">Current Plan</Badge>
                      ) : (
                        <Button onClick={() => handleUpgrade('pro')} variant="primary">
                          Upgrade to Pro
                        </Button>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Payment History */}
          {showPaymentHistory && paymentHistory.length > 0 && (
            <Card>
              <Card.Header>
                <h5>Payment History</h5>
              </Card.Header>
              <Card.Body>
                <Table striped bordered hover>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paymentHistory.map((payment, index) => (
                      <tr key={index}>
                        <td>{formatDate(payment.created_at)}</td>
                        <td>{formatCurrency(payment.amount, payment.currency)}</td>
                        <td>
                          <Badge bg={payment.status === 'succeeded' ? 'success' : 'warning'}>
                            {payment.status}
                          </Badge>
                        </td>
                        <td>{payment.description || 'Subscription payment'}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default SubscriptionManager;
