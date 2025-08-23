import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import EnhancedEventForm from '../components/EnhancedEventForm';
import { 
  DataLoadingState, 
  ErrorState, 
  EmptyState 
} from '../components/LoadingComponents';
import { 
  ResponsiveStatsGrid,
  ResponsiveActionBar
} from '../components/ResponsiveComponents';
import UserAvatar from '../components/UserAvatar';
import { useTheme } from '../contexts/ThemeContext';
import { getGoogleMapsApiKey } from '../config/constants';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

function Events() {
  const [events, setEvents] = useState([]);
  const [rsvps, setRsvps] = useState({});
  const [allRsvps, setAllRsvps] = useState({}); // Store all member responses
  const [sections, setSections] = useState([]); // Store sections
  const [allUsers, setAllUsers] = useState([]); // Store all users with section info
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('upcoming'); // Default to 'upcoming'
  const [expandedEvents, setExpandedEvents] = useState({}); // Track which events are expanded
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [categories, setCategories] = useState([]);
  const { orgThemeColor } = useTheme();
  const role = localStorage.getItem('role');

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

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        
        if (!token) {
          setError('Authentication required. Please log in.');
          setLoading(false);
          return;
        }

        // Fetch events using the same approach as EventsPage
        const eventsResponse = await axios.get(`${getApiUrl()}/events/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Sort events by date
        const sortedEvents = eventsResponse.data.sort((a, b) => new Date(a.date) - new Date(b.date));
        setEvents(sortedEvents);

        // Load current user's RSVP status for each event (same as EventsPage)
        const username = localStorage.getItem('username');
        const rsvpMap = {};
        for (const event of sortedEvents) {
          try {
            const rsvpRes = await axios.get(`${getApiUrl()}/events/${event.id}/rsvps`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            // Find user's RSVP status
            for (const [rsvpStatus, users] of Object.entries(rsvpRes.data)) {
              if (users.some(user => user.username === username)) {
                rsvpMap[event.id] = rsvpStatus;
                break;
              }
            }
          } catch (error) {
            console.warn('Error loading RSVP status for event:', event.id, error);
          }
        }
        setRsvps(rsvpMap);

        // Fetch RSVP details for each event (for admin response counts)
        if (role === 'Admin' || role === 'admin' || role === 'super_admin') {
          const eventRsvpData = {};
          for (const event of sortedEvents) {
            try {
              const rsvpRes = await axios.get(`${getApiUrl()}/events/${event.id}/rsvps`, {
                headers: { Authorization: `Bearer ${token}` }
              });
              
              // Store the full RSVP data for this event
              eventRsvpData[event.id] = rsvpRes.data;
              console.log(`Loaded RSVP data for event ${event.id}:`, rsvpRes.data);
            } catch (error) {
              console.warn(`Error loading RSVP details for event ${event.id}:`, error);
            }
          }
          setAllRsvps(eventRsvpData);
          console.log('All event RSVP data loaded:', eventRsvpData);
        }

      } catch (error) {
        console.error('Error fetching data:', error);
        if (error.response?.status === 401) {
          setError('Session expired. Please log in again.');
          localStorage.removeItem('token');
          window.location.href = '/login';
        } else {
          setError(error.response?.data?.message || 'Failed to load events. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [role]);

  const handleRSVP = async (eventId, status) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        showErrorMessage('Authentication required. Please log in.');
        return;
      }

      await axios.post(`${getApiUrl()}/events/${eventId}/rsvp`, {
        status: status
      }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Update local state immediately for better UX
      setRsvps(prev => ({
        ...prev,
        [eventId]: status
      }));

      // Show success message
      const statusMessages = {
        'yes': 'RSVP confirmed! See you there! 🎉',
        'no': 'RSVP updated - marked as not attending',
        'maybe': 'RSVP updated - marked as maybe attending'
      };
      
      showSuccessMessage(statusMessages[status] || 'RSVP updated successfully!');

    } catch (error) {
      console.error('Error updating RSVP:', error);
      if (error.response?.status === 401) {
        showErrorMessage('Session expired. Please log in again.');
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else {
        showErrorMessage(error.response?.data?.message || 'Failed to update RSVP. Please try again.');
      }
    }
  };

  const toggleEventExpansion = (eventId) => {
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  const isEventPast = (eventDateTime) => {
    if (!eventDateTime) return false; // TBD events are not past
    const eventDate = new Date(eventDateTime);
    const now = new Date();
    return eventDate < now;
  };

  const isEventUpcoming = (eventDateTime) => {
    if (!eventDateTime) return true; // TBD events are considered upcoming
    const eventDate = new Date(eventDateTime);
    const now = new Date();
    return eventDate >= now;
  };

  const getFilteredEvents = () => {
    if (filter === 'all') return events;
    if (filter === 'past') return events.filter(event => isEventPast(event.dateTime));
    if (filter === 'upcoming') return events.filter(event => isEventUpcoming(event.dateTime));
    return events;
  };

  const getRSVPCounts = (eventId) => {
    const eventRsvps = allRsvps[eventId] || {};
    const counts = {
      yes: 0,
      no: 0,
      maybe: 0,
      total: 0
    };
    
    // The data structure from /events/{id}/rsvps is: { "yes": [users], "no": [users], "maybe": [users] }
    Object.entries(eventRsvps).forEach(([status, users]) => {
      if (Array.isArray(users)) {
        counts[status] = users.length;
        counts.total += users.length;
      }
    });
    
    console.log(`RSVP counts for event ${eventId}:`, counts, 'Raw data:', eventRsvps);
    return counts;
  };

  const getUsersForEvent = (eventId, status = null) => {
    const eventRsvps = allRsvps[eventId] || {};
    
    if (status) {
      // Return users for a specific status
      return eventRsvps[status] || [];
    } else {
      // Return all users for the event
      const allUsers = [];
      Object.values(eventRsvps).forEach(users => {
        if (Array.isArray(users)) {
          allUsers.push(...users);
        }
      });
      return allUsers;
    }
  };

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString || dateTimeString === 'TBD') {
      return 'TBD';
    }
    
    try {
      const date = new Date(dateTimeString);
      const now = new Date();
      const isToday = date.toDateString() === now.toDateString();
      
      if (isToday) {
        return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      }
      
      const dayOptions = { weekday: 'short', month: 'short', day: 'numeric' };
      const timeOptions = { hour: '2-digit', minute: '2-digit' };
      
      return `${date.toLocaleDateString([], dayOptions)} at ${date.toLocaleTimeString([], timeOptions)}`;
    } catch (error) {
      return dateTimeString;
    }
  };

  const getRSVPButtonClass = (status, currentStatus) => {
    const baseClass = 'btn btn-sm mx-1';
    if (status === currentStatus) {
      switch (status) {
        case 'yes': return `${baseClass} btn-success`;
        case 'no': return `${baseClass} btn-danger`;
        case 'maybe': return `${baseClass} btn-warning`;
        default: return `${baseClass} btn-outline-secondary`;
      }
    }
    return `${baseClass} btn-outline-secondary`;
  };

  // Create new event handler
  const handleCreateEvent = async (eventData) => {
    try {
      const token = localStorage.getItem('token');
      
      await axios.post(`${getApiUrl()}/events`, eventData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Refresh events list
      const eventsResponse = await axios.get(`${getApiUrl()}/events/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const sortedEvents = eventsResponse.data.sort((a, b) => new Date(a.date) - new Date(b.date));
      setEvents(sortedEvents);
      
      setShowCreateForm(false);
      showSuccessMessage('Event created successfully! 🎉');
      
    } catch (error) {
      console.error('Error creating event:', error);
      showErrorMessage(error.response?.data?.error || 'Failed to create event. Please try again.');
      throw error; // Re-throw so the form can handle it
    }
  };

  // Edit event handler
  const handleEditEvent = async (eventData) => {
    try {
      const token = localStorage.getItem('token');
      
      await axios.put(`${getApiUrl()}/events/${editingEvent.id}`, eventData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Refresh events list
      const eventsResponse = await axios.get(`${getApiUrl()}/events/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const sortedEvents = eventsResponse.data.sort((a, b) => new Date(a.date) - new Date(b.date));
      setEvents(sortedEvents);
      
      setShowEditForm(false);
      setEditingEvent(null);
      showSuccessMessage('Event updated successfully! ✅');
      
    } catch (error) {
      console.error('Error updating event:', error);
      showErrorMessage(error.response?.data?.error || 'Failed to update event. Please try again.');
      throw error; // Re-throw so the form can handle it
    }
  };

  // Open edit form with event data
  const openEditForm = (event) => {
    setEditingEvent(event);
    setShowEditForm(true);
  };

  // Delete event handler
  const handleDeleteEvent = async (event) => {
    if (!window.confirm(`Are you sure you want to delete "${event.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      
      await axios.delete(`${getApiUrl()}/events/${event.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Refresh events list
      const eventsResponse = await axios.get(`${getApiUrl()}/events/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const sortedEvents = eventsResponse.data.sort((a, b) => new Date(a.date) - new Date(b.date));
      setEvents(sortedEvents);
      
      showSuccessMessage('Event deleted successfully! 🗑️');
      
    } catch (error) {
      console.error('Error deleting event:', error);
      showErrorMessage(error.response?.data?.error || 'Failed to delete event. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-vh-100 bg-light">
        <Navbar />
        <div className="container-fluid mt-4">
          <DataLoadingState 
            title="Loading Events..."
            subtitle="Fetching your event schedule and RSVPs"
          />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-vh-100 bg-light">
        <Navbar />
        <div className="container-fluid mt-4">
          <ErrorState 
            title="Unable to Load Events"
            message={error}
            onRetry={() => window.location.reload()}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 bg-light">
      <Navbar />
      <NotificationSystem />

      <div className="container-fluid mt-4">
        {/* Page Header */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <h1 className="h2 mb-1 text-dark fw-bold">
                  <i className="fas fa-calendar-alt me-2 text-primary"></i>
                  Events
                </h1>
                <p className="text-muted mb-0">View and manage your event schedule</p>
              </div>
              <div className="d-flex align-items-center gap-3">
                {/* Create Event Button - Admin Only */}
                {(role === 'Admin' || role === 'admin' || role === 'super_admin') && (
                  <button 
                    className="btn btn-success"
                    onClick={() => setShowCreateForm(true)}
                  >
                    <i className="fas fa-plus me-2"></i>
                    Create Event
                  </button>
                )}
                <a href="/analytics" className="btn btn-outline-primary">
                  <i className="fas fa-chart-line me-2"></i>
                  Analytics Dashboard
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="row mb-3">
          <div className="col-12">
            <div className="card border-0 shadow-sm">
              <div className="card-body py-2">
                <div className="d-flex justify-content-center">
                  <div className="btn-group" role="group">
                    <button
                      type="button"
                      className={`btn ${filter === 'upcoming' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => setFilter('upcoming')}
                    >
                      <i className="fas fa-calendar-plus me-1"></i>
                      Upcoming ({events.filter(e => isEventUpcoming(e.dateTime)).length})
                    </button>
                    <button
                      type="button"
                      className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => setFilter('all')}
                    >
                      <i className="fas fa-calendar me-1"></i>
                      All Events ({events.length})
                    </button>
                    <button
                      type="button"
                      className={`btn ${filter === 'past' ? 'btn-primary' : 'btn-outline-primary'}`}
                      onClick={() => setFilter('past')}
                    >
                      <i className="fas fa-calendar-check me-1"></i>
                      Past ({events.filter(e => isEventPast(e.dateTime)).length})
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Events List */}
        {getFilteredEvents().length === 0 ? (
          <EmptyState 
            title="No Events Found"
            message={filter === 'past' ? "No past events to show." : filter === 'upcoming' ? "No upcoming events scheduled." : "There are no events scheduled at the moment."}
            actionText="Refresh"
            onAction={() => window.location.reload()}
          />
        ) : (
          <div className="row">
            {getFilteredEvents().map(event => {
              const isExpanded = expandedEvents[event.id];
              const rsvpCounts = getRSVPCounts(event.id);
              const isPastEvent = isEventPast(event.dateTime);
              
              return (
                <div key={event.id} className="col-12 mb-4">
                  <div className={`card border-0 shadow-lg h-100 overflow-hidden position-relative ${isPastEvent ? 'opacity-75' : ''}`} 
                       style={{ 
                         borderRadius: '20px', 
                         transition: 'all 0.3s ease, transform 0.2s ease',
                         cursor: 'pointer',
                         border: `3px solid ${isPastEvent ? '#dee2e6' : (orgThemeColor || '#0d6efd')}33`
                       }}
                       onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-3px)'}
                       onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0px)'}>
                    
                    {/* Color accent top border */}
                    <div 
                      style={{
                        height: '6px',
                        background: isPastEvent ? '#6c757d' : `linear-gradient(90deg, ${orgThemeColor || '#0d6efd'} 0%, ${orgThemeColor ? `${orgThemeColor}aa` : '#0851d4'} 100%)`,
                        borderRadius: '20px 20px 0 0'
                      }}
                    ></div>
                    
                    {/* Main Event Content */}
                    <div 
                      className="card-body"
                      onClick={(e) => {
                        // Only expand if clicking on the card body, not buttons
                        if (!e.target.closest('button')) {
                          toggleEventExpansion(event.id);
                        }
                      }}
                      style={{ padding: '1.5rem', cursor: 'pointer' }}
                    >
                      <div className="d-flex flex-column gap-3">
                        {/* Event Title and Chevron */}
                        <div className="d-flex justify-content-between align-items-start">
                          <div className="d-flex align-items-start gap-3 flex-grow-1">
                            <div 
                              className="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                              style={{
                                width: '50px',
                                height: '50px',
                                background: isPastEvent ? '#6c757d' : `linear-gradient(135deg, ${orgThemeColor || '#0d6efd'} 0%, ${orgThemeColor ? `${orgThemeColor}dd` : '#0851d4'} 100%)`,
                                color: 'white'
                              }}
                            >
                              <i className="fas fa-calendar-check fs-5"></i>
                            </div>
                            <div className="flex-grow-1">
                              <h5 className="card-title mb-1 fw-bold text-dark">
                                {event.name}
                              </h5>
                              <div className="d-flex flex-wrap gap-2 align-items-center">
                                <span className="badge bg-light text-muted">
                                  {event.event_type || 'Event'}
                                </span>
                                {isPastEvent && (
                                  <span className="badge bg-secondary">
                                    <i className="fas fa-history me-1"></i>
                                    Past Event
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="d-flex gap-2">
                            {/* Admin Action Buttons */}
                            {(role === 'Admin' || role === 'admin' || role === 'super_admin') && (
                              <>
                                {/* Edit Button */}
                                <button 
                                  className="btn btn-sm btn-warning rounded-circle p-2"
                                  style={{ width: '40px', height: '40px' }}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    openEditForm(event);
                                  }}
                                  title="Edit Event"
                                >
                                  <i className="fas fa-pencil-alt"></i>
                                </button>
                                {/* Delete Button */}
                                <button 
                                  className="btn btn-sm btn-danger rounded-circle p-2"
                                  style={{ width: '40px', height: '40px' }}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteEvent(event);
                                  }}
                                  title="Delete Event"
                                >
                                  <i className="fas fa-trash-alt"></i>
                                </button>
                              </>
                            )}
                            {/* Expand/Collapse Button */}
                            <button 
                              className="btn btn-sm btn-light rounded-circle p-2"
                              style={{ width: '40px', height: '40px' }}
                              onClick={() => toggleEventExpansion(event.id)}
                              title={isExpanded ? 'Collapse' : 'Expand'}
                            >
                              <i className="fas fa-ellipsis-h"></i>
                            </button>
                          </div>
                        </div>
                        
                        {/* Event Details Grid */}
                        <div className="row g-3">
                          <div className="col-md-6">
                            <div className="d-flex align-items-center gap-2 p-2 bg-light rounded-3">
                              <i className="fas fa-clock text-primary"></i>
                              <div>
                                <small className="text-muted d-block">When</small>
                                <span className="fw-medium">{formatDateTime(event.dateTime)}</span>
                              </div>
                            </div>
                          </div>
                          
                          {event.location && (
                            <div className="col-md-6">
                              <div className="d-flex align-items-center gap-2 p-2 bg-light rounded-3">
                                <i className="fas fa-map-marker-alt text-danger"></i>
                                <div>
                                  <small className="text-muted d-block">Where</small>
                                  <span className="fw-medium">
                                    {event.location.length > 25 ? `${event.location.substring(0, 25)}...` : event.location}
                                  </span>
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {(role === 'Admin' || role === 'admin' || role === 'super_admin') && (
                            <div className="col-md-6">
                              <div className="d-flex align-items-center gap-2 p-2 bg-success bg-opacity-10 rounded-3">
                                <i className="fas fa-users text-success"></i>
                                <div>
                                  <small className="text-muted d-block">Attending</small>
                                  <span className="fw-bold text-success">{rsvpCounts.yes} members</span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* RSVP Buttons - Clean separator */}
                    {!isPastEvent && (
                      <div className="card-footer bg-white border-0" style={{ padding: '1rem 1.5rem' }}>
                        <div className="d-flex gap-2">
                          <button
                            className={`btn flex-fill ${rsvps[event.id] === 'yes' ? 'btn-success' : 'btn-outline-success'}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRSVP(event.id, 'yes');
                            }}
                            style={{ borderRadius: '12px', fontWeight: '600', padding: '10px' }}
                          >
                            <i className="fas fa-check me-2"></i>
                            Going
                          </button>
                          <button
                            className={`btn flex-fill ${rsvps[event.id] === 'maybe' ? 'btn-warning' : 'btn-outline-warning'}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRSVP(event.id, 'maybe');
                            }}
                            style={{ borderRadius: '12px', fontWeight: '600', padding: '10px' }}
                          >
                            <i className="fas fa-question me-2"></i>
                            Maybe
                          </button>
                          <button
                            className={`btn flex-fill ${rsvps[event.id] === 'no' ? 'btn-danger' : 'btn-outline-danger'}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRSVP(event.id, 'no');
                            }}
                            style={{ borderRadius: '12px', fontWeight: '600', padding: '10px' }}
                          >
                            <i className="fas fa-times me-2"></i>
                            Can't Go
                          </button>
                        </div>
                      </div>
                    )}
                    
                    {/* Event Description */}
                    {event.description && (
                      <div className="px-4 pb-3">
                        <div className="alert alert-light mb-0" style={{ borderRadius: '12px' }}>
                          <small className="text-muted">{event.description}</small>
                        </div>
                      </div>
                    )}

                    {/* Expandable Content */}
                    {isExpanded && (
                      <div className="card-footer bg-light border-0" style={{ padding: '1.5rem', borderRadius: '0 0 20px 20px' }}>
                        <div className="row g-3">
                          {/* Location with Map */}
                          {event.location && (
                            <div className="col-lg-6">
                              <div className="card border-0 shadow-sm">
                                <div className="card-header bg-white border-0">
                                  <h6 className="fw-bold text-dark mb-0">
                                    <i className="fas fa-map-marker-alt me-2 text-danger"></i>
                                    Location
                                  </h6>
                                </div>
                                <div className="card-body">
                                  <p className="text-muted mb-3">{event.location}</p>
                                  <div style={{ borderRadius: '12px', overflow: 'hidden' }}>
                                    <iframe
                                      width="100%"
                                      height="200"
                                      style={{ border: 0 }}
                                      src={`https://www.google.com/maps/embed/v1/place?key=${getGoogleMapsApiKey()}&q=${encodeURIComponent(event.location)}`}
                                      allowFullScreen
                                    ></iframe>
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {/* RSVP Responses for Admins */}
                          {(role === 'Admin' || role === 'admin' || role === 'super_admin') && (
                            <div className="col-lg-6">
                              <div className="card border-0 shadow-sm">
                                <div className="card-header bg-white border-0">
                                  <h6 className="fw-bold text-dark mb-0">
                                    <i className="fas fa-users me-2 text-primary"></i>
                                    Responses ({rsvpCounts.total})
                                  </h6>
                                </div>
                                <div className="card-body">
                                  {rsvpCounts.total > 0 ? (
                                    <>
                                      <div className="row g-2 mb-3">
                                        <div className="col-4">
                                          <div className="text-center p-3 bg-success bg-opacity-10 rounded-3">
                                            <div className="h4 mb-1 text-success fw-bold">{rsvpCounts.yes}</div>
                                            <small className="text-success fw-medium">Going</small>
                                          </div>
                                        </div>
                                        <div className="col-4">
                                          <div className="text-center p-3 bg-warning bg-opacity-10 rounded-3">
                                            <div className="h4 mb-1 text-warning fw-bold">{rsvpCounts.maybe}</div>
                                            <small className="text-warning fw-medium">Maybe</small>
                                          </div>
                                        </div>
                                        <div className="col-4">
                                          <div className="text-center p-3 bg-danger bg-opacity-10 rounded-3">
                                            <div className="h4 mb-1 text-danger fw-bold">{rsvpCounts.no}</div>
                                            <small className="text-danger fw-medium">Can't Go</small>
                                          </div>
                                        </div>
                                      </div>
                                      
                                      {getUsersForEvent(event.id, 'yes').length > 0 && (
                                        <div>
                                          <small className="text-muted d-block mb-2 fw-medium">Who's attending:</small>
                                          <div className="d-flex flex-wrap gap-2">
                                            {getUsersForEvent(event.id, 'yes').slice(0, 8).map(user => (
                                              <UserAvatar 
                                                key={user.id}
                                                user={user} 
                                                size="sm"
                                                showTooltip={true}
                                              />
                                            ))}
                                            {getUsersForEvent(event.id, 'yes').length > 8 && (
                                              <span className="badge bg-secondary rounded-pill">
                                                +{getUsersForEvent(event.id, 'yes').length - 8} more
                                              </span>
                                            )}
                                          </div>
                                        </div>
                                      )}
                                    </>
                                  ) : (
                                    <div className="text-center py-3">
                                      <i className="fas fa-inbox text-muted fs-1 mb-2"></i>
                                      <p className="text-muted mb-0">No responses yet</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
        
        {/* Create Event Modal */}
        <EnhancedEventForm
          show={showCreateForm}
          onHide={() => setShowCreateForm(false)}
          onSave={handleCreateEvent}
          categories={categories}
        />

        {/* Edit Event Modal */}
        <EnhancedEventForm
          show={showEditForm}
          onHide={() => {
            setShowEditForm(false);
            setEditingEvent(null);
          }}
          onSave={handleEditEvent}
          event={editingEvent}
          categories={categories}
        />
      </div>
    </div>
  );
}

export default Events;
