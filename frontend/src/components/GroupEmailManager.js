import React, { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader, CardTitle } from 'reactstrap';
import { 
  Button, 
  Form, 
  FormGroup, 
  Label, 
  Input, 
  Table, 
  Badge, 
  Alert,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Spinner
} from 'reactstrap';
import { FaPlus, FaTrash, FaEnvelope, FaCog } from 'react-icons/fa';
import Toast from './Toast';

const GroupEmailManager = () => {
  const [aliases, setAliases] = useState([]);
  const [forwardingRules, setForwardingRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showRulesModal, setShowRulesModal] = useState(false);
  const [selectedAlias, setSelectedAlias] = useState(null);
  const [toast, setToast] = useState(null);
  const [formData, setFormData] = useState({
    alias_name: '',
    description: '',
    is_active: true
  });
  const [ruleFormData, setRuleFormData] = useState({
    forward_to_type: 'all_members',
    target_section_id: '',
    target_user_id: ''
  });

  useEffect(() => {
    fetchAliases();
  }, []);

  const fetchAliases = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/email-management/aliases', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAliases(data);
      } else {
        setToast({ type: 'error', message: 'Failed to fetch email aliases' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error loading aliases' });
    } finally {
      setLoading(false);
    }
  };

  const fetchForwardingRules = async (aliasId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/email-management/aliases/${aliasId}/forwarding-rules`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setForwardingRules(data);
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Failed to fetch forwarding rules' });
    }
  };

  const handleCreateAlias = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/email-management/aliases', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Email alias created successfully' });
        setShowCreateModal(false);
        setFormData({ alias_name: '', description: '', is_active: true });
        fetchAliases();
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to create alias' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error creating alias' });
    }
  };

  const handleDeleteAlias = async (aliasId) => {
    if (!window.confirm('Are you sure you want to delete this email alias?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/email-management/aliases/${aliasId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Email alias deleted successfully' });
        fetchAliases();
      } else {
        setToast({ type: 'error', message: 'Failed to delete alias' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error deleting alias' });
    }
  };

  const handleToggleAlias = async (aliasId, currentStatus) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/email-management/aliases/${aliasId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: !currentStatus })
      });
      
      if (response.ok) {
        setToast({ 
          type: 'success', 
          message: `Email alias ${!currentStatus ? 'enabled' : 'disabled'} successfully` 
        });
        fetchAliases();
      } else {
        setToast({ type: 'error', message: 'Failed to update alias' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error updating alias' });
    }
  };

  const handleManageRules = (alias) => {
    setSelectedAlias(alias);
    fetchForwardingRules(alias.id);
    setShowRulesModal(true);
  };

  const handleCreateRule = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/email-management/aliases/${selectedAlias.id}/forwarding-rules`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(ruleFormData)
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Forwarding rule created successfully' });
        setRuleFormData({ forward_to_type: 'all_members', target_section_id: '', target_user_id: '' });
        fetchForwardingRules(selectedAlias.id);
      } else {
        const error = await response.json();
        setToast({ type: 'error', message: error.error || 'Failed to create rule' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error creating rule' });
    }
  };

  const handleDeleteRule = async (ruleId) => {
    if (!window.confirm('Are you sure you want to delete this forwarding rule?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/email-management/forwarding-rules/${ruleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setToast({ type: 'success', message: 'Forwarding rule deleted successfully' });
        fetchForwardingRules(selectedAlias.id);
      } else {
        setToast({ type: 'error', message: 'Failed to delete rule' });
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Network error deleting rule' });
    }
  };

  if (loading) {
    return (
      <div className="text-center p-4">
        <Spinner color="primary" />
        <p className="mt-2">Loading email aliases...</p>
      </div>
    );
  }

  return (
    <div className="group-email-manager">
      <Card>
        <CardHeader>
          <CardTitle className="d-flex justify-content-between align-items-center">
            <span><FaEnvelope className="me-2" />Group Email Management</span>
            <Button color="primary" onClick={() => setShowCreateModal(true)}>
              <FaPlus className="me-2" />New Email Alias
            </Button>
          </CardTitle>
        </CardHeader>
        <CardBody>
          {aliases.length === 0 ? (
            <Alert color="info">
              No email aliases configured. Create your first group email address to get started.
            </Alert>
          ) : (
            <Table responsive>
              <thead>
                <tr>
                  <th>Email Address</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {aliases.map((alias) => (
                  <tr key={alias.id}>
                    <td>
                      <strong>{alias.alias_name}@bandsync.com</strong>
                    </td>
                    <td>{alias.description}</td>
                    <td>
                      <Badge color={alias.is_active ? 'success' : 'secondary'}>
                        {alias.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td>{new Date(alias.created_at).toLocaleDateString()}</td>
                    <td>
                      <Button 
                        size="sm" 
                        color="info" 
                        className="me-2"
                        onClick={() => handleManageRules(alias)}
                      >
                        <FaCog />
                      </Button>
                      <Button 
                        size="sm" 
                        color={alias.is_active ? 'warning' : 'success'}
                        className="me-2"
                        onClick={() => handleToggleAlias(alias.id, alias.is_active)}
                      >
                        {alias.is_active ? 'Disable' : 'Enable'}
                      </Button>
                      <Button 
                        size="sm" 
                        color="danger"
                        onClick={() => handleDeleteAlias(alias.id)}
                      >
                        <FaTrash />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </CardBody>
      </Card>

      {/* Create Alias Modal */}
      <Modal isOpen={showCreateModal} toggle={() => setShowCreateModal(false)}>
        <ModalHeader toggle={() => setShowCreateModal(false)}>
          Create New Email Alias
        </ModalHeader>
        <Form onSubmit={handleCreateAlias}>
          <ModalBody>
            <FormGroup>
              <Label for="alias_name">Email Alias Name</Label>
              <div className="input-group">
                <Input
                  type="text"
                  id="alias_name"
                  value={formData.alias_name}
                  onChange={(e) => setFormData({ ...formData, alias_name: e.target.value })}
                  required
                  placeholder="yourband"
                />
                <span className="input-group-text">@bandsync.com</span>
              </div>
              <small className="form-text text-muted">
                Choose a unique name for your organization's email address
              </small>
            </FormGroup>
            
            <FormGroup>
              <Label for="description">Description</Label>
              <Input
                type="textarea"
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief description of this email alias"
                rows={3}
              />
            </FormGroup>
            
            <FormGroup check>
              <Input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              />
              <Label check for="is_active">
                Active (emails will be processed)
              </Label>
            </FormGroup>
          </ModalBody>
          <ModalFooter>
            <Button color="secondary" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button color="primary" type="submit">
              Create Alias
            </Button>
          </ModalFooter>
        </Form>
      </Modal>

      {/* Forwarding Rules Modal */}
      <Modal isOpen={showRulesModal} toggle={() => setShowRulesModal(false)} size="lg">
        <ModalHeader toggle={() => setShowRulesModal(false)}>
          Manage Forwarding Rules - {selectedAlias?.alias_name}@bandsync.com
        </ModalHeader>
        <ModalBody>
          <div className="mb-4">
            <h6>Create New Forwarding Rule</h6>
            <Form onSubmit={handleCreateRule}>
              <FormGroup>
                <Label for="forward_to_type">Forward To</Label>
                <Input
                  type="select"
                  id="forward_to_type"
                  value={ruleFormData.forward_to_type}
                  onChange={(e) => setRuleFormData({ ...ruleFormData, forward_to_type: e.target.value })}
                >
                  <option value="all_members">All Organization Members</option>
                  <option value="admins">Admins Only</option>
                  <option value="section">Specific Section</option>
                  <option value="user">Specific User</option>
                </Input>
              </FormGroup>
              
              {ruleFormData.forward_to_type === 'section' && (
                <FormGroup>
                  <Label for="target_section_id">Target Section</Label>
                  <Input
                    type="select"
                    id="target_section_id"
                    value={ruleFormData.target_section_id}
                    onChange={(e) => setRuleFormData({ ...ruleFormData, target_section_id: e.target.value })}
                  >
                    <option value="">Select a section...</option>
                    {/* TODO: Populate with actual sections */}
                  </Input>
                </FormGroup>
              )}
              
              {ruleFormData.forward_to_type === 'user' && (
                <FormGroup>
                  <Label for="target_user_id">Target User</Label>
                  <Input
                    type="select"
                    id="target_user_id"
                    value={ruleFormData.target_user_id}
                    onChange={(e) => setRuleFormData({ ...ruleFormData, target_user_id: e.target.value })}
                  >
                    <option value="">Select a user...</option>
                    {/* TODO: Populate with actual users */}
                  </Input>
                </FormGroup>
              )}
              
              <Button color="primary" type="submit" size="sm">
                Add Rule
              </Button>
            </Form>
          </div>
          
          <hr />
          
          <div>
            <h6>Existing Forwarding Rules</h6>
            {forwardingRules.length === 0 ? (
              <Alert color="info">
                No forwarding rules configured. All emails will be forwarded to all members by default.
              </Alert>
            ) : (
              <Table size="sm">
                <thead>
                  <tr>
                    <th>Forward To</th>
                    <th>Target</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {forwardingRules.map((rule) => (
                    <tr key={rule.id}>
                      <td>{rule.forward_to_type.replace('_', ' ').toUpperCase()}</td>
                      <td>{rule.target_name || 'N/A'}</td>
                      <td>
                        <Badge color={rule.is_active ? 'success' : 'secondary'}>
                          {rule.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td>
                        <Button 
                          size="sm" 
                          color="danger"
                          onClick={() => handleDeleteRule(rule.id)}
                        >
                          <FaTrash />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </div>
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={() => setShowRulesModal(false)}>
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

export default GroupEmailManager;
