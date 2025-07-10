import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardBody, 
  CardHeader, 
  CardTitle,
  Row,
  Col,
  Button,
  Form,
  FormGroup,
  Input,
  Label,
  Alert,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Spinner,
  Progress,
  Badge,
  ListGroup,
  ListGroupItem
} from 'reactstrap';
import { 
  FaPoll, 
  FaPlus, 
  FaVoteYea, 
  FaEye,
  FaTrash,
  FaCheck,
  FaTimes,
  FaDownload
} from 'react-icons/fa';
import Toast from './Toast';

const QuickPolls = () => {
  const [polls, setPolls] = useState([]);
  const [pollTemplates, setPollTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showTemplatesModal, setShowTemplatesModal] = useState(false);
  const [selectedPoll, setSelectedPoll] = useState(null);
  const [toast, setToast] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);

  const [newPoll, setNewPoll] = useState({
    question: '',
    options: ['', ''],
    poll_type: 'simple',
    is_anonymous: false,
    multiple_choice: false,
    expires_in_hours: 24
  });

  // const [pollResponse, setPollResponse] = useState(''); // Future use for responses

  useEffect(() => {
    fetchPolls();
    fetchTemplates();
    // TODO: Check if user is admin
    setIsAdmin(true);
  }, []);

  const fetchPolls = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/polls', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPolls(data);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch polls' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading polls' });
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/polls/templates', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPollTemplates(data);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchPollDetails = async (pollId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/polls/${pollId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSelectedPoll(data);
        setShowDetailsModal(true);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch poll details' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading poll details' });
    }
  };

  const handleCreatePoll = async (e) => {
    e.preventDefault();
    
    // Filter out empty options
    const validOptions = newPoll.options.filter(option => option.trim() !== '');
    
    if (validOptions.length < 2) {
      setToast({ type: 'error', message: 'Please provide at least 2 options' });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/polls', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...newPoll,
          options: validOptions
        })
      });

      if (response.ok) {
        setToast({ type: 'success', message: 'Poll created successfully' });
        setShowCreateModal(false);
        setNewPoll({
          question: '',
          options: ['', ''],
          poll_type: 'simple',
          is_anonymous: false,
          multiple_choice: false,
          expires_in_hours: 24
        });
        fetchPolls();
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to create poll' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error creating poll' });
    }
  };

  const handleVote = async (pollId, response) => {
    try {
      const token = localStorage.getItem('token');
      const result = await fetch(`/api/polls/${pollId}/respond`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ response })
      });

      if (result.ok) {
        setToast({ type: 'success', message: 'Vote recorded successfully' });
        fetchPolls();
      } else {
        const error = await result.json();
        setToast({ type: 'error', message: error.error || 'Failed to record vote' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error recording vote' });
    }
  };

  const handleClosePoll = async (pollId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/polls/${pollId}/close`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setToast({ type: 'success', message: 'Poll closed successfully' });
        fetchPolls();
      } else {
        setToast({ type: 'error', message: 'Failed to close poll' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error closing poll' });
    }
  };

  const handleDeletePoll = async (pollId) => {
    if (!window.confirm('Are you sure you want to delete this poll?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/polls/${pollId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setToast({ type: 'success', message: 'Poll deleted successfully' });
        fetchPolls();
      } else {
        setToast({ type: 'error', message: 'Failed to delete poll' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error deleting poll' });
    }
  };

  const handleExportResults = async (pollId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/polls/${pollId}/export`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        const csvContent = [
          ['Question', 'User Name', 'User Email', 'Response', 'Responded At'],
          ...data.responses.map(r => [
            data.poll_question,
            r.user_name,
            r.user_email,
            r.response,
            r.responded_at
          ])
        ].map(row => row.join(',')).join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `poll_results_${pollId}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        setToast({ type: 'success', message: 'Poll results exported successfully' });
      } else {
        setToast({ type: 'error', message: 'Failed to export results' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error exporting results' });
    }
  };

  const handleUseTemplate = (template) => {
    setNewPoll({
      ...newPoll,
      question: template.question,
      options: [...template.options],
      poll_type: template.poll_type,
      multiple_choice: template.multiple_choice || false
    });
    setShowTemplatesModal(false);
  };

  const addOption = () => {
    setNewPoll({
      ...newPoll,
      options: [...newPoll.options, '']
    });
  };

  const removeOption = (index) => {
    if (newPoll.options.length > 2) {
      setNewPoll({
        ...newPoll,
        options: newPoll.options.filter((_, i) => i !== index)
      });
    }
  };

  const updateOption = (index, value) => {
    const newOptions = [...newPoll.options];
    newOptions[index] = value;
    setNewPoll({
      ...newPoll,
      options: newOptions
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusBadge = (poll) => {
    if (!poll.is_active) {
      return <Badge color="secondary">Closed</Badge>;
    }
    if (poll.is_expired) {
      return <Badge color="warning">Expired</Badge>;
    }
    return <Badge color="success">Active</Badge>;
  };

  const calculatePercentage = (count, total) => {
    if (total === 0) return 0;
    return Math.round((count / total) * 100);
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <Spinner color="primary" />
        <p className="mt-2">Loading polls...</p>
      </div>
    );
  }

  return (
    <div className="quick-polls">
      <Card>
        <CardHeader>
          <CardTitle className="d-flex justify-content-between align-items-center">
            <span><FaPoll className="me-2" />Quick Polls</span>
            {isAdmin && (
              <div>
                <Button 
                  color="info" 
                  size="sm" 
                  className="me-2"
                  onClick={() => setShowTemplatesModal(true)}
                >
                  <FaEye className="me-1" />Templates
                </Button>
                <Button 
                  color="primary" 
                  size="sm"
                  onClick={() => setShowCreateModal(true)}
                >
                  <FaPlus className="me-1" />New Poll
                </Button>
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardBody>
          {polls.length === 0 ? (
            <Alert color="info">
              No polls available. {isAdmin && 'Create your first poll to get started!'}
            </Alert>
          ) : (
            <Row>
              {polls.map((poll) => (
                <Col md="6" key={poll.id} className="mb-4">
                  <Card className="h-100">
                    <CardHeader className="pb-2">
                      <div className="d-flex justify-content-between align-items-start">
                        <h6 className="mb-0">{poll.question}</h6>
                        {getStatusBadge(poll)}
                      </div>
                      <small className="text-muted">
                        Created {formatDate(poll.created_at)}
                        {poll.expires_at && ` • Expires ${formatDate(poll.expires_at)}`}
                      </small>
                    </CardHeader>
                    <CardBody className="pt-2">
                      {poll.user_responded ? (
                        <div>
                          <Alert color="success" className="py-2">
                            <FaCheck className="me-2" />
                            You voted: <strong>{poll.user_response}</strong>
                          </Alert>
                          
                          <div className="mt-3">
                            <h6>Results ({poll.total_responses} responses):</h6>
                            {poll.options.map((option) => {
                              const count = poll.option_counts[option] || 0;
                              const percentage = calculatePercentage(count, poll.total_responses);
                              return (
                                <div key={option} className="mb-2">
                                  <div className="d-flex justify-content-between mb-1">
                                    <span>{option}</span>
                                    <span>{count} ({percentage}%)</span>
                                  </div>
                                  <Progress value={percentage} />
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ) : (
                        <div>
                          {poll.is_active && !poll.is_expired ? (
                            <div>
                              <p className="mb-3">Choose your response:</p>
                              {poll.options.map((option) => (
                                <Button
                                  key={option}
                                  color="outline-primary"
                                  size="sm"
                                  className="me-2 mb-2"
                                  onClick={() => handleVote(poll.id, option)}
                                >
                                  <FaVoteYea className="me-1" />{option}
                                </Button>
                              ))}
                            </div>
                          ) : (
                            <Alert color="secondary" className="py-2">
                              <FaTimes className="me-2" />
                              This poll is no longer accepting responses.
                            </Alert>
                          )}
                        </div>
                      )}

                      <div className="mt-3 d-flex justify-content-between align-items-center">
                        <small className="text-muted">
                          {poll.total_responses} response{poll.total_responses !== 1 ? 's' : ''}
                          {poll.is_anonymous && ' • Anonymous'}
                        </small>
                        <div>
                          <Button
                            color="info"
                            size="sm"
                            className="me-2"
                            onClick={() => fetchPollDetails(poll.id)}
                          >
                            <FaEye />
                          </Button>
                          {isAdmin && (
                            <>
                              <Button
                                color="secondary"
                                size="sm"
                                className="me-2"
                                onClick={() => handleExportResults(poll.id)}
                              >
                                <FaDownload />
                              </Button>
                              {poll.is_active && (
                                <Button
                                  color="warning"
                                  size="sm"
                                  className="me-2"
                                  onClick={() => handleClosePoll(poll.id)}
                                >
                                  <FaTimes />
                                </Button>
                              )}
                              <Button
                                color="danger"
                                size="sm"
                                onClick={() => handleDeletePoll(poll.id)}
                              >
                                <FaTrash />
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                </Col>
              ))}
            </Row>
          )}
        </CardBody>
      </Card>

      {/* Create Poll Modal */}
      <Modal isOpen={showCreateModal} toggle={() => setShowCreateModal(false)}>
        <Form onSubmit={handleCreatePoll}>
          <ModalHeader toggle={() => setShowCreateModal(false)}>
            Create New Poll
          </ModalHeader>
          <ModalBody>
            <FormGroup>
              <Label>Question</Label>
              <Input
                type="text"
                value={newPoll.question}
                onChange={(e) => setNewPoll({...newPoll, question: e.target.value})}
                required
                placeholder="What would you like to ask?"
              />
            </FormGroup>

            <FormGroup>
              <Label>Options</Label>
              {newPoll.options.map((option, index) => (
                <div key={index} className="d-flex align-items-center mb-2">
                  <Input
                    type="text"
                    value={option}
                    onChange={(e) => updateOption(index, e.target.value)}
                    placeholder={`Option ${index + 1}`}
                    className="me-2"
                  />
                  {newPoll.options.length > 2 && (
                    <Button
                      color="danger"
                      size="sm"
                      onClick={() => removeOption(index)}
                    >
                      <FaTimes />
                    </Button>
                  )}
                </div>
              ))}
              <Button color="secondary" size="sm" onClick={addOption}>
                <FaPlus className="me-1" />Add Option
              </Button>
            </FormGroup>

            <FormGroup>
              <Label>Expires In</Label>
              <Input
                type="select"
                value={newPoll.expires_in_hours}
                onChange={(e) => setNewPoll({...newPoll, expires_in_hours: parseInt(e.target.value)})}
              >
                <option value={1}>1 Hour</option>
                <option value={6}>6 Hours</option>
                <option value={24}>24 Hours</option>
                <option value={72}>3 Days</option>
                <option value={168}>1 Week</option>
              </Input>
            </FormGroup>

            <FormGroup check>
              <Input
                type="checkbox"
                checked={newPoll.is_anonymous}
                onChange={(e) => setNewPoll({...newPoll, is_anonymous: e.target.checked})}
              />
              <Label check>
                Anonymous responses
              </Label>
            </FormGroup>

            <FormGroup check>
              <Input
                type="checkbox"
                checked={newPoll.multiple_choice}
                onChange={(e) => setNewPoll({...newPoll, multiple_choice: e.target.checked})}
              />
              <Label check>
                Allow multiple responses per user
              </Label>
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button color="primary" type="submit">
              Create Poll
            </Button>
          </ModalFooter>
        </Form>
      </Modal>

      {/* Poll Details Modal */}
      <Modal isOpen={showDetailsModal} toggle={() => setShowDetailsModal(false)} size="lg">
        <ModalHeader toggle={() => setShowDetailsModal(false)}>
          Poll Details
        </ModalHeader>
        <ModalBody>
          {selectedPoll && (
            <div>
              <h5>{selectedPoll.question}</h5>
              <p className="text-muted mb-3">
                Created by {selectedPoll.created_by?.name} on {formatDate(selectedPoll.created_at)}
                {selectedPoll.expires_at && ` • Expires ${formatDate(selectedPoll.expires_at)}`}
              </p>

              <div className="mb-4">
                <h6>Results ({selectedPoll.total_responses} responses):</h6>
                {selectedPoll.options.map((option) => {
                  const count = selectedPoll.option_counts[option] || 0;
                  const percentage = calculatePercentage(count, selectedPoll.total_responses);
                  return (
                    <div key={option} className="mb-3">
                      <div className="d-flex justify-content-between mb-1">
                        <span>{option}</span>
                        <span>{count} votes ({percentage}%)</span>
                      </div>
                      <Progress value={percentage} />
                    </div>
                  );
                })}
              </div>

              {selectedPoll.response_details && selectedPoll.response_details.length > 0 && (
                <div>
                  <h6>Individual Responses:</h6>
                  <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    <ListGroup>
                      {selectedPoll.response_details.map((response, index) => (
                        <ListGroupItem key={index} className="py-2">
                          <div className="d-flex justify-content-between">
                            <span>{response.user_name}</span>
                            <span>
                              <Badge color="primary">{response.response}</Badge>
                              <small className="text-muted ms-2">
                                {formatDate(response.responded_at)}
                              </small>
                            </span>
                          </div>
                        </ListGroupItem>
                      ))}
                    </ListGroup>
                  </div>
                </div>
              )}
            </div>
          )}
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={() => setShowDetailsModal(false)}>
            Close
          </Button>
        </ModalFooter>
      </Modal>

      {/* Templates Modal */}
      <Modal isOpen={showTemplatesModal} toggle={() => setShowTemplatesModal(false)}>
        <ModalHeader toggle={() => setShowTemplatesModal(false)}>
          Poll Templates
        </ModalHeader>
        <ModalBody>
          <p>Choose a template to get started quickly:</p>
          <ListGroup>
            {pollTemplates.map((template, index) => (
              <ListGroupItem 
                key={index} 
                action
                onClick={() => handleUseTemplate(template)}
                className="cursor-pointer"
              >
                <div>
                  <strong>{template.name}</strong>
                  <p className="mb-1">{template.question}</p>
                  <small className="text-muted">
                    Options: {template.options.join(', ')}
                  </small>
                </div>
              </ListGroupItem>
            ))}
          </ListGroup>
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={() => setShowTemplatesModal(false)}>
            Close
          </Button>
        </ModalFooter>
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

export default QuickPolls;
