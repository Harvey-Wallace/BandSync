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
import '@fortawesome/fontawesome-free/css/all.min.css';

function Events() {
  const [events, setEvents] = useState([]);
  const [rsvps, setRsvps] = useState({});
  const [allRsvps, setAllRsvps] = useState({}); // Store all member responses
  const [sections, setSections] = useState([]); // Store sections
  const [allUsers, setAllUsers] = useState([]); // Store all users with section info
  const [organizationMembers, setOrganizationMembers] = useState([]); // Store all organization members
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

          // Fetch organization members for admin view
          try {
            const orgMembersRes = await axios.get(`${getApiUrl()}/admin/users`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            console.log('Raw admin users response:', orgMembersRes.data);
            
            // The admin endpoint returns the array directly, not wrapped in { members: [] }
            const members = Array.isArray(orgMembersRes.data) ? orgMembersRes.data : [];
            
            // Transform the data to match expected format
            const transformedMembers = members.map(user => ({
              id: user.id,
              username: user.username,
              name: user.name || user.username,
              email: user.email,
              section: user.section_name || 'Unassigned',
              role: user.role,
              avatar_url: user.avatar_url
            }));
            
            setOrganizationMembers(transformedMembers);
            console.log('Organization members loaded:', transformedMembers);
          } catch (error) {
            console.error('Error loading organization members:', error);
            console.error('Error response:', error.response?.data);
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
    console.log(`Starting RSVP update for event ${eventId} with status: ${status}`);
    
    try {
      const token = localStorage.getItem('token');
      const username = localStorage.getItem('username');
      
      if (!token) {
        showErrorMessage('Authentication required. Please log in.');
        return;
      }

      console.log(`Current user: ${username}`);
      console.log(`Sending RSVP request to: ${getApiUrl()}/events/${eventId}/rsvp`);
      console.log(`Request payload:`, { status: status });

      const response = await axios.post(`${getApiUrl()}/events/${eventId}/rsvp`, {
        status: status
      }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('RSVP API response:', response.data);
      console.log('RSVP API response status:', response.status);

      // Update local state immediately for better UX - normalize to lowercase for UI consistency
      const normalizedStatus = status.toLowerCase();
      setRsvps(prev => ({
        ...prev,
        [eventId]: normalizedStatus
      }));

      console.log(`Updated local RSVP state for event ${eventId} to ${normalizedStatus}`);

      // Refresh the detailed RSVP data for admin view
      if (role === 'Admin' || role === 'admin' || role === 'super_admin') {
        console.log('User is admin, refreshing detailed RSVP data...');
        await refreshEventRsvpData(eventId);
      }

      // Also refresh current user's RSVP status from server to verify it persisted
      console.log('Verifying RSVP persistence by fetching fresh data...');
      setTimeout(async () => {
        try {
          const verifyResponse = await axios.get(`${getApiUrl()}/events/${eventId}/rsvps`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          console.log('Verification response:', verifyResponse.data);
          
          // Check if our RSVP is in the response
          let foundOurRsvp = false;
          for (const [rsvpStatus, users] of Object.entries(verifyResponse.data)) {
            if (users.some(user => user.username === username)) {
              console.log(`✅ RSVP verified! User ${username} found in ${rsvpStatus} list`);
              foundOurRsvp = true;
              // Update local state to match server
              setRsvps(prev => ({
                ...prev,
                [eventId]: rsvpStatus.toLowerCase()
              }));
              break;
            }
          }
          
          if (!foundOurRsvp) {
            console.error(`❌ RSVP NOT FOUND! User ${username} not found in any RSVP list`);
            console.log('Full verification response:', verifyResponse.data);
          }
        } catch (verifyError) {
          console.error('Error verifying RSVP:', verifyError);
        }
      }, 1000); // Wait 1 second then verify

      // Show success message
      const statusMessages = {
        'Yes': 'RSVP confirmed! See you there! 🎉',
        'No': 'RSVP updated - marked as not attending',
        'Maybe': 'RSVP updated - marked as maybe attending'
      };
      
      showSuccessMessage(statusMessages[status] || 'RSVP updated successfully!');

    } catch (error) {
      console.error('Error updating RSVP:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Error headers:', error.response?.headers);
      
      if (error.response?.status === 401) {
        showErrorMessage('Session expired. Please log in again.');
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else {
        showErrorMessage(error.response?.data?.message || error.response?.data?.msg || 'Failed to update RSVP. Please try again.');
      }
    }
  };

  // Function to refresh RSVP data for a specific event
  const refreshEventRsvpData = async (eventId) => {
    try {
      const token = localStorage.getItem('token');
      const rsvpRes = await axios.get(`${getApiUrl()}/events/${eventId}/rsvps`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update the allRsvps state with fresh data for this event
      setAllRsvps(prev => ({
        ...prev,
        [eventId]: rsvpRes.data
      }));
      
      console.log(`Refreshed RSVP data for event ${eventId}:`, rsvpRes.data);
    } catch (error) {
      console.warn(`Error refreshing RSVP data for event ${eventId}:`, error);
    }
  };

  const toggleEventExpansion = async (eventId) => {
    const wasExpanded = expandedEvents[eventId];
    
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));

    // If expanding the event and user is admin, refresh RSVP data
    if (!wasExpanded && (role === 'Admin' || role === 'admin' || role === 'super_admin')) {
      await refreshEventRsvpData(eventId);
    }
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
    
    // The data structure from /events/{id}/rsvps is: { "Yes": [users], "No": [users], "Maybe": [users] }
    // Backend returns capitalized keys, so we need to map them to lowercase for consistency
    const statusMapping = {
      'Yes': 'yes',
      'No': 'no', 
      'Maybe': 'maybe'
    };
    
    Object.entries(eventRsvps).forEach(([status, users]) => {
      if (Array.isArray(users)) {
        const normalizedStatus = statusMapping[status] || status.toLowerCase();
        if (counts.hasOwnProperty(normalizedStatus)) {
          counts[normalizedStatus] = users.length;
          counts.total += users.length;
        }
      }
    });
    
    console.log(`RSVP counts for event ${eventId}:`, counts, 'Raw data:', eventRsvps);
    return counts;
  };

  const getUsersForEvent = (eventId, status = null) => {
    const eventRsvps = allRsvps[eventId] || {};
    
    if (status) {
      // Convert lowercase status to capitalized for backend compatibility
      const capitalizedStatus = status.charAt(0).toUpperCase() + status.slice(1);
      // Try both capitalized and lowercase versions
      return eventRsvps[capitalizedStatus] || eventRsvps[status] || [];
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

  // Get all organization members with their RSVP status for a specific event
  const getAllMembersWithRsvpStatus = (eventId) => {
    const eventRsvps = allRsvps[eventId] || {};
    
    console.log(`Getting members for event ${eventId}:`, {
      organizationMembers: organizationMembers.length,
      eventRsvps: Object.keys(eventRsvps),
      rsvpData: eventRsvps
    });
    
    return organizationMembers.map(member => {
      // Find which RSVP status this member has
      let rsvpStatus = 'no_response';
      for (const [status, users] of Object.entries(eventRsvps)) {
        if (Array.isArray(users) && users.some(user => 
          user.id === member.id || user.username === member.username
        )) {
          // Normalize the status to lowercase for UI consistency
          rsvpStatus = status.toLowerCase();
          break;
        }
      }
      
      return {
        ...member,
        rsvpStatus
      };
    });
  };

  // Get RSVP status badge styling
  const getRsvpStatusStyle = (status) => {
    switch (status) {
      case 'yes':
        return { bg: 'success', text: 'Going', icon: 'fa-check' };
      case 'maybe':
        return { bg: 'warning', text: 'Maybe', icon: 'fa-question' };
      case 'no':
        return { bg: 'danger', text: "Can't Go", icon: 'fa-times' };
      default:
        return { bg: 'secondary', text: 'No Response', icon: 'fa-minus' };
    }
  };

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString || dateTimeString === 'TBD') {
      return 'TBD';
    }
    
    try {
      const date = new Date(dateTimeString);
      
      // Format date
      const dateOptions = { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      };
      const timeOptions = { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      };
      
      return `${date.toLocaleDateString('en-US', dateOptions)} ${date.toLocaleTimeString('en-US', timeOptions)}`;
    } catch (error) {
      console.error('Date parsing error:', error);
      return dateTimeString;
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return null;
    
    try {
      // Handle time string in format "HH:MM:SS" or "HH:MM"
      const [hours, minutes] = timeString.split(':');
      const date = new Date();
      date.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit', 
        hour12: true 
      });
    } catch (error) {
      return timeString;
    }
  };

  const formatEventTiming = (event) => {
    const date = event.date ? new Date(event.date) : null;
    const dateStr = date ? date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    }) : 'TBD';

    // For the main display, only show arrive by time if available
    const arriveBy = formatTime(event.arrive_by_time);
    
    if (arriveBy) {
      return `${dateStr} • Arrive: ${arriveBy}`;
    }

    // Fallback to start time if no arrive by time
    const startTime = formatTime(event.start_time);
    if (startTime) {
      return `${dateStr} • ${startTime}`;
    }

    // Final fallback to original dateTime
    return event.dateTime ? formatDateTime(event.dateTime) : dateStr;
  };

  const formatDetailedTiming = (event) => {
    const times = [];
    const arriveBy = formatTime(event.arrive_by_time);
    const startTime = formatTime(event.start_time);
    const endTime = formatTime(event.end_time);

    if (arriveBy) times.push(`Arrive: ${arriveBy}`);
    if (startTime) times.push(`Start: ${startTime}`);
    if (endTime) times.push(`End: ${endTime}`);
    
    return times.length > 0 ? times.join(' • ') : null;
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
      
      console.log('Creating event with data:', eventData);
      console.log(`POST request to: ${getApiUrl()}/events`);
      
      const response = await axios.post(`${getApiUrl()}/events`, eventData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Event creation response:', response.data);

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
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      console.error('Error response headers:', error.response?.headers);
      
      let errorMessage = 'Failed to create event. Please try again.';
      if (error.response?.status === 405) {
        errorMessage = 'Event creation endpoint not available. Please contact support.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to create events.';
      } else if (error.response?.status === 400) {
        errorMessage = error.response?.data?.error || 'Invalid event data. Please check all fields.';
      }
      
      showErrorMessage(errorMessage);
      throw error; // Re-throw so the form can handle it
    }
  };

  // Edit event handler
  const handleEditEvent = async (eventData) => {
    try {
      const token = localStorage.getItem('token');
      
      console.log('Updating event with data:', eventData);
      console.log(`PUT request to: ${getApiUrl()}/events/${editingEvent.id}`);
      
      const response = await axios.put(`${getApiUrl()}/events/${editingEvent.id}`, eventData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Event update response:', response.data);

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
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      console.error('Error response headers:', error.response?.headers);
      
      let errorMessage = 'Failed to update event. Please try again.';
      if (error.response?.status === 405) {
        errorMessage = 'Event update endpoint not available. Please contact support.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to update events.';
      } else if (error.response?.status === 400) {
        errorMessage = error.response?.data?.error || 'Invalid event data. Please check all fields.';
      }
      
      showErrorMessage(errorMessage);
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
                <div key={event.id} className="col-12 mb-2">
                  <div className={`card border-0 shadow-sm ${isPastEvent ? 'opacity-75' : ''}`} 
                       style={{ 
                         borderRadius: '12px', 
                         transition: 'all 0.2s ease, transform 0.1s ease',
                         cursor: 'pointer',
                         borderLeft: `4px solid ${isPastEvent ? '#6c757d' : (orgThemeColor || '#0d6efd')}`
                       }}
                       onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-1px)'}
                       onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0px)'}>
                    
                    {/* Compact Single-Line Layout */}
                    <div 
                      className="card-body py-3 px-4"
                      onClick={(e) => {
                        // Only expand if clicking on the card body, not buttons
                        if (!e.target.closest('button')) {
                          toggleEventExpansion(event.id);
                        }
                      }}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="d-flex align-items-center justify-content-between">
                        {/* Left Side - Event Info */}
                        <div className="d-flex align-items-center gap-3 flex-grow-1">
                          {/* Event Icon & Name */}
                          <div className="d-flex align-items-center gap-3">
                            <div 
                              className="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                              style={{
                                width: '35px',
                                height: '35px',
                                background: isPastEvent ? '#6c757d' : `linear-gradient(135deg, ${orgThemeColor || '#0d6efd'} 0%, ${orgThemeColor ? `${orgThemeColor}dd` : '#0851d4'} 100%)`,
                                color: 'white'
                              }}
                            >
                              <i className="fas fa-calendar-check"></i>
                            </div>
                            <div>
                              <h6 className="mb-0 fw-bold text-dark">{event.name}</h6>
                              <small className="text-muted">{event.event_type || 'Event'}</small>
                            </div>
                          </div>
                          
                          {/* Location - More prominent */}
                          {event.location && (
                            <div className="d-flex align-items-center gap-2 text-muted">
                              <i className="fas fa-map-marker-alt"></i>
                              <span className="fw-medium">
                                {event.location.length > 40 ? `${event.location.substring(0, 40)}...` : event.location}
                              </span>
                            </div>
                          )}
                          
                          {/* Simple Time Display */}
                          <div className="d-flex align-items-center gap-2 text-muted">
                            <i className="fas fa-clock"></i>
                            <span className="fw-medium">{formatEventTiming(event)}</span>
                          </div>
                          
                          {/* Response Count - Admin Only */}
                          {(role === 'Admin' || role === 'admin' || role === 'super_admin') && (
                            <div className="d-flex align-items-center gap-2">
                              <div 
                                className="rounded-pill px-2 py-1 d-flex align-items-center gap-1"
                                style={{ backgroundColor: '#e8f5e8', color: '#198754' }}
                              >
                                <i className="fas fa-users"></i>
                                <span className="fw-semibold small">{rsvpCounts.yes}</span>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Right Side - RSVP Status & Actions */}
                        <div className="d-flex align-items-center gap-2">
                          {/* Current User's RSVP Status */}
                          {!isPastEvent && (
                            <div className="d-flex gap-1">
                              <button
                                className={`btn btn-sm ${rsvps[event.id] === 'yes' ? 'btn-success' : 'btn-outline-success'}`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRSVP(event.id, 'Yes');
                                }}
                                style={{ borderRadius: '8px', minWidth: '60px' }}
                                title="Going"
                              >
                                <i className="fas fa-check"></i>
                              </button>
                              <button
                                className={`btn btn-sm ${rsvps[event.id] === 'maybe' ? 'btn-warning' : 'btn-outline-warning'}`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRSVP(event.id, 'Maybe');
                                }}
                                style={{ borderRadius: '8px', minWidth: '60px' }}
                                title="Maybe"
                              >
                                <i className="fas fa-question"></i>
                              </button>
                              <button
                                className={`btn btn-sm ${rsvps[event.id] === 'no' ? 'btn-danger' : 'btn-outline-danger'}`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRSVP(event.id, 'No');
                                }}
                                style={{ borderRadius: '8px', minWidth: '60px' }}
                                title="Can't Go"
                              >
                                <i className="fas fa-times"></i>
                              </button>
                            </div>
                          )}
                          
                          {/* Admin Action Buttons */}
                          {(role === 'Admin' || role === 'admin' || role === 'super_admin') && (
                            <div className="d-flex gap-1">
                              <button 
                                className="btn btn-sm btn-warning rounded-circle"
                                style={{ width: '32px', height: '32px' }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openEditForm(event);
                                }}
                                title="Edit Event"
                              >
                                <i className="fas fa-pencil-alt"></i>
                              </button>
                              <button 
                                className="btn btn-sm btn-danger rounded-circle"
                                style={{ width: '32px', height: '32px' }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteEvent(event);
                                }}
                                title="Delete Event"
                              >
                                <i className="fas fa-trash-alt"></i>
                              </button>
                            </div>
                          )}
                          
                          {/* Expand Button */}
                          <button 
                            className="btn btn-sm btn-light rounded-circle"
                            style={{ width: '32px', height: '32px' }}
                            onClick={() => toggleEventExpansion(event.id)}
                            title={isExpanded ? 'Collapse' : 'Expand'}
                          >
                            <i className="fas fa-ellipsis-h"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                    
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
                          {/* Detailed Timing */}
                          {formatDetailedTiming(event) && (
                            <div className="col-12">
                              <div className="card border-0 shadow-sm">
                                <div className="card-header bg-white border-0">
                                  <h6 className="fw-bold text-dark mb-0">
                                    <i className="fas fa-clock me-2 text-primary"></i>
                                    Event Schedule
                                  </h6>
                                </div>
                                <div className="card-body">
                                  <div className="d-flex flex-wrap gap-4">
                                    {formatTime(event.arrive_by_time) && (
                                      <div className="d-flex align-items-center gap-2">
                                        <div className="bg-primary bg-opacity-10 rounded-circle p-2">
                                          <i className="fas fa-door-open text-primary"></i>
                                        </div>
                                        <div>
                                          <small className="text-muted d-block">Arrive By</small>
                                          <span className="fw-bold">{formatTime(event.arrive_by_time)}</span>
                                        </div>
                                      </div>
                                    )}
                                    {formatTime(event.start_time) && (
                                      <div className="d-flex align-items-center gap-2">
                                        <div className="bg-success bg-opacity-10 rounded-circle p-2">
                                          <i className="fas fa-play text-success"></i>
                                        </div>
                                        <div>
                                          <small className="text-muted d-block">Start Time</small>
                                          <span className="fw-bold">{formatTime(event.start_time)}</span>
                                        </div>
                                      </div>
                                    )}
                                    {formatTime(event.end_time) && (
                                      <div className="d-flex align-items-center gap-2">
                                        <div className="bg-danger bg-opacity-10 rounded-circle p-2">
                                          <i className="fas fa-stop text-danger"></i>
                                        </div>
                                        <div>
                                          <small className="text-muted d-block">End Time</small>
                                          <span className="fw-bold">{formatTime(event.end_time)}</span>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}

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
                            <div className="col-12">
                              <div className="card border-0 shadow-sm">
                                <div className="card-header bg-white border-0">
                                  <h6 className="fw-bold text-dark mb-0">
                                    <i className="fas fa-users me-2 text-primary"></i>
                                    Member Responses ({organizationMembers.length} members)
                                  </h6>
                                </div>
                                <div className="card-body">
                                  {organizationMembers.length > 0 ? (
                                    <>
                                      {/* Response Summary */}
                                      <div className="row g-2 mb-4">
                                        <div className="col-3">
                                          <div className="text-center p-3 bg-success bg-opacity-10 rounded-3">
                                            <div className="h4 mb-1 text-success fw-bold">{rsvpCounts.yes}</div>
                                            <small className="text-success fw-medium">Going</small>
                                          </div>
                                        </div>
                                        <div className="col-3">
                                          <div className="text-center p-3 bg-warning bg-opacity-10 rounded-3">
                                            <div className="h4 mb-1 text-warning fw-bold">{rsvpCounts.maybe}</div>
                                            <small className="text-warning fw-medium">Maybe</small>
                                          </div>
                                        </div>
                                        <div className="col-3">
                                          <div className="text-center p-3 bg-danger bg-opacity-10 rounded-3">
                                            <div className="h4 mb-1 text-danger fw-bold">{rsvpCounts.no}</div>
                                            <small className="text-danger fw-medium">Can't Go</small>
                                          </div>
                                        </div>
                                        <div className="col-3">
                                          <div className="text-center p-3 bg-secondary bg-opacity-10 rounded-3">
                                            <div className="h4 mb-1 text-secondary fw-bold">
                                              {organizationMembers.length - rsvpCounts.total}
                                            </div>
                                            <small className="text-secondary fw-medium">No Response</small>
                                          </div>
                                        </div>
                                      </div>

                                      {/* Detailed Member List */}
                                      <div className="row g-2">
                                        {getAllMembersWithRsvpStatus(event.id).length > 0 ? 
                                          getAllMembersWithRsvpStatus(event.id).map(member => {
                                            const statusStyle = getRsvpStatusStyle(member.rsvpStatus);
                                            return (
                                              <div key={member.id} className="col-md-6 col-lg-4">
                                                <div className="d-flex align-items-center justify-content-between p-2 border rounded-3 bg-light">
                                                  <div className="d-flex align-items-center gap-2">
                                                    <UserAvatar 
                                                      user={member} 
                                                      size="sm"
                                                      showTooltip={false}
                                                    />
                                                    <div>
                                                      <div className="fw-medium text-dark">{member.name || member.username}</div>
                                                      {member.section && member.section !== 'Unassigned' && (
                                                        <small className="text-muted">{member.section}</small>
                                                      )}
                                                    </div>
                                                  </div>
                                                  <span className={`badge bg-${statusStyle.bg} d-flex align-items-center gap-1`}>
                                                    <i className={`fas ${statusStyle.icon}`}></i>
                                                    <span className="d-none d-sm-inline">{statusStyle.text}</span>
                                                  </span>
                                                </div>
                                              </div>
                                            );
                                          }) :
                                          <div className="col-12 text-center py-3">
                                            <p className="text-muted">No member data available for this event.</p>
                                          </div>
                                        }
                                      </div>
                                    </>
                                  ) : (
                                    <div className="text-center py-3">
                                      <i className="fas fa-users text-muted fs-1 mb-2"></i>
                                      <p className="text-muted mb-0">
                                        {loading ? 'Loading member list...' : 'No organization members found'}
                                      </p>
                                      {!loading && (
                                        <small className="text-muted">
                                          Check console for debugging information
                                        </small>
                                      )}
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
