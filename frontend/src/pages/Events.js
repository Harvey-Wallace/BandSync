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
  const [filter, setFilter] = useState('upcoming'); // Default to 'upcoming'
  const [expandedEvents, setExpandedEvents] = useState({}); // Track which events are expanded
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

        // Fetch additional data for admin users
        if (role === 'admin' || role === 'super_admin') {
          try {
            const organizationId = localStorage.getItem('organization_id');
            console.log('Admin data fetch attempt:', { role, organizationId });
            if (organizationId) {
              const [allRsvpsResponse, sectionsResponse, usersResponse] = await Promise.all([
                axios.get(`${getApiUrl()}/rsvps/all/${organizationId}`, {
                  headers: { Authorization: `Bearer ${token}` }
                }),
                axios.get(`${getApiUrl()}/sections/organization/${organizationId}`, {
                  headers: { Authorization: `Bearer ${token}` }
                }),
                axios.get(`${getApiUrl()}/users/organization/${organizationId}`, {
                  headers: { Authorization: `Bearer ${token}` }
                })
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
              console.log('Admin data loaded:', { 
                allRsvps: allRsvpsMap, 
                sections: sectionsResponse.data?.length || 0, 
                users: usersResponse.data?.length || 0 
              });
            }
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
      total: Object.keys(eventRsvps).length
    };
    
    Object.values(eventRsvps).forEach(status => {
      if (counts.hasOwnProperty(status)) {
        counts[status]++;
      }
    });
    
    console.log(`RSVP counts for event ${eventId}:`, counts, 'Raw data:', eventRsvps);
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
                {/* Temporary Debug Info */}
                <div className="text-muted small">
                  Role: {role || 'none'} | OrgID: {localStorage.getItem('organization_id') || 'none'}
                </div>
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
                                <span className="badge bg-secondary text-xs">Past Event</span>
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
                                
                                {!isPastEvent && (
                                  <div className="btn-group" role="group">
                                    <button
                                      className={getRSVPButtonClass('yes', rsvps[event.id])}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleRSVP(event.id, 'yes');
                                      }}
                                    >
                                      <i className="fas fa-check me-1"></i>
                                      Going
                                    </button>
                                    <button
                                      className={getRSVPButtonClass('maybe', rsvps[event.id])}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleRSVP(event.id, 'maybe');
                                      }}
                                    >
                                      <i className="fas fa-question me-1"></i>
                                      Maybe
                                    </button>
                                    <button
                                      className={getRSVPButtonClass('no', rsvps[event.id])}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleRSVP(event.id, 'no');
                                      }}
                                    >
                                      <i className="fas fa-times me-1"></i>
                                      Can't Go
                                    </button>
                                  </div>
                                )}
                                
                                <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'} text-muted ms-2`}></i>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {event.description && (
                      <div className="card-body border-bottom">
                        <p className="card-text text-muted mb-0">{event.description}</p>
                      </div>
                    )}

                    {isExpanded && (
                      <div className="card-body border-top bg-light">
                        {/* Event Details Section */}
                        <div className="row">
                          {/* Location with Map */}
                          {event.location && (
                            <div className="col-md-6 mb-3">
                              <h6 className="fw-bold text-dark mb-2">
                                <i className="fas fa-map-marker-alt me-2 text-primary"></i>
                                Location
                              </h6>
                              <p className="text-muted mb-2">{event.location}</p>
                              <div className="mt-2">
                                <iframe
                                  width="100%"
                                  height="200"
                                  style={{ border: 0, borderRadius: '8px' }}
                                  src={`https://www.google.com/maps/embed/v1/place?key=${getGoogleMapsApiKey()}&q=${encodeURIComponent(event.location)}`}
                                  allowFullScreen
                                ></iframe>
                              </div>
                            </div>
                          )}
                          
                          {/* RSVP Responses for Admins */}
                          {(role === 'admin' || role === 'super_admin') && (
                            <div className="col-md-6 mb-3">
                              <h6 className="fw-bold text-dark mb-2">
                                <i className="fas fa-users me-2 text-primary"></i>
                                Responses ({rsvpCounts.total})
                              </h6>
                              
                              {console.log(`Rendering responses for event ${event.id}:`, { role, rsvpCounts, allRsvps: allRsvps[event.id] })}
                              
                              {/* Temporary Debug Info */}
                              <div className="alert alert-info small mb-2">
                                <strong>Debug:</strong> Role: {role}, Total RSVP Data Keys: {Object.keys(allRsvps).length}, 
                                Users: {allUsers.length}, This Event RSVPs: {Object.keys(allRsvps[event.id] || {}).length}
                              </div>
                              
                              {rsvpCounts.total > 0 ? (
                                <div className="row g-2">
                                  <div className="col-4">
                                    <div className="text-center p-2 bg-success bg-opacity-10 rounded">
                                      <div className="h5 mb-1 text-success">{rsvpCounts.yes}</div>
                                      <small className="text-success">Going</small>
                                    </div>
                                  </div>
                                  <div className="col-4">
                                    <div className="text-center p-2 bg-warning bg-opacity-10 rounded">
                                      <div className="h5 mb-1 text-warning">{rsvpCounts.maybe}</div>
                                      <small className="text-warning">Maybe</small>
                                    </div>
                                  </div>
                                  <div className="col-4">
                                    <div className="text-center p-2 bg-danger bg-opacity-10 rounded">
                                      <div className="h5 mb-1 text-danger">{rsvpCounts.no}</div>
                                      <small className="text-danger">Can't Go</small>
                                    </div>
                                  </div>
                                </div>
                              ) : (
                                <p className="text-muted small">No responses yet</p>
                              )}
                              
                              {getUsersForEvent(event.id, 'yes').length > 0 && (
                                <div className="mt-3">
                                  <small className="text-muted d-block mb-2">Who's going:</small>
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
