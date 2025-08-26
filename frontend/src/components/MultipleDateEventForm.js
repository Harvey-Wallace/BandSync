import React, { useState } from 'react';
import { Button, Card, CardBody, CardHeader, Form, FormGroup, Label, Input, Alert } from 'reactstrap';
import { Plus, Trash2, Calendar, Clock } from 'lucide-react';
import { getApiUrl } from '../utils/api';

const MultipleDateEventForm = ({ onClose, onEventCreated }) => {
  const [eventData, setEventData] = useState({
    title: '',
    description: '',
    type: 'Rehearsal',
    location_address: '',
    has_multiple_dates: false,
    date_selection_deadline: '',
    possible_dates: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const addPossibleDate = () => {
    setEventData(prev => ({
      ...prev,
      possible_dates: [...prev.possible_dates, {
        date: '',
        end_date: '',
        start_time: '',
        end_time: '',
        arrive_by_time: ''
      }]
    }));
  };

  const removePossibleDate = (index) => {
    setEventData(prev => ({
      ...prev,
      possible_dates: prev.possible_dates.filter((_, i) => i !== index)
    }));
  };

  const updatePossibleDate = (index, field, value) => {
    setEventData(prev => ({
      ...prev,
      possible_dates: prev.possible_dates.map((date, i) => 
        i === index ? { ...date, [field]: value } : date
      )
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      
      const submitData = { ...eventData };
      
      // Convert single date mode to regular event
      if (!eventData.has_multiple_dates) {
        if (eventData.possible_dates.length > 0) {
          const singleDate = eventData.possible_dates[0];
          submitData.date = singleDate.date;
          submitData.end_date = singleDate.end_date;
          submitData.start_time = singleDate.start_time;
          submitData.end_time = singleDate.end_time;
          submitData.arrive_by_time = singleDate.arrive_by_time;
        }
        delete submitData.possible_dates;
        delete submitData.date_selection_deadline;
      }

      const response = await fetch(`${getApiUrl()}/events/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(submitData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create event');
      }

      const result = await response.json();
      setSuccess(`Event "${eventData.title}" created successfully!`);
      
      if (onEventCreated) {
        onEventCreated(result);
      }
      
      // Reset form
      setTimeout(() => {
        setEventData({
          title: '',
          description: '',
          type: 'Rehearsal',
          location_address: '',
          has_multiple_dates: false,
          date_selection_deadline: '',
          possible_dates: []
        });
        if (onClose) onClose();
      }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <h5 className="mb-0">
          <Calendar className="me-2" size={20} />
          Create Event with Multiple Date Options
        </h5>
      </CardHeader>
      <CardBody>
        {error && <Alert color="danger">{error}</Alert>}
        {success && <Alert color="success">{success}</Alert>}
        
        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <Label for="title">Event Title</Label>
            <Input
              id="title"
              type="text"
              value={eventData.title}
              onChange={(e) => setEventData(prev => ({ ...prev, title: e.target.value }))}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label for="description">Description</Label>
            <Input
              id="description"
              type="textarea"
              value={eventData.description}
              onChange={(e) => setEventData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
            />
          </FormGroup>

          <FormGroup>
            <Label for="type">Event Type</Label>
            <Input
              id="type"
              type="select"
              value={eventData.type}
              onChange={(e) => setEventData(prev => ({ ...prev, type: e.target.value }))}
            >
              <option value="Rehearsal">Rehearsal</option>
              <option value="Performance">Performance</option>
              <option value="Meeting">Meeting</option>
              <option value="Social">Social Event</option>
            </Input>
          </FormGroup>

          <FormGroup>
            <Label for="location">Location</Label>
            <Input
              id="location"
              type="text"
              value={eventData.location_address}
              onChange={(e) => setEventData(prev => ({ ...prev, location_address: e.target.value }))}
            />
          </FormGroup>

          <FormGroup check className="mb-3">
            <Input
              id="has_multiple_dates"
              type="checkbox"
              checked={eventData.has_multiple_dates}
              onChange={(e) => setEventData(prev => ({ 
                ...prev, 
                has_multiple_dates: e.target.checked,
                possible_dates: e.target.checked ? (prev.possible_dates.length === 0 ? [{}] : prev.possible_dates) : []
              }))}
            />
            <Label check for="has_multiple_dates">
              This event has multiple possible dates (members will vote)
            </Label>
          </FormGroup>

          {eventData.has_multiple_dates && (
            <>
              <FormGroup>
                <Label for="deadline">Date Selection Deadline</Label>
                <Input
                  id="deadline"
                  type="datetime-local"
                  value={eventData.date_selection_deadline}
                  onChange={(e) => setEventData(prev => ({ ...prev, date_selection_deadline: e.target.value }))}
                />
                <small className="text-muted">When members must vote by</small>
              </FormGroup>

              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <Label className="fw-bold">Possible Dates</Label>
                  <Button type="button" color="primary" size="sm" onClick={addPossibleDate}>
                    <Plus size={16} className="me-1" />
                    Add Date Option
                  </Button>
                </div>

                {eventData.possible_dates.map((date, index) => (
                  <Card key={index} className="mb-2 border-secondary">
                    <CardBody className="p-3">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <h6 className="mb-0">Option {index + 1}</h6>
                        {eventData.possible_dates.length > 1 && (
                          <Button 
                            type="button" 
                            color="danger" 
                            size="sm" 
                            onClick={() => removePossibleDate(index)}
                          >
                            <Trash2 size={14} />
                          </Button>
                        )}
                      </div>
                      
                      <div className="row">
                        <div className="col-md-6">
                          <FormGroup>
                            <Label>Start Date & Time</Label>
                            <Input
                              type="datetime-local"
                              value={date.date || ''}
                              onChange={(e) => updatePossibleDate(index, 'date', e.target.value)}
                              required={eventData.has_multiple_dates}
                            />
                          </FormGroup>
                        </div>
                        <div className="col-md-6">
                          <FormGroup>
                            <Label>End Date & Time</Label>
                            <Input
                              type="datetime-local"
                              value={date.end_date || ''}
                              onChange={(e) => updatePossibleDate(index, 'end_date', e.target.value)}
                            />
                          </FormGroup>
                        </div>
                      </div>
                      
                      <div className="row">
                        <div className="col-md-4">
                          <FormGroup>
                            <Label>Arrive By</Label>
                            <Input
                              type="time"
                              value={date.arrive_by_time || ''}
                              onChange={(e) => updatePossibleDate(index, 'arrive_by_time', e.target.value)}
                            />
                          </FormGroup>
                        </div>
                        <div className="col-md-4">
                          <FormGroup>
                            <Label>Start Time</Label>
                            <Input
                              type="time"
                              value={date.start_time || ''}
                              onChange={(e) => updatePossibleDate(index, 'start_time', e.target.value)}
                            />
                          </FormGroup>
                        </div>
                        <div className="col-md-4">
                          <FormGroup>
                            <Label>End Time</Label>
                            <Input
                              type="time"
                              value={date.end_time || ''}
                              onChange={(e) => updatePossibleDate(index, 'end_time', e.target.value)}
                            />
                          </FormGroup>
                        </div>
                      </div>
                    </CardBody>
                  </Card>
                ))}

                {eventData.possible_dates.length === 0 && (
                  <Alert color="info" className="text-center">
                    <Clock size={20} className="me-2" />
                    Click "Add Date Option" to add possible dates for this event
                  </Alert>
                )}
              </div>
            </>
          )}

          {!eventData.has_multiple_dates && (
            <div className="mb-3">
              <Label className="fw-bold">Event Date & Time</Label>
              {eventData.possible_dates.length === 0 && (
                <Button type="button" color="primary" size="sm" onClick={addPossibleDate} className="d-block mb-2">
                  <Plus size={16} className="me-1" />
                  Set Date & Time
                </Button>
              )}
              
              {eventData.possible_dates.length > 0 && (
                <Card className="border-secondary">
                  <CardBody className="p-3">
                    <div className="row">
                      <div className="col-md-6">
                        <FormGroup>
                          <Label>Start Date & Time</Label>
                          <Input
                            type="datetime-local"
                            value={eventData.possible_dates[0]?.date || ''}
                            onChange={(e) => updatePossibleDate(0, 'date', e.target.value)}
                            required
                          />
                        </FormGroup>
                      </div>
                      <div className="col-md-6">
                        <FormGroup>
                          <Label>End Date & Time</Label>
                          <Input
                            type="datetime-local"
                            value={eventData.possible_dates[0]?.end_date || ''}
                            onChange={(e) => updatePossibleDate(0, 'end_date', e.target.value)}
                          />
                        </FormGroup>
                      </div>
                    </div>
                    
                    <div className="row">
                      <div className="col-md-4">
                        <FormGroup>
                          <Label>Arrive By</Label>
                          <Input
                            type="time"
                            value={eventData.possible_dates[0]?.arrive_by_time || ''}
                            onChange={(e) => updatePossibleDate(0, 'arrive_by_time', e.target.value)}
                          />
                        </FormGroup>
                      </div>
                      <div className="col-md-4">
                        <FormGroup>
                          <Label>Start Time</Label>
                          <Input
                            type="time"
                            value={eventData.possible_dates[0]?.start_time || ''}
                            onChange={(e) => updatePossibleDate(0, 'start_time', e.target.value)}
                          />
                        </FormGroup>
                      </div>
                      <div className="col-md-4">
                        <FormGroup>
                          <Label>End Time</Label>
                          <Input
                            type="time"
                            value={eventData.possible_dates[0]?.end_time || ''}
                            onChange={(e) => updatePossibleDate(0, 'end_time', e.target.value)}
                          />
                        </FormGroup>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          )}

          <div className="d-flex justify-content-end gap-2">
            {onClose && (
              <Button type="button" color="secondary" onClick={onClose}>
                Cancel
              </Button>
            )}
            <Button type="submit" color="primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Event'}
            </Button>
          </div>
        </Form>
      </CardBody>
    </Card>
  );
};

export default MultipleDateEventForm;
