import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import EventForm from '../components/EventForm';
import { 
  LoadingSpinner, 
  DataLoadingState, 
  ErrorState, 
  EmptyState 
} from '../components/LoadingComponents';
import { 
  ResponsiveStatsGrid, 
  ResponsiveActionBar,
  ResponsiveButtonGroup,
  ResponsiveCardGrid 
} from '../components/ResponsiveComponents';
import axios from 'axios';
import { offlineManager, networkManager } from '../utils/offline';
import { getApiUrl } from '../utils/apiUrl';

function EventsPage() {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [editEvent, setEditEvent] = useState(null);
  const [role] = useState(localStorage.getItem('role'));
  const [rsvpSummary, setRsvpSummary] = useState({});
  const [rsvpLoading, setRsvpLoading] = useState(false);
  const [rsvpError, setRsvpError] = useState(null);
  const [openSummary, setOpenSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  // Enhanced notification functions
  const showSuccessMessage = (message) => {
    if (window.showSuccess) window.showSuccess(message);
  };

  const showErrorMessage = (message) => {
    if (window.showError) window.showError(message);
  };

  const showInfoMessage = (message) => {
    if (window.showInfo) window.showInfo(message);
  };

  const showWarningMessage = (message) => {
    if (window.showWarning) window.showWarning(message);
  };
  
  // New state for enhanced features
  const [categories, setCategories] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showTemplates, setShowTemplates] = useState(false);
  // const [showTemplateForm, setShowTemplateForm] = useState(false); // Future use
  const [substituteRequests, setSubstituteRequests] = useState({}); // Track substitute requests
  
  // Event cancellation state
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [eventToCancel, setEventToCancel] = useState(null);
  const [cancellationReason, setCancellationReason] = useState('');
  const [sendCancellationNotification, setSendCancellationNotification] = useState(true);
  const [cancelLoading, setCancelLoading] = useState(false);
  
  // Template usage state
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [templateDate, setTemplateDate] = useState('');
  const [templateLocation, setTemplateLocation] = useState('');
  const [templateLoading, setTemplateLoading] = useState(false);

  useEffect(() => {
    fetchEvents();
    fetchCategories();
    if (role === 'Admin') {
      fetchTemplates();
    }
    
    // Network status listener
    const handleNetworkChange = (status) => {
      setIsOnline(status === 'online');
      if (status === 'online') {
        // When back online, refresh events to get latest data
        fetchEvents();
      }
    };

    networkManager.addListener(handleNetworkChange);

    return () => {
      networkManager.removeListener(handleNetworkChange);
    };
  }, [role]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (role === 'Admin' && events.length) fetchRsvpSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events, role]);

  const fetchCategories = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${getApiUrl()}/events/categories`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCategories(res.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${getApiUrl()}/events/templates`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTemplates(res.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      let url = `${getApiUrl()}/events/`;
      
      // Add category filter if selected
      const params = new URLSearchParams();
      if (selectedCategory) {
        params.append('category_id', selectedCategory);
      }
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const res = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Sort events by date
      const sortedEvents = res.data.sort((a, b) => new Date(a.date) - new Date(b.date));
      setEvents(sortedEvents);
      
      // Load current user's RSVP status for each event
      const username = localStorage.getItem('username');
      const statusMap = {};
      for (const event of sortedEvents) {
        try {
          const rsvpRes = await axios.get(`${getApiUrl()}/events/${event.id}/rsvps`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          // Find user's RSVP status
          for (const [rsvpStatus, users] of Object.entries(rsvpRes.data)) {
            if (users.some(user => user.username === username)) {
              statusMap[event.id] = rsvpStatus;
              break;
            }
          }
        } catch (error) {
          console.error('Error loading RSVP status:', error);
        }
      }
      setStatus(statusMap);
    } catch (error) {
      showErrorMessage('Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  const fetchRsvpSummary = async () => {
    setRsvpLoading(true);
    setRsvpError(null);
    const token = localStorage.getItem('token');
    const summary = {};
    try {
      for (const event of events) {
        const res = await axios.get(`${getApiUrl()}/events/${event.id}/rsvps`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        summary[event.id] = res.data;
      }
      setRsvpSummary(summary);
    } catch (err) {
      setRsvpError('Failed to load RSVP summary.');
    }
    setRsvpLoading(false);
  };

  const handleRsvp = async (eventId, rsvpStatus) => {
    const token = localStorage.getItem('token');
    const userId = localStorage.getItem('user_id');
    
    try {
      if (navigator.onLine) {
        // Online: send RSVP immediately
        await axios.post(`${getApiUrl()}/events/${eventId}/rsvp`, { status: rsvpStatus }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStatus({ ...status, [eventId]: rsvpStatus });
        showSuccessMessage(`RSVP set to ${rsvpStatus}`);
        if (role === 'Admin') fetchRsvpSummary();
      } else {
        // Offline: save RSVP locally
        const saved = await offlineManager.saveOfflineRSVP(eventId, userId, rsvpStatus);
        if (saved) {
          setStatus({ ...status, [eventId]: rsvpStatus });
          showWarningMessage(`RSVP set to ${rsvpStatus} (will sync when online)`);
        } else {
          showErrorMessage('Failed to save RSVP offline');
        }
      }
    } catch (error) {
      console.error('RSVP error:', error);
      showErrorMessage('Failed to RSVP');
    }
  };

  const handleCreate = async (data) => {
    const token = localStorage.getItem('token');
    try {
      await axios.post(`${getApiUrl()}/events/`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showSuccessMessage('Event created successfully');
      fetchEvents();
      setShowForm(false);
      if (role === 'Admin') fetchRsvpSummary();
    } catch {
      showErrorMessage('Failed to create event');
    }
  };

  const handleEdit = async (data) => {
    const token = localStorage.getItem('token');
    try {
      await axios.put(`${getApiUrl()}/events/${editEvent.id}`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      showSuccessMessage('Event updated successfully');
      fetchEvents();
      setEditEvent(null);
      setShowForm(false);
      if (role === 'Admin') fetchRsvpSummary();
    } catch {
      showErrorMessage('Failed to update event');
    }
  };

  const handleDelete = async (eventId) => {
    if (window.confirm('Are you sure you want to delete this event?')) {
      const token = localStorage.getItem('token');
      try {
        await axios.delete(`${getApiUrl()}/events/${eventId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        showSuccessMessage('Event deleted successfully');
        fetchEvents();
        if (role === 'Admin') fetchRsvpSummary();
      } catch {
        showErrorMessage('Failed to delete event');
      }
    }
  };

  const handleCancelEvent = async () => {
    if (!eventToCancel || !cancellationReason.trim()) {
      showErrorMessage('Please provide a reason for cancellation');
      return;
    }

    setCancelLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await axios.post(`${getApiUrl()}/events/${eventToCancel.id}/cancel`, {
        reason: cancellationReason.trim(),
        send_notification: sendCancellationNotification
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const { msg, notification_sent, notifications_count } = response.data;
      
      let successMessage = 'Event cancelled successfully';
      if (notification_sent && notifications_count > 0) {
        successMessage += ` - ${notifications_count} notification(s) sent`;
      }
      
      showSuccessMessage(successMessage);
      
      // Reset modal state
      setShowCancelModal(false);
      setEventToCancel(null);
      setCancellationReason('');
      setSendCancellationNotification(true);
      
      // Refresh events
      fetchEvents();
      if (role === 'Admin') fetchRsvpSummary();
      
    } catch (error) {
      const errorMessage = error.response?.data?.msg || 'Failed to cancel event';
      showErrorMessage(errorMessage);
    } finally {
      setCancelLoading(false);
    }
  };

  const openCancelModal = (event) => {
    setEventToCancel(event);
    setShowCancelModal(true);
    setCancellationReason('');
    setSendCancellationNotification(true);
  };

  const closeCancelModal = () => {
    setShowCancelModal(false);
    setEventToCancel(null);
    setCancellationReason('');
    setSendCancellationNotification(true);
  };

  // Template modal functions
  const openTemplateModal = (template) => {
    setSelectedTemplate(template);
    setTemplateDate('');
    setTemplateLocation('');
    setShowTemplateModal(true);
  };

  const closeTemplateModal = () => {
    setShowTemplateModal(false);
    setSelectedTemplate(null);
    setTemplateDate('');
    setTemplateLocation('');
  };

  const createEventFromTemplate = async () => {
    if (!selectedTemplate || !templateDate) {
      showErrorMessage('Please select a date for the event');
      return;
    }

    setTemplateLoading(true);
    try {
      const response = await axios.post(`${getApiUrl()}/events/from-template/${selectedTemplate.id}`, {
        date: templateDate,
        location_address: templateLocation,
        title: selectedTemplate.template_name || selectedTemplate.title
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      showSuccessMessage('Event created successfully from template!');
      closeTemplateModal();
      fetchEvents(); // Refresh events list
    } catch (error) {
      console.error('Error creating event from template:', error);
      showErrorMessage(error.response?.data?.error || 'Failed to create event from template');
    } finally {
      setTemplateLoading(false);
    }
  };

  const downloadEventRSVPPDF = async (event) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${getApiUrl()}/events/${event.id}/rsvp-report/pdf`, {
        headers: { 
          Authorization: `Bearer ${token}` 
        },
        responseType: 'blob'
      });

      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Create safe filename
      const safeTitle = event.title.replace(/[^a-zA-Z0-9\s\-_]/g, '');
      const date = new Date().toISOString().split('T')[0];
      link.download = `RSVP_Report_${safeTitle}_${date}.pdf`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      showSuccessMessage('PDF report downloaded successfully');
    } catch (error) {
      const errorMessage = error.response?.data?.msg || 'Failed to download PDF report';
      showErrorMessage(errorMessage);
    }
  };

  const handleCategoryFilter = (categoryId) => {
    setSelectedCategory(categoryId);
    // Trigger refetch when category changes
    setTimeout(() => {
      fetchEvents();
    }, 100);
  };

  // const handleCreateFromTemplate = async (templateId, eventData) => { // Future use
  //   const token = localStorage.getItem('token');
  //   try {
  //     await axios.post(`${getApiUrl()}/events/from-template/${templateId}`, eventData, {
  //       headers: { Authorization: `Bearer ${token}` }
  //     });
  //     showSuccessMessage('Event created from template successfully');
  //     fetchEvents();
  //     setShowTemplateForm(false);
  //     if (role === 'Admin') fetchRsvpSummary();
  //   } catch (error) {
  //     showErrorMessage('Failed to create event from template');
  //   }
  // };

  const exportRsvps = async (eventId, format = 'csv') => {
    const token = localStorage.getItem('token');
    try {
      const response = await axios.get(`${getApiUrl()}/events/${eventId}/export-rsvps?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `event_rsvps.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      showSuccessMessage(`RSVPs exported as ${format.toUpperCase()}`);
    } catch (error) {
      showErrorMessage('Failed to export RSVPs');
    }
  };

  const handleSubstituteRequest = async (eventId) => {
    const token = localStorage.getItem('token');
    try {
      await axios.post(`${getApiUrl()}/substitutes/request`, 
        { event_id: eventId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSubstituteRequests({ ...substituteRequests, [eventId]: true });
      showSuccessMessage('Substitute request sent');
    } catch (error) {
      console.error('Substitute request error:', error);
      showErrorMessage('Failed to request substitute');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Date not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'Time not set';
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getEventTypeIcon = (event) => {
    if (event.category && categories.length > 0) {
      const category = categories.find(cat => cat.id === event.category_id);
      if (category) {
        return <i className={`fas fa-${category.icon}`} style={{ color: category.color }}></i>;
      }
    }
    
    // Fallback to type-based icons
    const icons = {
      'performance': '🎵',
      'rehearsal': '🎼',
      'meeting': '💼',
      'social': '🎉',
      'other': '📅'
    };
    return icons[event.type] || icons['other'];
  };

  const getEventTypeBadge = (event) => {
    if (event.category && categories.length > 0) {
      const category = categories.find(cat => cat.id === event.category_id);
      if (category) {
        return { color: 'white', backgroundColor: category.color };
      }
    }
    
    // Fallback to type-based colors
    const colors = {
      'performance': 'danger',
      'rehearsal': 'primary',
      'meeting': 'warning',
      'social': 'success',
      'other': 'secondary'
    };
    return colors[event.type] || colors['other'];
  };

  const toggleSummary = (eventId) => {
    setOpenSummary(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  // Offline/Online status handler
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Sync local changes to server
      offlineManager.syncAll();
    };
    
    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (loading) {
    return (
      <div>
        <Navbar />
        <div className="d-flex justify-content-center mt-5">
          <LoadingSpinner size="md" />
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <div className="container mt-4">
        {/* Offline indicator */}
        {!isOnline && (
          <div className="alert alert-warning mb-3" role="alert">
            <i className="bi bi-wifi-off me-2"></i>
            <strong>You're offline.</strong> You can still view cached events and submit RSVPs, 
            which will sync automatically when you're back online.
          </div>
        )}
        
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Events</h2>
          {role === 'Admin' && (
            <div className="d-flex gap-2">
              <button 
                className="btn btn-outline-secondary"
                onClick={() => setShowTemplates(!showTemplates)}
              >
                <i className="bi bi-file-earmark me-2"></i>
                Templates
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setShowForm(true)}
              >
                <i className="bi bi-plus me-2"></i>
                Create Event
              </button>
            </div>
          )}
        </div>

        {/* Category Filter */}
        <div className="mb-4">
          <div className="d-flex align-items-center gap-3 flex-wrap">
            <label className="form-label mb-0">
              <i className="bi bi-funnel me-1"></i>
              Filter by Category:
            </label>
            <select 
              className="form-select" 
              style={{ width: 'auto' }}
              value={selectedCategory} 
              onChange={e => handleCategoryFilter(e.target.value)}
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            {selectedCategory && (
              <button 
                className="btn btn-sm btn-outline-secondary"
                onClick={() => handleCategoryFilter('')}
              >
                Clear Filter
              </button>
            )}
          </div>
        </div>

        {/* Templates Section */}
        {role === 'Admin' && showTemplates && (
          <div className="card mb-4">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="bi bi-file-earmark-text me-2"></i>
                Event Templates
              </h5>
            </div>
            <div className="card-body">
              {templates.length === 0 ? (
                <p className="text-muted">No templates found. Create an event and save it as a template.</p>
              ) : (
                <div className="row">
                  {templates.map(template => (
                    <div key={template.id} className="col-md-4 mb-3">
                      <div className="card">
                        <div className="card-body">
                          <h6 className="card-title">{template.template_name}</h6>
                          <p className="card-text small text-muted">{template.description}</p>
                          <span className="badge bg-secondary me-2">{template.category || 'No category'}</span>
                          <button 
                            className="btn btn-sm btn-primary"
                            onClick={() => openTemplateModal(template)}
                          >
                            Use Template
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {showForm && (
          <div className="card mb-4">
            <div className="card-header">
              <h5 className="mb-0">
                {editEvent ? 'Edit Event' : 'Create New Event'}
              </h5>
            </div>
            <div className="card-body">
              <EventForm
                initialData={editEvent}
                onSubmit={editEvent ? handleEdit : handleCreate}
                onCancel={() => {
                  setShowForm(false);
                  setEditEvent(null);
                }}
              />
            </div>
          </div>
        )}

        {events.length === 0 ? (
          <div className="text-center mt-5">
            <p className="text-muted">No events found</p>
          </div>
        ) : (
          <div className="row">
            {events.map(event => (
              <div key={event.id} className="col-md-6 col-lg-4 mb-4">
                <div className={`card h-100 ${event.is_cancelled ? 'border-danger' : ''}`}>
                  <div className="card-header d-flex justify-content-between align-items-center">
                    <div className="d-flex align-items-center">
                      <span className="me-2" style={{ fontSize: '1.2em' }}>
                        {getEventTypeIcon(event)}
                      </span>
                      <h6 className="mb-0">{event.title}</h6>
                      {event.is_recurring && (
                        <i className="bi bi-arrow-repeat ms-2 text-muted" title="Recurring Event"></i>
                      )}
                    </div>
                    <div>
                      {event.is_cancelled && (
                        <span className="badge bg-danger me-2">
                          <i className="bi bi-x-circle me-1"></i>
                          CANCELLED
                        </span>
                      )}
                      {event.category && (
                        <span 
                          className={typeof getEventTypeBadge(event) === 'string' ? `badge bg-${getEventTypeBadge(event)} me-2` : 'badge me-2'}
                          style={typeof getEventTypeBadge(event) === 'object' ? getEventTypeBadge(event) : {}}
                        >
                          {event.category}
                        </span>
                      )}
                      <span className={`badge bg-${typeof getEventTypeBadge(event) === 'string' ? getEventTypeBadge(event) : 'secondary'}`}>
                        {event.type || 'other'}
                      </span>
                    </div>
                  </div>
                  <div className="card-body">
                    {event.is_cancelled && (
                      <div className="alert alert-danger py-2 mb-3">
                        <small>
                          <strong>⚠️ This event has been cancelled</strong>
                          <br />
                          <em>Reason: {event.cancellation_reason}</em>
                          <br />
                          <small className="text-muted">
                            Cancelled {event.cancelled_at ? new Date(event.cancelled_at).toLocaleDateString() : 'recently'}
                            {event.canceller_name && ` by ${event.canceller_name}`}
                          </small>
                        </small>
                      </div>
                    )}
                    <p className="card-text">{event.description}</p>
                    <div className="mb-2">
                      <small className="text-muted">
                        <i className="bi bi-calendar me-1"></i>
                        {formatDate(event.date)}
                      </small>
                    </div>
                    {event.time && (
                      <div className="mb-2">
                        <small className="text-muted">
                          <i className="bi bi-clock me-1"></i>
                          {formatTime(event.time)}
                        </small>
                      </div>
                    )}
                    {event.location_address && (
                      <div className="mb-3">
                        <small className="text-muted">
                          <i className="bi bi-geo-alt me-1"></i>
                          {event.location_address}
                          {event.lat && event.lng && (
                            <a
                              href={`https://www.google.com/maps?q=${event.lat},${event.lng}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ms-2 text-decoration-none"
                            >
                              <i className="bi bi-box-arrow-up-right"></i>
                            </a>
                          )}
                        </small>
                      </div>
                    )}
                    
                    <div className="d-flex gap-2 flex-wrap">
                      <button 
                        className={`btn btn-sm ${status[event.id] === 'yes' ? 'btn-success' : 'btn-outline-success'}`}
                        onClick={() => handleRsvp(event.id, 'yes')}
                      >
                        ✓ Yes
                      </button>
                      <button 
                        className={`btn btn-sm ${status[event.id] === 'no' ? 'btn-danger' : 'btn-outline-danger'}`}
                        onClick={() => handleRsvp(event.id, 'no')}
                      >
                        ✗ No
                      </button>
                      {status[event.id] === 'no' && (
                        <button 
                          className={`btn btn-sm ${substituteRequests[event.id] ? 'btn-success' : 'btn-outline-info'}`}
                          onClick={() => handleSubstituteRequest(event.id)}
                          disabled={substituteRequests[event.id]}
                        >
                          {substituteRequests[event.id] ? '✓ Sub Requested' : '👤 Request Substitute'}
                        </button>
                      )}
                      <button 
                        className={`btn btn-sm ${status[event.id] === 'maybe' ? 'btn-warning' : 'btn-outline-warning'}`}
                        onClick={() => handleRsvp(event.id, 'maybe')}
                      >
                        ? Maybe
                      </button>
                    </div>
                  </div>
                  
                  {role === 'Admin' && (
                    <div className="card-footer">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <button
                            className="btn btn-sm btn-outline-secondary me-2"
                            onClick={() => {
                              setEditEvent(event);
                              setShowForm(true);
                            }}
                            title="Edit Event"
                            disabled={event.is_cancelled}
                          >
                            <i className="bi bi-pencil"></i>
                          </button>
                          {!event.is_cancelled && (
                            <button
                              className="btn btn-sm btn-outline-warning me-2"
                              onClick={() => openCancelModal(event)}
                              title="Cancel Event"
                            >
                              <i className="bi bi-x-circle"></i>
                            </button>
                          )}
                          <button
                            className="btn btn-sm btn-outline-info me-2"
                            onClick={() => downloadEventRSVPPDF(event)}
                            title="Download RSVP Report PDF"
                          >
                            <i className="bi bi-file-earmark-pdf"></i>
                          </button>
                          <button
                            className="btn btn-sm btn-outline-danger"
                            onClick={() => handleDelete(event.id)}
                            title="Delete Event"
                          >
                            <i className="bi bi-trash"></i>
                          </button>
                        </div>
                        
                        <div className="d-flex gap-1">
                          <div className="dropdown">
                            <button 
                              className="btn btn-sm btn-outline-success dropdown-toggle"
                              type="button" 
                              data-bs-toggle="dropdown"
                            >
                              <i className="bi bi-download me-1"></i>
                              Export
                            </button>
                            <ul className="dropdown-menu">
                              <li>
                                <button 
                                  className="dropdown-item" 
                                  onClick={(e) => { e.preventDefault(); exportRsvps(event.id, 'csv'); }}
                                >
                                  <i className="bi bi-filetype-csv me-2"></i>
                                  Export as CSV
                                </button>
                              </li>
                              <li>
                                <button 
                                  className="dropdown-item" 
                                  onClick={(e) => { e.preventDefault(); exportRsvps(event.id, 'pdf'); }}
                                >
                                  <i className="bi bi-filetype-pdf me-2"></i>
                                  Export as PDF
                                </button>
                              </li>
                            </ul>
                          </div>
                          
                          <button
                            className="btn btn-sm btn-outline-info"
                            onClick={() => toggleSummary(event.id)}
                          >
                            {openSummary[event.id] ? 'Hide' : 'Show'} RSVPs
                          </button>
                        </div>
                      </div>
                      
                      {openSummary[event.id] && rsvpSummary[event.id] && (
                        <div className="mt-3">
                          <h6>RSVP Summary:</h6>
                          {rsvpLoading ? (
                            <LoadingSpinner size="sm" />
                          ) : rsvpError ? (
                            <p className="text-danger">{rsvpError}</p>
                          ) : (
                            <div className="small">
                              <div className="text-success">
                                <strong>Yes ({rsvpSummary[event.id].yes?.length || 0}):</strong> {rsvpSummary[event.id].yes?.map(user => user.name || user.username).join(', ') || 'None'}
                              </div>
                              <div className="text-danger">
                                <strong>No ({rsvpSummary[event.id].no?.length || 0}):</strong> {rsvpSummary[event.id].no?.map(user => user.name || user.username).join(', ') || 'None'}
                              </div>
                              <div className="text-warning">
                                <strong>Maybe ({rsvpSummary[event.id].maybe?.length || 0}):</strong> {rsvpSummary[event.id].maybe?.map(user => user.name || user.username).join(', ') || 'None'}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Event Cancellation Modal */}
      {showCancelModal && (
        <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-x-circle-fill text-danger me-2"></i>
                  Cancel Event
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={closeCancelModal}
                  disabled={cancelLoading}
                ></button>
              </div>
              <div className="modal-body">
                {eventToCancel && (
                  <>
                    <div className="alert alert-warning">
                      <strong>⚠️ Are you sure you want to cancel this event?</strong>
                      <br />
                      <strong>Event:</strong> {eventToCancel.title}
                      <br />
                      <strong>Date:</strong> {new Date(eventToCancel.date).toLocaleDateString()}
                      <br />
                      <small className="text-muted">
                        This action cannot be undone. The event will be marked as cancelled.
                      </small>
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="cancellationReason" className="form-label">
                        <strong>Reason for cancellation *</strong>
                      </label>
                      <textarea
                        id="cancellationReason"
                        className="form-control"
                        rows="3"
                        placeholder="Please provide a reason for the cancellation (e.g., weather, illness, venue unavailable)..."
                        value={cancellationReason}
                        onChange={(e) => setCancellationReason(e.target.value)}
                        disabled={cancelLoading}
                      />
                    </div>
                    
                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="sendNotification"
                        checked={sendCancellationNotification}
                        onChange={(e) => setSendCancellationNotification(e.target.checked)}
                        disabled={cancelLoading}
                      />
                      <label className="form-check-label" htmlFor="sendNotification">
                        Send cancellation notification email to all organization members
                      </label>
                    </div>
                  </>
                )}
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeCancelModal}
                  disabled={cancelLoading}
                >
                  Keep Event
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={handleCancelEvent}
                  disabled={cancelLoading || !cancellationReason.trim()}
                >
                  {cancelLoading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Cancelling...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-x-circle me-1"></i>
                      Cancel Event
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {showCancelModal && <div className="modal-backdrop fade show"></div>}

      {/* Template Usage Modal */}
      {showTemplateModal && (
        <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="bi bi-calendar-plus me-2"></i>
                  Create Event from Template
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={closeTemplateModal}
                ></button>
              </div>
              <div className="modal-body">
                {selectedTemplate && (
                  <>
                    <div className="mb-3">
                      <h6 className="fw-bold">{selectedTemplate.template_name || selectedTemplate.title}</h6>
                      <p className="text-muted small mb-0">{selectedTemplate.description}</p>
                      {selectedTemplate.category && (
                        <span className="badge bg-secondary mt-1">{selectedTemplate.category}</span>
                      )}
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="template-date" className="form-label">
                        <i className="bi bi-calendar me-1"></i>
                        Event Date & Time *
                      </label>
                      <input
                        type="datetime-local"
                        className="form-control"
                        id="template-date"
                        value={templateDate}
                        onChange={(e) => setTemplateDate(e.target.value)}
                        required
                      />
                    </div>

                    <div className="mb-3">
                      <label htmlFor="template-location" className="form-label">
                        <i className="bi bi-geo-alt me-1"></i>
                        Location (Optional)
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="template-location"
                        value={templateLocation}
                        onChange={(e) => setTemplateLocation(e.target.value)}
                        placeholder="Enter event location"
                      />
                    </div>

                    <div className="alert alert-info">
                      <i className="bi bi-info-circle me-2"></i>
                      <strong>Note:</strong> This will create a new event using the template's settings. 
                      You can modify the event details after creation.
                    </div>
                  </>
                )}
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeTemplateModal}
                  disabled={templateLoading}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={createEventFromTemplate}
                  disabled={templateLoading || !templateDate}
                >
                  {templateLoading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Creating...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-plus-circle me-1"></i>
                      Create Event
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {showTemplateModal && <div className="modal-backdrop fade show"></div>}
    </div>
  );
}

export default EventsPage;
