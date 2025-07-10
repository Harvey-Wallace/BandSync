import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardBody, 
  CardHeader, 
  CardTitle,
  Button,
  Form,
  FormGroup,
  Input,
  Label,
  Table,
  Badge,
  Alert,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Spinner,
  Nav,
  NavItem,
  NavLink,
  TabContent,
  TabPane
} from 'reactstrap';
import { 
  FaUserFriends, 
  FaHandPaper, 
  FaCheck, 
  FaTimes, 
  FaClock,
  FaList
} from 'react-icons/fa';
import Toast from './Toast';

const SubstitutionManager = () => {
  const [activeTab, setActiveTab] = useState('requests');
  const [myRequests, setMyRequests] = useState([]);
  const [availableRequests, setAvailableRequests] = useState([]);
  const [callList, setCallList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [showCallListModal, setShowCallListModal] = useState(false);
  const [showAvailabilityModal, setShowAvailabilityModal] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [userAvailability, setUserAvailability] = useState(true);

  const [newCallListEntry] = useState({
    entries: []
  });

  useEffect(() => {
    fetchSubstituteRequests();
    fetchAvailableRequests();
    fetchCallList();
    // TODO: Check if user is admin
    setIsAdmin(true);
  }, []);

  const fetchSubstituteRequests = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/substitutes/requests', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMyRequests(data);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch substitute requests' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading requests' });
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableRequests = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/substitutes/available', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAvailableRequests(data);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch available requests' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading available requests' });
    }
  };

  const fetchCallList = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/substitutes/call-list', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCallList(data);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch call list' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading call list' });
    }
  };

  const handleAcceptSubstitute = async (requestId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/substitutes/accept', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ request_id: requestId })
      });
      
      if (response.ok) {
        const data = await response.json();
        setToast({ type: 'success', message: data.message });
        fetchAvailableRequests();
        fetchSubstituteRequests();
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to accept substitute request' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error accepting request' });
    }
  };

  const handleDeclineSubstitute = async (requestId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/substitutes/decline', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ request_id: requestId })
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Substitute request declined' });
        fetchAvailableRequests();
      } else {
        setToast({ type: 'error', message: 'Failed to decline substitute request' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error declining request' });
    }
  };

  const handleUpdateCallList = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/substitutes/call-list', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newCallListEntry)
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Call list updated successfully' });
        setShowCallListModal(false);
        fetchCallList();
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to update call list' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error updating call list' });
    }
  };

  const handleUpdateAvailability = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/substitutes/availability', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ available_for_substitution: userAvailability })
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Availability updated successfully' });
        setShowAvailabilityModal(false);
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to update availability' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error updating availability' });
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge color="warning"><FaClock className="me-1" />Pending</Badge>;
      case 'fulfilled':
        return <Badge color="success"><FaCheck className="me-1" />Fulfilled</Badge>;
      case 'cancelled':
        return <Badge color="danger"><FaTimes className="me-1" />Cancelled</Badge>;
      default:
        return <Badge color="secondary">Unknown</Badge>;
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <Spinner color="primary" />
        <p className="mt-2">Loading substitute information...</p>
      </div>
    );
  }

  return (
    <div className="substitution-manager">
      <Card>
        <CardHeader>
          <CardTitle className="d-flex justify-content-between align-items-center">
            <span><FaUserFriends className="me-2" />Substitution Management</span>
            <div>
              <Button 
                color="info" 
                size="sm" 
                className="me-2"
                onClick={() => setShowAvailabilityModal(true)}
              >
                <FaHandPaper className="me-1" />My Availability
              </Button>
              {isAdmin && (
                <Button 
                  color="primary" 
                  size="sm"
                  onClick={() => setShowCallListModal(true)}
                >
                  <FaList className="me-1" />Manage Call List
                </Button>
              )}
            </div>
          </CardTitle>
        </CardHeader>
        <CardBody>
          <Nav tabs>
            <NavItem>
              <NavLink 
                active={activeTab === 'requests'} 
                onClick={() => setActiveTab('requests')}
                style={{ cursor: 'pointer' }}
              >
                My Requests
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink 
                active={activeTab === 'available'} 
                onClick={() => setActiveTab('available')}
                style={{ cursor: 'pointer' }}
              >
                Available Requests
                {availableRequests.length > 0 && (
                  <Badge color="primary" className="ms-2">
                    {availableRequests.length}
                  </Badge>
                )}
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink 
                active={activeTab === 'calllist'} 
                onClick={() => setActiveTab('calllist')}
                style={{ cursor: 'pointer' }}
              >
                Call List
              </NavLink>
            </NavItem>
          </Nav>

          <TabContent activeTab={activeTab}>
            {/* My Requests Tab */}
            <TabPane tabId="requests">
              <div className="mt-3">
                {myRequests.length === 0 ? (
                  <Alert color="info">
                    You haven't made any substitute requests yet. When you RSVP "No" to an event, you'll have the option to request a substitute.
                  </Alert>
                ) : (
                  <Table responsive>
                    <thead>
                      <tr>
                        <th>Event</th>
                        <th>Date/Time</th>
                        <th>Status</th>
                        <th>Substitute</th>
                        <th>Requested</th>
                      </tr>
                    </thead>
                    <tbody>
                      {myRequests.map((request) => (
                        <tr key={request.id}>
                          <td>
                            <strong>{request.event.name}</strong>
                            <br />
                            <small className="text-muted">{request.event.location}</small>
                          </td>
                          <td>{formatDateTime(request.event.start_datetime)}</td>
                          <td>{getStatusBadge(request.status)}</td>
                          <td>
                            {request.substitute_user ? (
                              <div>
                                <strong>{request.substitute_user.name}</strong>
                                <br />
                                <small className="text-muted">
                                  Accepted {formatDateTime(request.fulfilled_at)}
                                </small>
                              </div>
                            ) : (
                              <span className="text-muted">No substitute yet</span>
                            )}
                          </td>
                          <td>{formatDateTime(request.requested_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </div>
            </TabPane>

            {/* Available Requests Tab */}
            <TabPane tabId="available">
              <div className="mt-3">
                {availableRequests.length === 0 ? (
                  <Alert color="info">
                    No substitute requests available at this time. Check back later or update your availability settings.
                  </Alert>
                ) : (
                  <Table responsive>
                    <thead>
                      <tr>
                        <th>Event</th>
                        <th>Date/Time</th>
                        <th>Original Member</th>
                        <th>Reason</th>
                        <th>Requested</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {availableRequests.map((request) => (
                        <tr key={request.id}>
                          <td>
                            <strong>{request.event.name}</strong>
                            <br />
                            <small className="text-muted">{request.event.location}</small>
                            {request.event.description && (
                              <>
                                <br />
                                <small className="text-muted">{request.event.description}</small>
                              </>
                            )}
                          </td>
                          <td>{formatDateTime(request.event.start_datetime)}</td>
                          <td>{request.original_user.name}</td>
                          <td>{request.reason || 'No reason provided'}</td>
                          <td>{formatDateTime(request.requested_at)}</td>
                          <td>
                            <Button
                              color="success"
                              size="sm"
                              className="me-2"
                              onClick={() => handleAcceptSubstitute(request.id)}
                              disabled={!request.can_substitute}
                            >
                              <FaCheck className="me-1" />Accept
                            </Button>
                            <Button
                              color="secondary"
                              size="sm"
                              onClick={() => handleDeclineSubstitute(request.id)}
                            >
                              <FaTimes className="me-1" />Decline
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </div>
            </TabPane>

            {/* Call List Tab */}
            <TabPane tabId="calllist">
              <div className="mt-3">
                {callList.length === 0 ? (
                  <Alert color="info">
                    No call list configured. Contact your administrator to set up substitute priorities.
                  </Alert>
                ) : (
                  <Table responsive>
                    <thead>
                      <tr>
                        <th>Priority</th>
                        <th>Member</th>
                        <th>Email</th>
                        <th>Available</th>
                        <th>Last Substitute</th>
                        <th>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {callList.map((entry) => (
                        <tr key={entry.id}>
                          <td>
                            <Badge color="primary">#{entry.priority_order}</Badge>
                          </td>
                          <td>{entry.user.name}</td>
                          <td>{entry.user.email}</td>
                          <td>
                            <Badge color={entry.available_for_substitution ? 'success' : 'secondary'}>
                              {entry.available_for_substitution ? 'Available' : 'Unavailable'}
                            </Badge>
                          </td>
                          <td>
                            {entry.last_substitute_date ? 
                              formatDateTime(entry.last_substitute_date) : 
                              'Never'
                            }
                          </td>
                          <td>{entry.notes || 'None'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </div>
            </TabPane>
          </TabContent>
        </CardBody>
      </Card>

      {/* Call List Management Modal */}
      <Modal isOpen={showCallListModal} toggle={() => setShowCallListModal(false)} size="lg">
        <ModalHeader toggle={() => setShowCallListModal(false)}>
          Manage Call List
        </ModalHeader>
        <Form onSubmit={handleUpdateCallList}>
          <ModalBody>
            <Alert color="info">
              <strong>Call List Management</strong><br />
              This feature allows you to set the priority order for substitute requests. 
              When a substitute is needed, members will be contacted in this order.
            </Alert>
            
            <div className="mt-3">
              <p><strong>Current Call List:</strong></p>
              {callList.map((entry, index) => (
                <div key={entry.id} className="d-flex align-items-center mb-2 p-2 border rounded">
                  <Badge color="primary" className="me-2">#{index + 1}</Badge>
                  <div className="flex-grow-1">
                    <strong>{entry.user.name}</strong>
                    <br />
                    <small className="text-muted">{entry.user.email}</small>
                  </div>
                  <Badge color={entry.available_for_substitution ? 'success' : 'secondary'}>
                    {entry.available_for_substitution ? 'Available' : 'Unavailable'}
                  </Badge>
                </div>
              ))}
            </div>
            
            <Alert color="warning">
              <strong>Note:</strong> Full call list management functionality requires additional implementation. 
              Currently showing read-only view.
            </Alert>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={() => setShowCallListModal(false)}>
              Close
            </Button>
          </ModalFooter>
        </Form>
      </Modal>

      {/* Availability Modal */}
      <Modal isOpen={showAvailabilityModal} toggle={() => setShowAvailabilityModal(false)}>
        <ModalHeader toggle={() => setShowAvailabilityModal(false)}>
          Update Availability
        </ModalHeader>
        <Form onSubmit={handleUpdateAvailability}>
          <ModalBody>
            <Alert color="info">
              <strong>Substitute Availability</strong><br />
              Control whether you want to receive substitute requests from other members.
            </Alert>
            
            <FormGroup check>
              <Input
                type="checkbox"
                id="availability"
                checked={userAvailability}
                onChange={(e) => setUserAvailability(e.target.checked)}
              />
              <Label check for="availability">
                I am available to substitute for other members
              </Label>
            </FormGroup>
            
            <small className="text-muted">
              When enabled, you will receive notifications when other members need substitutes for events.
            </small>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={() => setShowAvailabilityModal(false)}>
              Cancel
            </Button>
            <Button color="primary" type="submit">
              Update Availability
            </Button>
          </ModalFooter>
        </Form>
      </Modal>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

export default SubstitutionManager;
