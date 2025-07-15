import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Spinner, Badge } from 'react-bootstrap';
import axios from 'axios';
import { getApiUrl } from '../utils/apiUrl';

const CustomFields = ({ eventId, isAdmin = false }) => {
  const [fields, setFields] = useState([]);
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'success' });
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newField, setNewField] = useState({
    field_name: '',
    field_type: 'text',
    field_description: '',
    required: false,
    field_options: []
  });

  useEffect(() => {
    loadFields();
    if (!isAdmin) {
      loadResponses();
    }
  }, [eventId, isAdmin]);

  const loadFields = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${getApiUrl()}/events/${eventId}/custom-fields`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFields(response.data);
    } catch (error) {
      console.error('Error loading fields:', error);
      setAlert({ show: true, message: 'Failed to load custom fields', type: 'danger' });
    } finally {
      setLoading(false);
    }
  };

  const loadResponses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${getApiUrl()}/events/${eventId}/field-responses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResponses(response.data);
    } catch (error) {
      console.error('Error loading responses:', error);
    }
  };

  const handleResponseChange = (fieldId, value) => {
    setResponses(prev => ({
      ...prev,
      [fieldId]: value
    }));
  };

  const handleSubmitResponses = async () => {
    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${getApiUrl()}/events/${eventId}/field-responses`, {
        responses: responses
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlert({ show: true, message: 'Responses submitted successfully', type: 'success' });
    } catch (error) {
      console.error('Error submitting responses:', error);
      setAlert({ show: true, message: 'Failed to submit responses', type: 'danger' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateField = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${getApiUrl()}/events/${eventId}/custom-fields`, newField, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlert({ show: true, message: 'Field created successfully', type: 'success' });
      setShowCreateForm(false);
      setNewField({
        field_name: '',
        field_type: 'text',
        field_description: '',
        required: false,
        field_options: []
      });
      loadFields();
    } catch (error) {
      console.error('Error creating field:', error);
      setAlert({ show: true, message: 'Failed to create field', type: 'danger' });
    }
  };

  const handleDeleteField = async (fieldId) => {
    if (!window.confirm('Are you sure you want to delete this field?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${getApiUrl()}/events/${eventId}/custom-fields/${fieldId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlert({ show: true, message: 'Field deleted successfully', type: 'success' });
      loadFields();
    } catch (error) {
      console.error('Error deleting field:', error);
      setAlert({ show: true, message: 'Failed to delete field', type: 'danger' });
    }
  };

  const renderField = (field) => {
    const fieldId = field.id;
    const value = responses[fieldId] || '';

    switch (field.field_type) {
      case 'text':
      case 'email':
      case 'phone':
        return (
          <Form.Control
            type={field.field_type === 'email' ? 'email' : field.field_type === 'phone' ? 'tel' : 'text'}
            value={value}
            onChange={(e) => handleResponseChange(fieldId, e.target.value)}
            required={field.required}
            placeholder={field.field_description}
          />
        );
      
      case 'number':
        return (
          <Form.Control
            type="number"
            value={value}
            onChange={(e) => handleResponseChange(fieldId, e.target.value)}
            required={field.required}
            placeholder={field.field_description}
          />
        );
      
      case 'textarea':
        return (
          <Form.Control
            as="textarea"
            rows={3}
            value={value}
            onChange={(e) => handleResponseChange(fieldId, e.target.value)}
            required={field.required}
            placeholder={field.field_description}
          />
        );
      
      case 'select':
        return (
          <Form.Select
            value={value}
            onChange={(e) => handleResponseChange(fieldId, e.target.value)}
            required={field.required}
          >
            <option value="">Select an option...</option>
            {field.field_options?.map((option, index) => (
              <option key={index} value={option}>{option}</option>
            ))}
          </Form.Select>
        );
      
      case 'checkbox':
        return (
          <div>
            {field.field_options?.map((option, index) => (
              <Form.Check
                key={index}
                type="checkbox"
                label={option}
                checked={value.includes && value.includes(option)}
                onChange={(e) => {
                  const currentValues = value.split(',').filter(v => v);
                  if (e.target.checked) {
                    currentValues.push(option);
                  } else {
                    const index = currentValues.indexOf(option);
                    if (index > -1) {
                      currentValues.splice(index, 1);
                    }
                  }
                  handleResponseChange(fieldId, currentValues.join(','));
                }}
              />
            ))}
          </div>
        );
      
      default:
        return <Form.Control value={value} onChange={(e) => handleResponseChange(fieldId, e.target.value)} />;
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center p-4">
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <div>
      {alert.show && (
        <Alert 
          variant={alert.type} 
          onClose={() => setAlert({ show: false, message: '', type: 'success' })} 
          dismissible
        >
          {alert.message}
        </Alert>
      )}

      {isAdmin && (
        <div className="mb-3">
          <Button 
            variant="outline-primary" 
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="mb-2"
          >
            {showCreateForm ? 'Cancel' : 'Add Custom Field'}
          </Button>

          {showCreateForm && (
            <Card>
              <Card.Body>
                <Form>
                  <Form.Group className="mb-3">
                    <Form.Label>Field Name</Form.Label>
                    <Form.Control
                      type="text"
                      value={newField.field_name}
                      onChange={(e) => setNewField({...newField, field_name: e.target.value})}
                      placeholder="e.g., Uniform Size"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Field Type</Form.Label>
                    <Form.Select
                      value={newField.field_type}
                      onChange={(e) => setNewField({...newField, field_type: e.target.value})}
                    >
                      <option value="text">Text</option>
                      <option value="textarea">Long Text</option>
                      <option value="select">Dropdown</option>
                      <option value="checkbox">Checkboxes</option>
                      <option value="number">Number</option>
                      <option value="email">Email</option>
                      <option value="phone">Phone</option>
                    </Form.Select>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>Description/Help Text</Form.Label>
                    <Form.Control
                      type="text"
                      value={newField.field_description}
                      onChange={(e) => setNewField({...newField, field_description: e.target.value})}
                      placeholder="Optional help text for users"
                    />
                  </Form.Group>

                  {(newField.field_type === 'select' || newField.field_type === 'checkbox') && (
                    <Form.Group className="mb-3">
                      <Form.Label>Options (one per line)</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        value={newField.field_options.join('\n')}
                        onChange={(e) => setNewField({...newField, field_options: e.target.value.split('\n').filter(opt => opt.trim())})}
                        placeholder="Option 1\nOption 2\nOption 3"
                      />
                    </Form.Group>
                  )}

                  <Form.Check
                    type="checkbox"
                    label="Required field"
                    checked={newField.required}
                    onChange={(e) => setNewField({...newField, required: e.target.checked})}
                    className="mb-3"
                  />

                  <Button variant="primary" onClick={handleCreateField}>
                    Create Field
                  </Button>
                </Form>
              </Card.Body>
            </Card>
          )}
        </div>
      )}

      {fields.length === 0 ? (
        <Alert variant="info">
          No custom fields for this event.
        </Alert>
      ) : (
        <Card>
          <Card.Header>
            <h6 className="mb-0">Event Information</h6>
          </Card.Header>
          <Card.Body>
            <Form>
              {fields.map(field => (
                <div key={field.id} className="mb-3">
                  <div className="d-flex justify-content-between align-items-center">
                    <Form.Label>
                      {field.field_name}
                      {field.required && <span className="text-danger ms-1">*</span>}
                    </Form.Label>
                    {isAdmin && (
                      <Button 
                        variant="outline-danger" 
                        size="sm"
                        onClick={() => handleDeleteField(field.id)}
                      >
                        Delete
                      </Button>
                    )}
                  </div>
                  {field.field_description && (
                    <Form.Text className="text-muted d-block mb-2">
                      {field.field_description}
                    </Form.Text>
                  )}
                  {renderField(field)}
                </div>
              ))}
              
              {!isAdmin && fields.length > 0 && (
                <div className="mt-4">
                  <Button 
                    variant="primary" 
                    onClick={handleSubmitResponses}
                    disabled={submitting}
                  >
                    {submitting ? <Spinner animation="border" size="sm" /> : 'Submit Information'}
                  </Button>
                </div>
              )}
            </Form>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default CustomFields;
