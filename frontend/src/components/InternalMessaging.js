import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, 
  CardBody, 
  CardHeader, 
  CardTitle,
  Row,
  Col,
  ListGroup,
  ListGroupItem,
  Form,
  FormGroup,
  Input,
  Button,
  Badge,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Spinner
} from 'reactstrap';
import { 
  FaEnvelope, 
  FaPlus, 
  FaPaperPlane, 
  FaUsers
} from 'react-icons/fa';
import Toast from './Toast';

const InternalMessaging = () => {
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [users, setUsers] = useState([]);
  // const [sections, setSections] = useState([]); // Future use for section-based messaging
  const [loading, setLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [showNewMessageModal, setShowNewMessageModal] = useState(false);
  const [showBroadcastModal, setShowBroadcastModal] = useState(false);
  const [toast, setToast] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const messagesEndRef = useRef(null);

  const [newThreadForm, setNewThreadForm] = useState({
    subject: '',
    participants: [],
    initial_message: ''
  });

  const [broadcastForm, setBroadcastForm] = useState({
    subject: '',
    content: '',
    recipients: {
      user_ids: [],
      section_ids: [],
      all_members: false
    }
  });

  useEffect(() => {
    fetchThreads();
    fetchComposeOptions();
    // TODO: Check if user is admin
    setIsAdmin(true);
  }, []);

  useEffect(() => {
    if (selectedThread) {
      fetchMessages(selectedThread.id);
    }
  }, [selectedThread]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchThreads = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/messages/threads', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setThreads(data);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch message threads' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading threads' });
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (threadId) => {
    setMessagesLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/messages/threads/${threadId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch messages' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading messages' });
    } finally {
      setMessagesLoading(false);
    }
  };

  const fetchComposeOptions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/messages/compose', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
        // setSections(data.sections); // Future use
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Failed to fetch compose options' });
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !selectedThread) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/messages/threads/${selectedThread.id}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: newMessage })
      });
      
      if (response.ok) {
        setNewMessage('');
        fetchMessages(selectedThread.id);
        fetchThreads(); // Refresh threads to update last message
      } else {
        setToast({ type: 'error', message: 'Failed to send message' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error sending message' });
    }
  };

  const handleCreateThread = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/messages/threads', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newThreadForm)
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Message thread created successfully' });
        setShowNewMessageModal(false);
        setNewThreadForm({ subject: '', participants: [], initial_message: '' });
        fetchThreads();
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to create thread' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error creating thread' });
    }
  };

  const handleBroadcast = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/messages/broadcast', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(broadcastForm)
      });
      
      if (response.ok) {
        const data = await response.json();
        setToast({ type: 'success', message: data.message });
        setShowBroadcastModal(false);
        setBroadcastForm({ 
          subject: '', 
          content: '', 
          recipients: { user_ids: [], section_ids: [], all_members: false } 
        });
        fetchThreads();
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to send broadcast' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error sending broadcast' });
    }
  };

  const handleParticipantToggle = (userId) => {
    setNewThreadForm(prev => ({
      ...prev,
      participants: prev.participants.includes(userId)
        ? prev.participants.filter(id => id !== userId)
        : [...prev.participants, userId]
    }));
  };

  const handleBroadcastUserToggle = (userId) => {
    setBroadcastForm(prev => ({
      ...prev,
      recipients: {
        ...prev.recipients,
        user_ids: prev.recipients.user_ids.includes(userId)
          ? prev.recipients.user_ids.filter(id => id !== userId)
          : [...prev.recipients.user_ids, userId]
      }
    }));
  };

  const filteredThreads = threads.filter(thread =>
    thread.subject.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <Spinner color="primary" />
        <p className="mt-2">Loading messages...</p>
      </div>
    );
  }

  return (
    <div className="internal-messaging">
      <Card className="h-100">
        <CardHeader>
          <CardTitle className="d-flex justify-content-between align-items-center">
            <span><FaEnvelope className="me-2" />Internal Messages</span>
            <div>
              <Button 
                color="primary" 
                size="sm" 
                className="me-2"
                onClick={() => setShowNewMessageModal(true)}
              >
                <FaPlus className="me-1" />New Message
              </Button>
              {isAdmin && (
                <Button 
                  color="info" 
                  size="sm"
                  onClick={() => setShowBroadcastModal(true)}
                >
                  <FaUsers className="me-1" />Broadcast
                </Button>
              )}
            </div>
          </CardTitle>
        </CardHeader>
        <CardBody className="p-0">
          <Row className="g-0 h-100">
            {/* Threads List */}
            <Col md="4" className="border-end">
              <div className="p-3 border-bottom">
                <FormGroup className="mb-0">
                  <Input
                    type="text"
                    placeholder="Search messages..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </FormGroup>
              </div>
              <div style={{ height: '400px', overflowY: 'auto' }}>
                <ListGroup flush>
                  {filteredThreads.map((thread) => (
                    <ListGroupItem
                      key={thread.id}
                      active={selectedThread?.id === thread.id}
                      action
                      onClick={() => setSelectedThread(thread)}
                      className="border-0"
                    >
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <h6 className="mb-1">{thread.subject}</h6>
                          <p className="mb-1 text-muted small">
                            {thread.last_message?.content || 'No messages yet'}
                          </p>
                          <small className="text-muted">
                            {thread.participant_count} participant{thread.participant_count !== 1 ? 's' : ''}
                          </small>
                        </div>
                        <div className="text-end">
                          <small className="text-muted">
                            {thread.last_message?.created_at ? formatMessageTime(thread.last_message.created_at) : ''}
                          </small>
                          {thread.unread_count > 0 && (
                            <Badge color="primary" className="ms-1">
                              {thread.unread_count}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </ListGroupItem>
                  ))}
                </ListGroup>
                {filteredThreads.length === 0 && (
                  <div className="text-center p-4 text-muted">
                    {searchTerm ? 'No messages found' : 'No messages yet'}
                  </div>
                )}
              </div>
            </Col>

            {/* Messages View */}
            <Col md="8">
              {selectedThread ? (
                <div className="d-flex flex-column h-100">
                  {/* Messages Header */}
                  <div className="p-3 border-bottom">
                    <h6 className="mb-1">{selectedThread.subject}</h6>
                    <small className="text-muted">
                      {selectedThread.participant_count} participant{selectedThread.participant_count !== 1 ? 's' : ''}
                    </small>
                  </div>

                  {/* Messages List */}
                  <div className="flex-grow-1 p-3" style={{ height: '300px', overflowY: 'auto' }}>
                    {messagesLoading ? (
                      <div className="text-center">
                        <Spinner color="primary" size="sm" />
                      </div>
                    ) : (
                      <div>
                        {messages.map((message) => (
                          <div key={message.id} className="mb-3">
                            <div className="d-flex justify-content-between align-items-start">
                              <strong>{message.sender.name}</strong>
                              <small className="text-muted">
                                {formatMessageTime(message.created_at)}
                              </small>
                            </div>
                            <div className="mt-1">
                              {message.content}
                            </div>
                          </div>
                        ))}
                        <div ref={messagesEndRef} />
                      </div>
                    )}
                  </div>

                  {/* Message Input */}
                  <div className="p-3 border-top">
                    <Form onSubmit={handleSendMessage}>
                      <FormGroup className="mb-0">
                        <div className="input-group">
                          <Input
                            type="textarea"
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            placeholder="Type your message..."
                            rows={2}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSendMessage(e);
                              }
                            }}
                          />
                          <Button type="submit" color="primary" disabled={!newMessage.trim()}>
                            <FaPaperPlane />
                          </Button>
                        </div>
                      </FormGroup>
                    </Form>
                  </div>
                </div>
              ) : (
                <div className="text-center p-5 text-muted">
                  <FaEnvelope size={48} className="mb-3" />
                  <h5>Select a conversation</h5>
                  <p>Choose a message thread to view your conversation</p>
                </div>
              )}
            </Col>
          </Row>
        </CardBody>
      </Card>

      {/* New Message Modal */}
      <Modal isOpen={showNewMessageModal} toggle={() => setShowNewMessageModal(false)}>
        <Form onSubmit={handleCreateThread}>
          <ModalHeader toggle={() => setShowNewMessageModal(false)}>
            New Message
          </ModalHeader>
          <ModalBody>
            <FormGroup>
              <Input
                type="text"
                placeholder="Subject"
                value={newThreadForm.subject}
                onChange={(e) => setNewThreadForm({...newThreadForm, subject: e.target.value})}
                required
              />
            </FormGroup>
            
            <FormGroup>
              <label>Recipients</label>
              <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #dee2e6', padding: '10px' }}>
                {users.map(user => (
                  <div key={user.id} className="form-check">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={newThreadForm.participants.includes(user.id)}
                      onChange={() => handleParticipantToggle(user.id)}
                    />
                    <label className="form-check-label">
                      {user.name} ({user.email})
                    </label>
                  </div>
                ))}
              </div>
            </FormGroup>
            
            <FormGroup>
              <Input
                type="textarea"
                placeholder="Your message..."
                value={newThreadForm.initial_message}
                onChange={(e) => setNewThreadForm({...newThreadForm, initial_message: e.target.value})}
                rows={4}
                required
              />
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={() => setShowNewMessageModal(false)}>
              Cancel
            </Button>
            <Button color="primary" type="submit">
              Send Message
            </Button>
          </ModalFooter>
        </Form>
      </Modal>

      {/* Broadcast Modal */}
      <Modal isOpen={showBroadcastModal} toggle={() => setShowBroadcastModal(false)}>
        <Form onSubmit={handleBroadcast}>
          <ModalHeader toggle={() => setShowBroadcastModal(false)}>
            Broadcast Message
          </ModalHeader>
          <ModalBody>
            <FormGroup>
              <Input
                type="text"
                placeholder="Subject"
                value={broadcastForm.subject}
                onChange={(e) => setBroadcastForm({...broadcastForm, subject: e.target.value})}
                required
              />
            </FormGroup>
            
            <FormGroup>
              <label>Recipients</label>
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  checked={broadcastForm.recipients.all_members}
                  onChange={(e) => setBroadcastForm({
                    ...broadcastForm,
                    recipients: {...broadcastForm.recipients, all_members: e.target.checked}
                  })}
                />
                <label className="form-check-label">
                  <strong>All Organization Members</strong>
                </label>
              </div>
              {!broadcastForm.recipients.all_members && (
                <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #dee2e6', padding: '10px', marginTop: '10px' }}>
                  {users.map(user => (
                    <div key={user.id} className="form-check">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        checked={broadcastForm.recipients.user_ids.includes(user.id)}
                        onChange={() => handleBroadcastUserToggle(user.id)}
                      />
                      <label className="form-check-label">
                        {user.name} ({user.email})
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </FormGroup>
            
            <FormGroup>
              <Input
                type="textarea"
                placeholder="Your message..."
                value={broadcastForm.content}
                onChange={(e) => setBroadcastForm({...broadcastForm, content: e.target.value})}
                rows={4}
                required
              />
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={() => setShowBroadcastModal(false)}>
              Cancel
            </Button>
            <Button color="primary" type="submit">
              Send Broadcast
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

export default InternalMessaging;
