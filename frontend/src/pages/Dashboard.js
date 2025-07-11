import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Spinner from '../components/Spinner';
import Toast from '../components/Toast';
import UserAvatar from '../components/UserAvatar';
import { useTheme } from '../contexts/ThemeContext';
import axios from 'axios';

function Dashboard() {
  const [events, setEvents] = useState([]);
  const [rsvps, setRsvps] = useState({});
  const [allRsvps, setAllRsvps] = useState({}); // Store all member responses
  const [sections, setSections] = useState([]); // Store sections
  const [allUsers, setAllUsers] = useState([]); // Store all users with section info
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const [filter, setFilter] = useState('upcoming'); // Default to 'upcoming', can be changed to 'all' or 'past'
  const [expandedEvents, setExpandedEvents] = useState({}); // Track which events are expanded
  const { orgThemeColor } = useTheme();
  const role = localStorage.getItem('role'); // Assuming role is stored in localStorage

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        
        // Get sections
        const resSections = await axios.get(`${process.env.REACT_APP_API_URL || ''}/api/admin/sections`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSections(resSections.data);
        
        // Get all users with section info
        const resUsers = await axios.get(`${process.env.REACT_APP_API_URL || ''}/api/admin/users/all`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAllUsers(resUsers.data);
        
        // Get all events
        const resEvents = await axios.get(`${process.env.REACT_APP_API_URL || ''}/api/events/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Sort events by date
        const sortedEvents = resEvents.data.sort((a, b) => new Date(a.date) - new Date(b.date));
        setEvents(sortedEvents);
        
        // Get user's RSVPs for all events and all member responses
        const rsvpMap = {};
        const allRsvpMap = {};
        for (const event of sortedEvents) {
          try {
            const res = await axios.get(`${process.env.REACT_APP_API_URL || ''}/api/events/${event.id}/rsvps`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            
            // Store all responses for this event
            allRsvpMap[event.id] = res.data;
            
            // Find the RSVP for the current user
            const username = localStorage.getItem('username');
            let status = null;
            for (const [rsvpStatus, users] of Object.entries(res.data)) {
              // Check if users array contains objects with username property
              const hasUserRsvp = users.some(user => 
                typeof user === 'object' ? user.username === username : user === username
              );
              if (hasUserRsvp) status = rsvpStatus;
            }
            rsvpMap[event.id] = status;
          } catch {
            rsvpMap[event.id] = null;
            allRsvpMap[event.id] = { Yes: [], No: [], Maybe: [] };
          }
        }
        setRsvps(rsvpMap);
        setAllRsvps(allRsvpMap);
      } catch (err) {
        setError('Failed to load events.');
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  const handleRSVP = async (eventId, rsvpStatus) => {
    try {
      const token = localStorage.getItem('token');
      // Capitalize the status to match backend format
      const capitalizedStatus = rsvpStatus.charAt(0).toUpperCase() + rsvpStatus.slice(1);
      
      await axios.post(`${process.env.REACT_APP_API_URL || ''}/api/events/${eventId}/rsvp`, 
        { status: capitalizedStatus }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRsvps({ ...rsvps, [eventId]: capitalizedStatus });
      setToast({ show: true, message: `RSVP updated to "${capitalizedStatus}"`, type: 'success' });
      
      // Refresh the RSVP data to get updated member responses
      const res = await axios.get(`${process.env.REACT_APP_API_URL || ''}/api/events/${eventId}/rsvps`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAllRsvps(prev => ({ ...prev, [eventId]: res.data }));
    } catch (error) {
      setToast({ show: true, message: 'Failed to update RSVP', type: 'danger' });
    }
  };

  // Helper function to get user's RSVP status for an event
  const getUserRsvpStatus = (user, eventId) => {
    const eventRsvps = allRsvps[eventId] || { Yes: [], No: [], Maybe: [] };
    
    for (const [status, users] of Object.entries(eventRsvps)) {
      const hasResponse = users.some(u => 
        typeof u === 'object' ? u.username === user.username : u === user.username
      );
      if (hasResponse) return status;
    }
    return null; // No response
  };

  // Helper function to get status background color
  const getStatusBgClass = (status) => {
    switch (status) {
      case 'Yes': return 'bg-success bg-opacity-10';
      case 'No': return 'bg-danger bg-opacity-10';
      case 'Maybe': return 'bg-warning bg-opacity-10';
      default: return 'bg-light'; // No response
    }
  };

  // Helper function to organize users by sections for RSVP display
  const organizeUsersBySection = (eventId) => {
    const sectionGroups = {};
    
    // Initialize section groups
    sections.forEach(section => {
      sectionGroups[section.id] = {
        name: section.name,
        users: []
      };
    });
    
    // Add unassigned section
    sectionGroups['unassigned'] = {
      name: 'Unassigned',
      users: []
    };
    
    // Add all users to their respective sections
    allUsers.forEach(user => {
      const rsvpStatus = getUserRsvpStatus(user, eventId);
      const userWithStatus = {
        ...user,
        rsvpStatus
      };
      
      if (user.section_id) {
        if (sectionGroups[user.section_id]) {
          sectionGroups[user.section_id].users.push(userWithStatus);
        }
      } else {
        sectionGroups['unassigned'].users.push(userWithStatus);
      }
    });
    
    // Remove empty sections
    Object.keys(sectionGroups).forEach(key => {
      if (sectionGroups[key].users.length === 0) {
        delete sectionGroups[key];
      }
    });
    
    return sectionGroups;
  };

  const isEventUpcoming = (eventDate) => {
    return new Date(eventDate) >= new Date().setHours(0, 0, 0, 0);
  };

  const toggleEventExpansion = (eventId) => {
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
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

  const getEventTypeIcon = (eventType) => {
    const icons = {
      'performance': '🎵',
      'rehearsal': '🎼',
      'meeting': '💼',
      'social': '🎉',
      'other': '📅'
    };
    return icons[eventType] || icons['other'];
  };

  const getEventTypeBadge = (eventType) => {
    const colors = {
      'performance': 'danger',
      'rehearsal': 'primary',
      'meeting': 'warning',
      'social': 'success',
      'other': 'secondary'
    };
    return colors[eventType] || colors['other'];
  };

  const getRsvpSummary = (eventId) => {
    const responses = allRsvps[eventId];
    if (!responses) {
      return { yes: [], no: [], maybe: [], total: 0 };
    }
    
    // Handle the backend format which uses capital letters
    // Ensure arrays are always returned, even if undefined
    const yes = Array.isArray(responses.Yes) ? responses.Yes : [];
    const no = Array.isArray(responses.No) ? responses.No : [];
    const maybe = Array.isArray(responses.Maybe) ? responses.Maybe : [];
    
    const total = yes.length + no.length + maybe.length;
    return { yes, no, maybe, total };
  };

  const filteredEvents = events.filter(event => {
    switch (filter) {
      case 'upcoming':
        return isEventUpcoming(event.date);
      case 'past':
        return !isEventUpcoming(event.date);
      default:
        return true;
    }
  });

  const upcomingCount = events.filter(event => isEventUpcoming(event.date)).length;
  const pastCount = events.length - upcomingCount;

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="container mt-4 text-center">
          <Spinner size={40} />
          <div className="mt-3 text-muted">Loading events...</div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="container mt-4">
          <div className="alert alert-danger">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {error}
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        {/* Header */}
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4">
          <div>
            <h2 className="mb-1">
              <i className="bi bi-calendar-event me-2" style={{ color: orgThemeColor }}></i>
              My Events
            </h2>
            <p className="text-muted mb-0">Manage your event attendance and stay updated</p>
          </div>
          
          {/* Event Stats */}
          <div className="d-flex gap-2 mt-3 mt-md-0">
            <div className="text-center">
              <div className="fw-bold" style={{ color: orgThemeColor }}>{upcomingCount}</div>
              <div className="small text-muted">Upcoming</div>
            </div>
            <div className="vr"></div>
            <div className="text-center">
              <div className="fw-bold text-muted">{pastCount}</div>
              <div className="small text-muted">Past</div>
            </div>
          </div>
        </div>

        {/* Quick Actions - Phase 2 Features */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="card border-0 shadow-sm">
              <div className="card-body">
                <h6 className="card-title mb-3">
                  <i className="bi bi-lightning me-2" style={{ color: orgThemeColor }}></i>
                  Quick Actions
                </h6>
                <div className="row g-2">
                  <div className="col-md-3">
                    <Link to="/messaging" className="btn btn-outline-primary w-100">
                      <i className="bi bi-chat-dots me-2"></i>
                      Messages
                    </Link>
                  </div>
                  <div className="col-md-3">
                    <Link to="/substitution" className="btn btn-outline-success w-100">
                      <i className="bi bi-person-plus me-2"></i>
                      Find Substitute
                    </Link>
                  </div>
                  <div className="col-md-3">
                    <Link to="/polls" className="btn btn-outline-info w-100">
                      <i className="bi bi-bar-chart me-2"></i>
                      Quick Polls
                    </Link>
                  </div>
                  {role === 'Admin' && (
                    <div className="col-md-3">
                      <Link to="/bulk-operations" className="btn btn-outline-warning w-100">
                        <i className="bi bi-stack me-2"></i>
                        Bulk Operations
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <ul className="nav nav-pills mb-4" role="tablist">
          <li className="nav-item" role="presentation">
            <button 
              className={`nav-link ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
              type="button"
            >
              All Events
              <span className="badge bg-light text-dark ms-2">{events.length}</span>
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button 
              className={`nav-link ${filter === 'upcoming' ? 'active' : ''}`}
              onClick={() => setFilter('upcoming')}
              type="button"
            >
              Upcoming
              <span className="badge bg-light text-dark ms-2">{upcomingCount}</span>
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button 
              className={`nav-link ${filter === 'past' ? 'active' : ''}`}
              onClick={() => setFilter('past')}
              type="button"
            >
              Past
              <span className="badge bg-light text-dark ms-2">{pastCount}</span>
            </button>
          </li>
        </ul>

        {/* Events List */}
        <div className="row">
          {filteredEvents.length === 0 ? (
            <div className="col-12">
              <div className="text-center py-5">
                <i className="bi bi-calendar-x" style={{ fontSize: '3rem', color: orgThemeColor }}></i>
                <h4 className="mt-3 text-muted">No events found</h4>
                <p className="text-muted">
                  {filter === 'upcoming' ? 'No upcoming events scheduled' : 
                   filter === 'past' ? 'No past events to show' : 
                   'No events available'}
                </p>
              </div>
            </div>
          ) : (
            filteredEvents.map(event => {
              const isUpcoming = isEventUpcoming(event.date);
              const eventRsvp = rsvps[event.id];
              const rsvpSummary = getRsvpSummary(event.id) || { yes: [], no: [], maybe: [], total: 0 };
              const isExpanded = expandedEvents[event.id];
              
              return (
                <div key={event.id} className="col-12 mb-4">
                  <div className={`card shadow-sm ${!isUpcoming ? 'border-muted' : ''}`}>
                    {/* Card Header */}
                    <div className="card-header d-flex justify-content-between align-items-center">
                      <div className="d-flex align-items-center">
                        <span className="me-2" style={{ fontSize: '1.2em' }}>
                          {getEventTypeIcon(event.event_type)}
                        </span>
                        <h5 className="mb-0 fw-bold">{event.title}</h5>
                        <span className={`badge bg-${getEventTypeBadge(event.event_type)} ms-2`}>
                          {event.event_type || 'other'}
                        </span>
                        {!isUpcoming && (
                          <span className="badge bg-secondary ms-2">Past Event</span>
                        )}
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <span className={`badge ${
                          eventRsvp === 'Yes' ? 'bg-success' :
                          eventRsvp === 'No' ? 'bg-danger' :
                          eventRsvp === 'Maybe' ? 'bg-warning text-dark' :
                          'bg-secondary'
                        }`}>
                          Your RSVP: {eventRsvp || 'No response'}
                        </span>
                        <button
                          className="btn btn-sm btn-outline-secondary"
                          onClick={() => toggleEventExpansion(event.id)}
                        >
                          {isExpanded ? 'Less Info' : 'More Info'}
                          <i className={`bi bi-chevron-${isExpanded ? 'up' : 'down'} ms-1`}></i>
                        </button>
                      </div>
                    </div>

                    <div className="card-body">
                      <div className="row">
                        {/* Left Column - Event Details */}
                        <div className="col-md-6">
                          <p className="card-text mb-3">{event.description}</p>
                          
                          <div className="mb-2">
                            <i className="bi bi-calendar3 me-2 text-muted"></i>
                            <strong>Date:</strong> {new Date(event.date).toLocaleDateString('en-US', {
                              weekday: 'long',
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </div>
                          
                          {event.time && (
                            <div className="mb-2">
                              <i className="bi bi-clock me-2 text-muted"></i>
                              <strong>Time:</strong> {formatTime(event.time)}
                            </div>
                          )}
                          
                          {event.location_address && (
                            <div className="mb-2">
                              <i className="bi bi-geo-alt me-2 text-muted"></i>
                              <strong>Location:</strong> {event.location_address}
                              {event.lat && event.lng && (
                                <a
                                  href={`https://www.google.com/maps?q=${event.lat},${event.lng}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="ms-2 text-decoration-none"
                                >
                                  <i className="bi bi-box-arrow-up-right"></i> View on Map
                                </a>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Right Column - Map and RSVP Summary */}
                        <div className="col-md-6">
                          {/* Small Map Preview */}
                          {event.lat && event.lng && (
                            <div className="mb-3">
                              <h6 className="mb-2">
                                <i className="bi bi-map me-2"></i>
                                Location Map
                              </h6>
                              <div className="border rounded" style={{ height: '120px', overflow: 'hidden' }}>
                                {process.env.REACT_APP_GOOGLE_MAPS_API_KEY ? (
                                  <iframe
                                    src={`https://www.google.com/maps/embed/v1/place?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&q=${event.lat},${event.lng}&zoom=14`}
                                    width="100%"
                                    height="120"
                                    style={{ border: 0 }}
                                    allowFullScreen=""
                                    loading="lazy"
                                    referrerPolicy="no-referrer-when-downgrade"
                                    title={`Map for ${event.title}`}
                                  ></iframe>
                                ) : (
                                  <div className="d-flex align-items-center justify-content-center h-100 bg-light text-muted">
                                    <div className="text-center">
                                      <i className="bi bi-map" style={{ fontSize: '1.5rem' }}></i>
                                      <div className="mt-1">
                                        <small>Google Maps API key required</small>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </div>
                              <div className="mt-1 text-center">
                                <a
                                  href={`https://www.google.com/maps?q=${event.lat},${event.lng}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="btn btn-sm btn-outline-primary"
                                >
                                  <i className="bi bi-map me-1"></i>
                                  Open in Google Maps
                                </a>
                              </div>
                            </div>
                          )}

                          <h6 className="mb-3">
                            <i className="bi bi-people me-2"></i>
                            Member Responses ({rsvpSummary.total || 0} total)
                          </h6>
                          
                          <div className="row g-2 mb-3">
                            <div className="col-4">
                              <div className="card bg-success bg-opacity-10 border-success">
                                <div className="card-body text-center py-2">
                                  <div className="fw-bold text-success">{(rsvpSummary.yes || []).length}</div>
                                  <div className="small text-success">Going</div>
                                </div>
                              </div>
                            </div>
                            <div className="col-4">
                              <div className="card bg-warning bg-opacity-10 border-warning">
                                <div className="card-body text-center py-2">
                                  <div className="fw-bold text-warning">{(rsvpSummary.maybe || []).length}</div>
                                  <div className="small text-warning">Maybe</div>
                                </div>
                              </div>
                            </div>
                            <div className="col-4">
                              <div className="card bg-danger bg-opacity-10 border-danger">
                                <div className="card-body text-center py-2">
                                  <div className="fw-bold text-danger">{(rsvpSummary.no || []).length}</div>
                                  <div className="small text-danger">Not Going</div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* RSVP Buttons */}
                          {isUpcoming && (
                            <div className="btn-group w-100" role="group">
                              {["yes", "maybe", "no"].map(option => {
                                const capitalizedOption = option.charAt(0).toUpperCase() + option.slice(1);
                                return (
                                  <button
                                    key={option}
                                    type="button"
                                    className={`btn ${eventRsvp === capitalizedOption ? 
                                      (option === 'yes' ? 'btn-success' : 
                                       option === 'no' ? 'btn-danger' : 'btn-warning') :
                                      'btn-outline-secondary'
                                    }`}
                                    onClick={() => handleRSVP(event.id, option)}
                                  >
                                    <i className={`bi bi-${
                                      option === 'yes' ? 'check' :
                                      option === 'no' ? 'x' : 'question'
                                    }-circle me-1`}></i>
                                    {option === 'yes' ? 'Yes' : option === 'no' ? 'No' : 'Maybe'}
                                  </button>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Expanded Details */}
                      {isExpanded && (
                        <div className="mt-4">
                          <hr />
                          <div className="row">
                            {/* Section-Organized Member List */}
                            <div className="col-md-6">
                              <h6>Member Responses by Section</h6>
                              
                              {(() => {
                                const sectionGroups = organizeUsersBySection(event.id);
                                return Object.entries(sectionGroups).map(([sectionId, section]) => (
                                  <div key={sectionId} className="mb-4">
                                    <h6 className="text-primary border-bottom pb-1">
                                      <i className="bi bi-music-note-beamed me-2"></i>
                                      {section.name}
                                    </h6>
                                    
                                    <div className="ms-3">
                                      {section.users.map(user => (
                                        <div 
                                          key={user.username} 
                                          className={`d-flex align-items-center justify-content-between p-2 mb-1 rounded ${getStatusBgClass(user.rsvpStatus)}`}
                                        >
                                          <div className="d-flex align-items-center">
                                            <UserAvatar
                                              user={user}
                                              size={32}
                                              className="me-2"
                                            />
                                            <span className="fw-medium">
                                              {user.display_name}
                                            </span>
                                          </div>
                                          <span className={`badge ${
                                            user.rsvpStatus === 'Yes' ? 'bg-success' :
                                            user.rsvpStatus === 'No' ? 'bg-danger' :
                                            user.rsvpStatus === 'Maybe' ? 'bg-warning text-dark' :
                                            'bg-secondary'
                                          }`}>
                                            {user.rsvpStatus === 'Yes' && <><i className="bi bi-check-circle me-1"></i>Going</>}
                                            {user.rsvpStatus === 'No' && <><i className="bi bi-x-circle me-1"></i>Not Going</>}
                                            {user.rsvpStatus === 'Maybe' && <><i className="bi bi-question-circle me-1"></i>Maybe</>}
                                            {!user.rsvpStatus && <><i className="bi bi-clock me-1"></i>No Response</>}
                                          </span>
                                        </div>
                                      ))}
                                      
                                      {section.users.length === 0 && (
                                        <div className="text-muted fst-italic">
                                          No members in this section
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                ));
                              })()}
                            </div>

                            {/* Map */}
                            {event.lat && event.lng && (
                              <div className="col-md-6">
                                <h6>Location Map</h6>
                                <div className="border rounded" style={{ height: '200px', overflow: 'hidden' }}>
                                  {process.env.REACT_APP_GOOGLE_MAPS_API_KEY ? (
                                    <iframe
                                      src={`https://www.google.com/maps/embed/v1/place?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&q=${event.lat},${event.lng}&zoom=15`}
                                      width="100%"
                                      height="200"
                                      style={{ border: 0 }}
                                      allowFullScreen=""
                                      loading="lazy"
                                      referrerPolicy="no-referrer-when-downgrade"
                                      title={`Map for ${event.title}`}
                                    ></iframe>
                                  ) : (
                                    <div className="d-flex align-items-center justify-content-center h-100 bg-light text-muted">
                                      <div className="text-center">
                                        <i className="bi bi-map" style={{ fontSize: '2rem' }}></i>
                                        <div className="mt-2">
                                          <small>Google Maps API key required</small>
                                          <br />
                                          <small>See GOOGLE_MAPS_SETUP.md</small>
                                        </div>
                                      </div>
                                    </div>
                                  )}
                                </div>
                                <div className="mt-2 text-center">
                                  <a
                                    href={`https://www.google.com/maps?q=${event.lat},${event.lng}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="btn btn-sm btn-outline-primary"
                                  >
                                    <i className="bi bi-map me-1"></i>
                                    Open in Google Maps
                                  </a>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <Toast 
          show={toast.show} 
          message={toast.message} 
          type={toast.type} 
          onClose={() => setToast(prev => ({ ...prev, show: false }))} 
        />
      </div>
    </>
  );
}

export default Dashboard;
