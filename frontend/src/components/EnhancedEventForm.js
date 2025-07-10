import React, { useState, useEffect } from 'react';
import { Modal, Form, Button, Alert, Spinner, Tab, Tabs, Card, Row, Col } from 'react-bootstrap';
import CustomFields from './CustomFields';
import axios from 'axios';

const EnhancedEventForm = ({ show, onHide, onSave, event = null, categories = [] }) => {
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'success' });
  const [activeTab, setActiveTab] = useState('basic');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: '',
    end_date: '',
    location_address: '',
    category_id: '',
    is_template: false,
    template_name: '',
    send_reminders: true,
    reminder_days_before: 1
  });

  useEffect(() => {
    if (event) {
      setFormData({
        title: event.title || '',
        description: event.description || '',
        date: event.date ? new Date(event.date).toISOString().slice(0, 16) : '',
        end_date: event.end_date ? new Date(event.end_date).toISOString().slice(0, 16) : '',
        location_address: event.location_address || '',
        category_id: event.category_id || '',
        is_template: event.is_template || false,
        template_name: event.template_name || '',
        send_reminders: event.send_reminders !== undefined ? event.send_reminders : true,
        reminder_days_before: event.reminder_days_before || 1
      });
    } else {
      setFormData({
        title: '',
        description: '',
        date: '',
        end_date: '',
        location_address: '',
        category_id: '',
        is_template: false,
        template_name: '',
        send_reminders: true,
        reminder_days_before: 1
      });
    }
  }, [event]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAlert({ show: false, message: '', type: 'success' });

    try {
      // Validate required fields
      if (!formData.title.trim()) {
        setAlert({ show: true, message: 'Event title is required', type: 'danger' });
        setLoading(false);
        return;
      }

      if (!formData.is_template && !formData.date) {
        setAlert({ show: true, message: 'Event date is required', type: 'danger' });
        setLoading(false);
        return;
      }

      // Format data for API
      const eventData = {
        ...formData,
        date: formData.date ? new Date(formData.date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null,
        category_id: formData.category_id || null
      };

      await onSave(eventData);
      onHide();
    } catch (error) {
      console.error('Error saving event:', error);
      setAlert({ 
        show: true, 
        message: error.response?.data?.error || 'Failed to save event', 
        type: 'danger' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setAlert({ show: false, message: '', type: 'success' });
    onHide();
  };

  return (
    <Modal show={show} onHide={handleClose} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>{event ? 'Edit Event' : 'Create New Event'}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {alert.show && (
          <Alert variant={alert.type} onClose={() => setAlert({ show: false, message: '', type: 'success' })} dismissible>
            {alert.message}
          </Alert>
        )}

        <Tabs activeKey={activeTab} onSelect={setActiveTab} className="mb-3">
          <Tab eventKey="basic" title="Basic Info">
            <Form onSubmit={handleSubmit}>
              <Row>
                <Col md={8}>
                  <Form.Group className="mb-3">
                    <Form.Label>Event Title *</Form.Label>
                    <Form.Control
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      required
                      placeholder="Enter event title"
                    />
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Category</Form.Label>
                    <Form.Select
                      name="category_id"
                      value={formData.category_id}
                      onChange={handleInputChange}
                    >
                      <option value="">Select category...</option>
                      {categories.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>

              <Form.Group className="mb-3">
                <Form.Label>Description</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Enter event description"
                />
              </Form.Group>

              <Form.Check
                type="checkbox"
                label="Save as template (no specific date)"
                name="is_template"
                checked={formData.is_template}
                onChange={handleInputChange}
                className="mb-3"
              />

              {formData.is_template && (
                <Form.Group className="mb-3">
                  <Form.Label>Template Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="template_name"
                    value={formData.template_name}
                    onChange={handleInputChange}
                    placeholder="Enter template name"
                  />
                </Form.Group>
              )}

              {!formData.is_template && (
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Start Date & Time *</Form.Label>
                      <Form.Control
                        type="datetime-local"
                        name="date"
                        value={formData.date}
                        onChange={handleInputChange}
                        required
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>End Date & Time</Form.Label>
                      <Form.Control
                        type="datetime-local"
                        name="end_date"
                        value={formData.end_date}
                        onChange={handleInputChange}
                      />
                    </Form.Group>
                  </Col>
                </Row>
              )}

              <Form.Group className="mb-3">
                <Form.Label>Location</Form.Label>
                <Form.Control
                  type="text"
                  name="location_address"
                  value={formData.location_address}
                  onChange={handleInputChange}
                  placeholder="Enter location address"
                />
              </Form.Group>

              <Card className="mb-3">
                <Card.Header>
                  <h6 className="mb-0">Notification Settings</h6>
                </Card.Header>
                <Card.Body>
                  <Form.Check
                    type="checkbox"
                    label="Send reminder notifications"
                    name="send_reminders"
                    checked={formData.send_reminders}
                    onChange={handleInputChange}
                    className="mb-3"
                  />

                  {formData.send_reminders && (
                    <Form.Group className="mb-3">
                      <Form.Label>Send reminder how many days before?</Form.Label>
                      <Form.Select
                        name="reminder_days_before"
                        value={formData.reminder_days_before}
                        onChange={handleInputChange}
                      >
                        <option value={1}>1 day before</option>
                        <option value={2}>2 days before</option>
                        <option value={3}>3 days before</option>
                        <option value={7}>1 week before</option>
                        <option value={14}>2 weeks before</option>
                      </Form.Select>
                    </Form.Group>
                  )}
                </Card.Body>
              </Card>
            </Form>
          </Tab>

          {event && (
            <Tab eventKey="custom-fields" title="Custom Fields">
              <CustomFields eventId={event.id} isAdmin={true} />
            </Tab>
          )}
        </Tabs>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? <Spinner animation="border" size="sm" /> : (event ? 'Update Event' : 'Create Event')}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default EnhancedEventForm;
