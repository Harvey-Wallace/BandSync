import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import { 
  LoadingSpinner, 
  DataLoadingState, 
  ErrorState, 
  EmptyState 
} from '../components/LoadingComponents';
import { 
  ResponsiveStatsGrid, 
  ResponsiveCardGrid,
  ResponsiveActionBar
} from '../components/ResponsiveComponents';
import UserAvatar from '../components/UserAvatar';
import { useTheme } from '../contexts/ThemeContext';
import { getGoogleMapsApiKey } from '../config/constants';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

function Dashboard() {
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
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        // Get sections
        const resSections = await axios.get(`${apiUrl}/admin/sections`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSections(resSections.data);
        
        // Get all users with section info
        const resUsers = await axios.get(`${apiUrl}/admin/users/all`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAllUsers(resUsers.data);
        
        // Get all events
        const resEvents = await axios.get(`${apiUrl}/events/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        // Sort events by date
        const sortedEvents = resEvents.data.sort((a, b) => new Date(a.date) - new Date(b.date));
        setEvents(sortedEvents);
        
        // Get user's RSVP status from the new rsvp_stats format
        const rsvpMap = {};
        const allRsvpMap = {};
        const username = localStorage.getItem('username');
        
        for (const event of sortedEvents) {
          try {
            // Use the rsvp_stats from events API which includes privacy logic
            if (event.rsvp_stats && event.rsvp_stats.responses) {
              // Find current user's RSVP status
              const userRsvp = event.rsvp_stats.responses.find(response => 
                response.name === username || response.username === username
              );
              rsvpMap[event.id] = userRsvp ? userRsvp.status : null;
              
              // Organize responses by status for backward compatibility
              const groupedResponses = { Yes: [], No: [], Maybe: [] };
              event.rsvp_stats.responses.forEach(response => {
                if (groupedResponses[response.status]) {
                  groupedResponses[response.status].push({
                    username: response.name,
                    name: response.name,
                    display_name: response.name,
                    section_id: null,
                    section_name: response.section || 'Unassigned'
                  });
                }
              });
              
              // Add privacy metadata - this contains the correct behavior
              groupedResponses._privacy = {
                can_view_details: event.rsvp_stats.can_view_details,
                privacy_message: event.rsvp_stats.privacy_message
              };
              
              allRsvpMap[event.id] = groupedResponses;
            } else {
              // Fallback: make separate API call for events without rsvp_stats
              const res = await axios.get(`${apiUrl}/events/${event.id}/rsvps`, {
                headers: { Authorization: `Bearer ${token}` }
              });
              
              // Store all responses for this event
              allRsvpMap[event.id] = res.data;
              
              // Find the RSVP for the current user
              let status = null;
              for (const [rsvpStatus, users] of Object.entries(res.data)) {
                // Skip privacy metadata
                if (rsvpStatus === '_privacy') continue;
                
                // Check if users array contains objects with username property
                const hasUserRsvp = users.some(user => 
                  typeof user === 'object' ? user.username === username : user === username
                );
                if (hasUserRsvp) status = rsvpStatus;
              }
              rsvpMap[event.id] = status;
            }
          } catch {
            rsvpMap[event.id] = null;
            allRsvpMap[event.id] = { 
              Yes: [], 
              No: [], 
              Maybe: [],
              _privacy: {
                can_view_details: false,
                privacy_message: "Unable to load RSVP data"
              }
            };
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
      const apiUrl = getApiUrl();
      // Capitalize the status to match backend format
      const capitalizedStatus = rsvpStatus.charAt(0).toUpperCase() + rsvpStatus.slice(1);
      
      await axios.post(`${apiUrl}/events/${eventId}/rsvp`, 
        { status: capitalizedStatus }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRsvps({ ...rsvps, [eventId]: capitalizedStatus });
      showSuccessMessage(`RSVP updated to "${capitalizedStatus}"`);
      
      // Refresh the RSVP data - check if we have rsvp_stats or need to use legacy endpoint
      const currentEvent = events.find(e => e.id === eventId);
      if (currentEvent && currentEvent.rsvp_stats) {
        // Refresh the entire events list to get updated rsvp_stats
        const resEvents = await axios.get(`${apiUrl}/events/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const sortedEvents = resEvents.data.sort((a, b) => new Date(a.date) - new Date(b.date));
        setEvents(sortedEvents);
        
        // Update RSVP data from the refreshed events
        const updatedEvent = sortedEvents.find(e => e.id === eventId);
        if (updatedEvent && updatedEvent.rsvp_stats && updatedEvent.rsvp_stats.responses) {
          const groupedResponses = { Yes: [], No: [], Maybe: [] };
          updatedEvent.rsvp_stats.responses.forEach(response => {
            if (groupedResponses[response.status]) {
              groupedResponses[response.status].push({
                username: response.name,
                name: response.name,
                display_name: response.name,
                section_id: null,
                section_name: response.section || 'Unassigned'
              });
            }
          });
          
          groupedResponses._privacy = {
            can_view_details: updatedEvent.rsvp_stats.can_view_details,
            privacy_message: updatedEvent.rsvp_stats.privacy_message
          };
          
          setAllRsvps(prev => ({ ...prev, [eventId]: groupedResponses }));
        }
      } else {
        // Fallback to legacy endpoint
        const res = await axios.get(`${apiUrl}/events/${eventId}/rsvps`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAllRsvps(prev => ({ ...prev, [eventId]: res.data }));
      }
    } catch (error) {
      showErrorMessage('Failed to update RSVP');
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
    const eventRsvps = allRsvps[eventId] || { Yes: [], No: [], Maybe: [] };
    
    // Check if user can view details based on privacy settings
    const privacyData = eventRsvps._privacy;
    
    if (privacyData && !privacyData.can_view_details) {
      // User cannot see detailed RSVP list, return empty sections
      return {};
    }
    
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
    
    // Process all RSVP responses and organize by sections
    Object.entries(eventRsvps).forEach(([status, users]) => {
      // Skip privacy metadata
      if (status === '_privacy') return;
      
      users.forEach(user => {
        const userWithStatus = {
          ...user,
          rsvpStatus: status
        };
        
        // Use the section information from the RSVP data itself
        if (user.section_id) {
          // Find or create section group
          if (!sectionGroups[user.section_id]) {
            sectionGroups[user.section_id] = {
              name: user.section_name || `Section ${user.section_id}`,
              users: []
            };
          }
          sectionGroups[user.section_id].users.push(userWithStatus);
        } else {
          sectionGroups['unassigned'].users.push(userWithStatus);
        }
      });
    });
    
    // Also add users who haven't responded yet
    allUsers.forEach(user => {
      // Check if this user already has an RSVP response
      const hasResponse = Object.values(eventRsvps).some(statusUsers => 
        statusUsers.some(rsvpUser => rsvpUser.username === user.username)
      );
      
      if (!hasResponse) {
        const userWithStatus = {
          ...user,
          rsvpStatus: null // No response
        };
        
        if (user.section_id) {
          if (!sectionGroups[user.section_id]) {
            sectionGroups[user.section_id] = {
              name: user.section_name || `Section ${user.section_id}`,
              users: []
            };
          }
          sectionGroups[user.section_id].users.push(userWithStatus);
        } else {
          sectionGroups['unassigned'].users.push(userWithStatus);
        }
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
    const type = eventType ? eventType.toLowerCase() : 'other';
    const icons = {
      'performance': '🎵',
      'rehearsal': '🎼',
      'concert': '🎵',
      'committee meeting': '💼',
      'meeting': '💼',
      'agm': '💼',
      'social': '🎉',
      'other': '📅'
    };
    return icons[type] || icons['other'];
  };

  const getEventTypeBadge = (eventType) => {
    const type = eventType ? eventType.toLowerCase() : 'other';
    const colors = {
      'performance': 'danger',
      'rehearsal': 'primary',
      'concert': 'danger',
      'committee meeting': 'warning',
      'meeting': 'warning',
      'agm': 'warning',
      'social': 'success',
      'other': 'secondary'
    };
    return colors[type] || colors['other'];
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

  // Get RSVP stats from the new backend format (X of Y display)
  const getRsvpStats = (event) => {
    if (event.rsvp_stats) {
      // Use the backend stats directly - these are always correct regardless of privacy settings
      return event.rsvp_stats;
    }
    // Fallback to old format if new stats not available
    const rsvpSummary = getRsvpSummary(event.id);
    return {
      total_responses: rsvpSummary.total,
      total_users: rsvpSummary.total, // Fallback - not accurate
      yes_count: rsvpSummary.yes.length,
      no_count: rsvpSummary.no.length,
      maybe_count: rsvpSummary.maybe.length,
      no_response_count: 0
    };
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
        <NotificationSystem />
        <div className="container-fluid mt-4 px-3">
          <DataLoadingState type="skeleton" message="Loading your events..." />
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <NotificationSystem />
        <div className="container-fluid mt-4 px-3">
          <ErrorState 
            message={error} 
            onRetry={() => window.location.reload()} 
          />
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <NotificationSystem />
      <div className="container-fluid mt-4 px-3">
        <ResponsiveActionBar
          title="My Events"
          subtitle="Manage your event attendance and stay updated"
          icon="calendar-event"
          actions={[
            {
              label: 'View All Events',
              shortLabel: 'All',
              icon: 'calendar3',
              variant: filter === 'all' ? 'btn-primary' : 'btn-outline-primary',
              onClick: () => setFilter('all')
            },
            {
              label: 'Upcoming Only',
              shortLabel: 'Upcoming',
              icon: 'clock',
              variant: filter === 'upcoming' ? 'btn-primary' : 'btn-outline-primary',
              onClick: () => setFilter('upcoming')
            },
            {
              label: 'Past Events',
              shortLabel: 'Past',
              icon: 'calendar-check',
              variant: filter === 'past' ? 'btn-primary' : 'btn-outline-primary',
              onClick: () => setFilter('past')
            }
          ]}
        />

        {/* Enhanced Event Stats */}
        <ResponsiveStatsGrid
          stats={[
            {
              label: 'Upcoming Events',
              value: upcomingCount,
              subtitle: 'Events to attend',
              icon: 'calendar-plus'
            },
            {
              label: 'Past Events',
              value: pastCount,
              subtitle: 'Previously attended',
              icon: 'calendar-check'
            },
            {
              label: 'My RSVPs',
              value: Object.keys(rsvps).length,
              subtitle: 'Total responses',
              icon: 'check2-circle'
            },
            {
              label: 'Status',
              value: events.length > 0 ? 'Active' : 'No Events',
              subtitle: role === 'Admin' ? 'Admin access' : 'Member access',
              icon: role === 'Admin' ? 'shield-check' : 'person-check'
            }
          ]}
          className="mb-4"
        />

        {/* Quick Actions */}
        <div className="card card-enhanced mb-4">
          <div className="card-body">
            <h6 className="card-title mb-3">
              <i className="bi bi-lightning me-2"></i>
              Quick Actions
            </h6>
            <div className="d-flex flex-column flex-md-row gap-2">
              <a href="/messaging" className="btn btn-outline-primary flex-fill mb-2 mb-md-0">
                <i className="bi bi-chat-dots me-1"></i>Messages
              </a>
              <a href="/substitution" className="btn btn-outline-success flex-fill mb-2 mb-md-0">
                <i className="bi bi-person-plus me-1"></i>Find Substitute
              </a>
              <a href="/polls" className="btn btn-outline-info flex-fill mb-2 mb-md-0">
                <i className="bi bi-bar-chart me-1"></i>Quick Polls
              </a>
              {(role === 'Admin' || localStorage.getItem('super_admin') === 'true') && (
                <a href="/admin" className="btn btn-outline-warning flex-fill mb-2 mb-md-0">
                  <i className="bi bi-gear me-1"></i>Admin Panel
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Events List */}
        <div className="row">
          {filteredEvents.length === 0 ? (
            <div className="col-12">
              <EmptyState
                icon="calendar-x"
                title="No events found"
                message={
                  filter === 'upcoming' 
                    ? 'No upcoming events scheduled' 
                    : filter === 'past' 
                    ? 'No past events to display'
                    : 'No events available'
                }
                action={{
                  label: 'View All Events',
                  onClick: () => setFilter('all')
                }}
              />
            </div>
          ) : (
            filteredEvents.map(event => {
              const isUpcoming = isEventUpcoming(event.date);
              const eventRsvp = rsvps[event.id];
              const rsvpSummary = getRsvpSummary(event.id) || { yes: [], no: [], maybe: [], total: 0 };
              const isExpanded = expandedEvents[event.id];
              
              return (
                <div key={event.id} className="col-12 mb-3">
                  <div className={`card shadow-sm event-card-compact ${!isUpcoming ? 'border-muted event-past' : 'event-upcoming'}`}>
                    {/* Collapsed View - Always Visible */}
                    <div className="card-header d-flex justify-content-between align-items-center py-2">
                      <div className="d-flex align-items-center flex-grow-1">
                        <span className="me-2" style={{ fontSize: '1.1em' }}>
                          {getEventTypeIcon(event.type)}
                        </span>
                        <div className="d-flex flex-column flex-md-row align-items-md-center flex-grow-1">
                          <h6 className="mb-0 fw-bold me-md-3">{event.title}</h6>
                          <div className="d-flex align-items-center gap-2 flex-wrap">
                            <span className="badge bg-secondary text-xs">
                              {new Date(event.date).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric'
                              })}
                              {/* Show main time info - prefer start_time, then arrive_by_time, then legacy time */}
                              {(event.start_time || event.arrive_by_time || event.time) && 
                                ` • ${formatTime(event.start_time || event.arrive_by_time || event.time)}`}
                            </span>
                            {event.location_address && (
                              <span className="badge bg-info text-xs">
                                <i className="bi bi-geo-alt me-1"></i>
                                {event.location_address.length > 20 ? 
                                  event.location_address.substring(0, 20) + '...' : 
                                  event.location_address}
                              </span>
                            )}
                            {event.is_cancelled && (
                              <span className="badge bg-danger text-xs">
                                <i className="bi bi-x-circle me-1"></i>
                                CANCELLED
                              </span>
                            )}
                            <span className={`badge bg-${getEventTypeBadge(event.type)} text-xs`}>
                              {event.type ? event.type.charAt(0).toUpperCase() + event.type.slice(1) : 'Rehearsal'}
                            </span>
                            {!isUpcoming && (
                              <span className="badge bg-secondary text-xs">Past</span>
                            )}
                            {!event.is_cancelled && (
                              <span className={`badge text-xs ${
                                eventRsvp === 'Yes' ? 'bg-success' :
                                eventRsvp === 'No' ? 'bg-danger' :
                                eventRsvp === 'Maybe' ? 'bg-warning text-dark' :
                                'bg-outline-secondary'
                              }`}>
                                {eventRsvp || 'No RSVP'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <small className="text-muted d-none d-md-inline">
                          {(() => {
                            const stats = getRsvpStats(event);
                            return `${stats.total_responses} of ${stats.total_users}`;
                          })()}
                        </small>
                        
                        {/* Quick RSVP buttons - only for upcoming events */}
                        {isUpcoming && !event.is_cancelled && (
                          <div className="btn-group me-2" role="group">
                            {["yes", "maybe", "no"].map(option => {
                              const capitalizedOption = option.charAt(0).toUpperCase() + option.slice(1);
                              return (
                                <button
                                  key={option}
                                  type="button"
                                  className={`btn btn-sm ${eventRsvp === capitalizedOption ? 
                                    (option === 'yes' ? 'btn-success' : 
                                     option === 'no' ? 'btn-danger' : 'btn-warning') :
                                    'btn-outline-secondary'
                                  }`}
                                  onClick={() => handleRSVP(event.id, option)}
                                  title={`RSVP ${option === 'yes' ? 'Yes' : option === 'no' ? 'No' : 'Maybe'}`}
                                >
                                  <i className={`bi bi-${
                                    option === 'yes' ? 'check' :
                                    option === 'no' ? 'x' : 'question'
                                  }-circle`}></i>
                                </button>
                              );
                            })}
                          </div>
                        )}
                        
                        <button
                          className="btn btn-sm btn-outline-secondary"
                          onClick={() => toggleEventExpansion(event.id)}
                        >
                          <i className={`bi bi-${isExpanded ? 'dash' : 'plus'}`}></i>
                        </button>
                      </div>
                    </div>

                    {/* Expanded View - Only When Expanded */}
                    {isExpanded && (
                      <div className="card-body event-card-expanded">
                        <div className="row">
                          {/* Left Column - Event Details */}
                          <div className="col-md-6">
                            {event.is_cancelled && (
                              <div className="alert alert-danger mb-3">
                                <h6 className="alert-heading">
                                  <i className="bi bi-x-circle-fill me-2"></i>
                                  Event Cancelled
                                </h6>
                                <p className="mb-1">
                                  <strong>Reason:</strong> {event.cancellation_reason}
                                </p>
                                <hr className="my-2" />
                                <small className="text-muted">
                                  Cancelled on {event.cancelled_at ? new Date(event.cancelled_at).toLocaleDateString('en-US', {
                                    weekday: 'long',
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                  }) : 'Unknown date'}
                                  {event.canceller_name && ` by ${event.canceller_name}`}
                                </small>
                              </div>
                            )}
                            
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
                            
                            {/* Enhanced Timing Information - Single Line Display */}
                            {(event.arrive_by_time || event.start_time || event.end_time) && (
                              <div className="mb-2">
                                <i className="bi bi-clock me-2 text-muted"></i>
                                <strong>Timing:</strong>
                                <span className="ms-2">
                                  {event.arrive_by_time && (
                                    <span className="me-3">
                                      <span className="badge bg-info me-1">Arrive by</span>
                                      {formatTime(event.arrive_by_time)}
                                    </span>
                                  )}
                                  {event.start_time && (
                                    <span className="me-3">
                                      <span className="badge bg-primary me-1">Start</span>
                                      {formatTime(event.start_time)}
                                    </span>
                                  )}
                                  {event.end_time && (
                                    <span>
                                      <span className="badge bg-secondary me-1">End</span>
                                      {formatTime(event.end_time)}
                                    </span>
                                  )}
                                </span>
                              </div>
                            )}
                            
                            {/* Fallback for legacy time field */}
                            {!event.arrive_by_time && !event.start_time && !event.end_time && event.time && (
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

                          {/* Right Column - RSVP Summary and Actions */}
                          <div className="col-md-6">
                            <h6 className="mb-3">
                              <i className="bi bi-people me-2"></i>
                              Member Responses ({(() => {
                                const stats = getRsvpStats(event);
                                return `${stats.total_responses} of ${stats.total_users}`;
                              })()})
                            </h6>
                            
                            <div className="row g-2 mb-3">
                              <div className="col-4">
                                <div className="card bg-success bg-opacity-10 border-success">
                                  <div className="card-body text-center py-2">
                                    <div className="fw-bold text-success">{(() => {
                                      const stats = getRsvpStats(event);
                                      return stats.yes_count || 0;
                                    })()}</div>
                                    <div className="small text-success">Going</div>
                                  </div>
                                </div>
                              </div>
                              <div className="col-4">
                                <div className="card bg-warning bg-opacity-10 border-warning">
                                  <div className="card-body text-center py-2">
                                    <div className="fw-bold text-warning">{(() => {
                                      const stats = getRsvpStats(event);
                                      return stats.maybe_count || 0;
                                    })()}</div>
                                    <div className="small text-warning">Maybe</div>
                                  </div>
                                </div>
                              </div>
                              <div className="col-4">
                                <div className="card bg-danger bg-opacity-10 border-danger">
                                  <div className="card-body text-center py-2">
                                    <div className="fw-bold text-danger">{(() => {
                                      const stats = getRsvpStats(event);
                                      return stats.no_count || 0;
                                    })()}</div>
                                    <div className="small text-danger">Not Going</div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* RSVP Buttons */}
                            {isUpcoming && !event.is_cancelled && (
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
                            {event.is_cancelled && (
                              <div className="alert alert-secondary text-center">
                                <i className="bi bi-x-circle me-2"></i>
                                RSVP is disabled for cancelled events
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Additional Expanded Details */}
                        <div className="mt-4">
                          <hr />
                          <div className="row">
                            {/* Section-Organized Member List */}
                            <div className="col-md-6">
                              <h6>Member Responses by Section</h6>
                              
                              {(() => {
                                const eventRsvps = allRsvps[event.id] || { Yes: [], No: [], Maybe: [] };
                                const privacyData = eventRsvps._privacy;
                                
                                // Check if user can view details
                                if (privacyData && !privacyData.can_view_details) {
                                  return (
                                    <div className="alert alert-info">
                                      <i className="bi bi-shield-lock me-2"></i>
                                      <strong>Privacy Mode Active</strong>
                                      <div className="small mt-1">
                                        {privacyData.privacy_message}
                                      </div>
                                    </div>
                                  );
                                }
                                
                                const sectionGroups = organizeUsersBySection(event.id);
                                
                                // If no sections with users, show message
                                if (Object.keys(sectionGroups).length === 0 || 
                                    Object.values(sectionGroups).every(section => section.users.length === 0)) {
                                  return (
                                    <div className="text-muted fst-italic">
                                      No RSVP responses yet
                                    </div>
                                  );
                                }
                                
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

                            {/* Map - Only One Map in Expanded View */}
                            {event.lat && event.lng && (
                              <div className="col-md-6">
                                <h6>Location Map</h6>
                                <div className="border rounded" style={{ height: '200px', overflow: 'hidden' }}>
                                  {getGoogleMapsApiKey() ? (
                                    <iframe
                                      src={`https://www.google.com/maps/embed/v1/place?key=${getGoogleMapsApiKey()}&q=${event.lat},${event.lng}&zoom=15`}
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
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </>
  );
}

export default Dashboard;
