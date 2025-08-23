import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
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
  const [filter, setFilter] = useState('upcoming'); // Default to 'upcoming', can be changed to 'all' or 'past'
  const [expandedEvents, setExpandedEvents] = useState({}); // Track which events are expanded
  const { orgThemeColor } = useTheme();
  const role = localStorage.getItem('role'); // Assuming role is stored in localStorage

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
        const organizationId = localStorage.getItem('organizationId');
        
        if (!token || !organizationId) {
          setError('Authentication required. Please log in.');
          setLoading(false);
          return;
        }

        // Create config object for API requests
        const config = {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        };

        // Fetch events and RSVPs in parallel
        const [eventsResponse, rsvpResponse] = await Promise.all([
          axios.get(`${getApiUrl()}/events/organization/${organizationId}`, config),
          axios.get(`${getApiUrl()}/rsvps/user`, config)
        ]);

        setEvents(eventsResponse.data);
        
        // Convert RSVP array to object for easier lookup
        const rsvpMap = {};
        if (rsvpResponse.data && Array.isArray(rsvpResponse.data)) {
          rsvpResponse.data.forEach(rsvp => {
            rsvpMap[rsvp.eventId] = rsvp.status;
          });
        }
        setRsvps(rsvpMap);

        // Fetch additional data for admin users
        if (role === 'admin' || role === 'super_admin') {
          try {
            const [allRsvpsResponse, sectionsResponse, usersResponse] = await Promise.all([
              axios.get(`${getApiUrl()}/rsvps/all/${organizationId}`, config),
              axios.get(`${getApiUrl()}/sections/organization/${organizationId}`, config),
              axios.get(`${getApiUrl()}/users/organization/${organizationId}`, config)
            ]);

            // Process all RSVPs data
            const allRsvpsMap = {};
            if (allRsvpsResponse.data && Array.isArray(allRsvpsResponse.data)) {
              allRsvpsResponse.data.forEach(rsvp => {
                if (!allRsvpsMap[rsvp.eventId]) {
                  allRsvpsMap[rsvp.eventId] = {};
                }
                allRsvpsMap[rsvp.eventId][rsvp.userId] = rsvp.status;
              });
            }
            setAllRsvps(allRsvpsMap);

            setSections(sectionsResponse.data || []);
            setAllUsers(usersResponse.data || []);
          } catch (adminError) {
            console.warn('Error fetching admin data:', adminError);
            // Continue without admin data
          }
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
      const organizationId = localStorage.getItem('organizationId');
      
      if (!token || !organizationId) {
        showErrorMessage('Authentication required. Please log in.');
        return;
      }

      const config = {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      };

      await axios.post(`${getApiUrl()}/rsvps`, {
        eventId: parseInt(eventId),
        status
      }, config);

      // Update local state immediately for better UX
      setRsvps(prev => ({
        ...prev,
        [eventId]: status
      }));

      // Show success message with status-specific text
      const statusMessages = {
        'yes': 'RSVP confirmed! See you there! 🎉',
        'no': 'RSVP updated - marked as not attending',
        'maybe': 'RSVP updated - marked as maybe attending'
      };
      
      showSuccessMessage(statusMessages[status] || 'RSVP updated successfully!');

      // Refresh admin data if user is admin
      if (role === 'admin' || role === 'super_admin') {
        try {
          const allRsvpsResponse = await axios.get(`${getApiUrl()}/rsvps/all/${organizationId}`, config);
          const allRsvpsMap = {};
          if (allRsvpsResponse.data && Array.isArray(allRsvpsResponse.data)) {
            allRsvpsResponse.data.forEach(rsvp => {
              if (!allRsvpsMap[rsvp.eventId]) {
                allRsvpsMap[rsvp.eventId] = {};
              }
              allRsvpsMap[rsvp.eventId][rsvp.userId] = rsvp.status;
            });
          }
          setAllRsvps(allRsvpsMap);
        } catch (error) {
          console.warn('Error refreshing admin RSVP data:', error);
        }
      }

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

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return 'TBD';
    
    try {
      const date = new Date(dateTimeString);
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Invalid Date';
      }
      
      return date.toLocaleString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Invalid Date';
    }
  };

  const isEventPast = (eventDateTime) => {
    if (!eventDateTime) return false;
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
      total: Object.keys(eventRsvps).length
    };
    
    Object.values(eventRsvps).forEach(status => {
      if (counts.hasOwnProperty(status)) {
        counts[status]++;
      }
    });
    
    return counts;
  };

  const getUsersForEvent = (eventId, status = null) => {
    const eventRsvps = allRsvps[eventId] || {};
    const userIds = status 
      ? Object.keys(eventRsvps).filter(userId => eventRsvps[userId] === status)
      : Object.keys(eventRsvps);
    
    return userIds.map(userId => {
      const user = allUsers.find(u => u.id === parseInt(userId));
      if (!user) return null;
      
      const section = sections.find(s => s.id === user.sectionId);
      return {
        ...user,
        sectionName: section?.name || 'No Section'
      };
    }).filter(Boolean);
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

  const filteredEvents = getFilteredEvents();

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
                <a href="/analytics" className="btn btn-outline-primary">
                  <i className="fas fa-chart-line me-2"></i>
                  Analytics Dashboard
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <ResponsiveStatsGrid>
          <div className="col-md-3 col-6 mb-3">
            <div className="card h-100 border-0 shadow-sm">
              <div className="card-body text-center">
                <div className="display-6 fw-bold text-primary mb-1">
                  {events.length}
                </div>
                <div className="small text-muted">Total Events</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-6 mb-3">
            <div className="card h-100 border-0 shadow-sm">
              <div className="card-body text-center">
                <div className="display-6 fw-bold text-success mb-1">
                  {events.filter(event => isEventUpcoming(event.dateTime)).length}
                </div>
                <div className="small text-muted">Upcoming</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-6 mb-3">
            <div className="card h-100 border-0 shadow-sm">
              <div className="card-body text-center">
                <div className="display-6 fw-bold text-info mb-1">
                  {Object.values(rsvps).filter(status => status === 'yes').length}
                </div>
                <div className="small text-muted">Attending</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 col-6 mb-3">
            <div className="card h-100 border-0 shadow-sm">
              <div className="card-body text-center">
                <div className="display-6 fw-bold text-warning mb-1">
                  {Object.values(rsvps).filter(status => status === 'maybe').length}
                </div>
                <div className="small text-muted">Maybe</div>
              </div>
            </div>
          </div>
        </ResponsiveStatsGrid>

        {/* Filter Controls */}
        <ResponsiveActionBar className="mb-4">
          <div className="d-flex flex-wrap gap-2">
            <button 
              className={`btn ${filter === 'upcoming' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFilter('upcoming')}
            >
              <i className="fas fa-clock me-1"></i>
              Upcoming
            </button>
            <button 
              className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFilter('all')}
            >
              <i className="fas fa-list me-1"></i>
              All Events
            </button>
            <button 
              className={`btn ${filter === 'past' ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFilter('past')}
            >
              <i className="fas fa-history me-1"></i>
              Past Events
            </button>
          </div>
        </ResponsiveActionBar>

        {/* Events List */}
        {filteredEvents.length === 0 ? (
          <EmptyState 
            title={filter === 'upcoming' ? "No Upcoming Events" : filter === 'past' ? "No Past Events" : "No Events Found"}
            message={filter === 'upcoming' ? "No upcoming events scheduled at the moment." : filter === 'past' ? "No past events to display." : "No events match your current filter."}
            actionText="View All Events"
            onAction={() => setFilter('all')}
          />
        ) : (
          <div className="row">
            {filteredEvents.map(event => {
              const isExpanded = expandedEvents[event.id];
              const rsvpCounts = getRSVPCounts(event.id);
              const isPastEvent = isEventPast(event.dateTime);
              
              return (
                <div key={event.id} className="col-12 mb-3">
                  <div className={`card border-0 shadow-sm h-100 ${isPastEvent ? 'opacity-75' : ''}`}>
                    <div 
                      className="card-header bg-white border-bottom-0 cursor-pointer event-card-compact"
                      onClick={() => toggleEventExpansion(event.id)}
                    >
                      <div className="d-flex justify-content-between align-items-center">
                        <div className="flex-grow-1">
                          <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-2">
                            <div className="d-flex align-items-center gap-3">
                              <h5 className="card-title mb-0 fw-bold text-dark">
                                {event.name}
                              </h5>
                              {isPastEvent && (
                                <span className="badge bg-secondary text-xs">
                                  <i className="fas fa-history me-1"></i>
                                  Past Event
                                </span>
                              )}
                            </div>
                            
                            <div className="d-flex flex-column flex-md-row gap-2 align-items-start align-items-md-center">
                              <div className="d-flex flex-wrap gap-1">
                                <span className="badge bg-info text-xs">
                                  <i className="fas fa-clock me-1"></i>
                                  {formatDateTime(event.dateTime)}
                                </span>
                                {event.location && (
                                  <span className="badge bg-info text-xs">
                                    <i className="fas fa-map-marker-alt me-1"></i>
                                    {event.location.length > 20 ? `${event.location.substring(0, 20)}...` : event.location}
                                  </span>
                                )}
                              </div>
                              
                              <div className="d-flex align-items-center gap-2">
                                {(role === 'admin' || role === 'super_admin') && (
                                  <span className="text-muted small d-none d-md-inline">
                                    {rsvpCounts.yes} going
                                  </span>
                                )}
                                
                                <div className="btn-group btn-group-sm" role="group">
                                  <button
                                    className={getRSVPButtonClass('yes', rsvps[event.id])}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleRSVP(event.id, 'yes');
                                    }}
                                    title="Attending"
                                  >
                                    <i className="fas fa-check"></i>
                                  </button>
                                  <button
                                    className={getRSVPButtonClass('maybe', rsvps[event.id])}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleRSVP(event.id, 'maybe');
                                    }}
                                    title="Maybe"
                                  >
                                    <i className="fas fa-question"></i>
                                  </button>
                                  <button
                                    className={getRSVPButtonClass('no', rsvps[event.id])}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleRSVP(event.id, 'no');
                                    }}
                                    title="Not Attending"
                                  >
                                    <i className="fas fa-times"></i>
                                  </button>
                                </div>
                                
                                <button className="btn btn-sm btn-outline-secondary">
                                  <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'}`}></i>
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {isExpanded && (
                      <div className="card-body event-card-expanded">
                        <div className="row">
                          <div className="col-md-8">
                            {event.description && (
                              <div className="mb-3">
                                <h6 className="fw-bold text-dark">
                                  <i className="fas fa-info-circle me-2"></i>
                                  Description
                                </h6>
                                <p className="text-muted">{event.description}</p>
                              </div>
                            )}
                            
                            <div className="mb-3">
                              <h6 className="fw-bold text-dark">
                                <i className="fas fa-calendar-alt me-2"></i>
                                Event Details
                              </h6>
                              <div className="row">
                                <div className="col-sm-6 mb-2">
                                  <strong>Date & Time:</strong><br />
                                  <span className="text-muted">{formatDateTime(event.dateTime)}</span>
                                </div>
                                {event.location && (
                                  <div className="col-sm-6 mb-2">
                                    <strong>Location:</strong><br />
                                    <span className="text-muted">{event.location}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {(role === 'admin' || role === 'super_admin') && (
                            <div className="col-md-4">
                              <h6 className="fw-bold text-dark">
                                <i className="fas fa-users me-2"></i>
                                RSVP Summary
                              </h6>
                              <div className="mb-3">
                                <div className="d-flex justify-content-between align-items-center mb-1">
                                  <span className="text-success">
                                    <i className="fas fa-check me-1"></i>
                                    Attending
                                  </span>
                                  <span className="badge bg-success">{rsvpCounts.yes}</span>
                                </div>
                                <div className="d-flex justify-content-between align-items-center mb-1">
                                  <span className="text-warning">
                                    <i className="fas fa-question me-1"></i>
                                    Maybe
                                  </span>
                                  <span className="badge bg-warning">{rsvpCounts.maybe}</span>
                                </div>
                                <div className="d-flex justify-content-between align-items-center mb-1">
                                  <span className="text-danger">
                                    <i className="fas fa-times me-1"></i>
                                    Not Attending
                                  </span>
                                  <span className="badge bg-danger">{rsvpCounts.no}</span>
                                </div>
                                <div className="d-flex justify-content-between align-items-center">
                                  <span className="text-muted">
                                    <i className="fas fa-users me-1"></i>
                                    Total Responses
                                  </span>
                                  <span className="badge bg-secondary">{rsvpCounts.total}</span>
                                </div>
                              </div>
                              
                              {rsvpCounts.yes > 0 && (
                                <div>
                                  <h6 className="fw-bold text-success small">Attending Members:</h6>
                                  <div className="d-flex flex-wrap gap-1">
                                    {getUsersForEvent(event.id, 'yes').slice(0, 5).map(user => (
                                      <UserAvatar 
                                        key={user.id}
                                        user={user} 
                                        size="sm"
                                        showTooltip={true}
                                      />
                                    ))}
                                    {getUsersForEvent(event.id, 'yes').length > 5 && (
                                      <span className="badge bg-secondary small">
                                        +{getUsersForEvent(event.id, 'yes').length - 5} more
                                      </span>
                                    )}
                                  </div>
                                </div>
                              )}
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
      </div>
    </div>
  );
}

export default Events;
