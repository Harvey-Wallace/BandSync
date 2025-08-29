import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import EventForm from '../components/EventForm';
import EnhancedEventForm from '../components/EnhancedEventForm';
import EventDateVoting from '../components/EventDateVoting';
import EnhancedRSVPModal from '../components/EnhancedRSVPModal';
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
  const [rsvpDetails, setRsvpDetails] = useState({}); // Store detailed RSVP data (comments, likelihood, etc.)
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
  const [showVoting, setShowVoting] = useState({}); // Track which events show voting
  
  // Templates state
  const [templates, setTemplates] = useState([]);
  const [showTemplatesModal, setShowTemplatesModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [templateDate, setTemplateDate] = useState('');
  const [templateLocation, setTemplateLocation] = useState('');
  const [templateLoading, setTemplateLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  
  // Template creation state
  const [showCreateTemplateForm, setShowCreateTemplateForm] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    template_name: '',
    description: '',
    category_id: '',
    default_location_address: '',
    default_start_time: '',
    default_end_time: '',
    default_arrive_by_time: '',
    default_rsvp_required: true,
    default_rsvp_deadline_hours: 24,
    default_reminder_hours: 24,
    default_send_invitations: true
  });
  const [createTemplateLoading, setCreateTemplateLoading] = useState(false);
  
  // Enhanced RSVP Modal state
  const [showRsvpModal, setShowRsvpModal] = useState(false);
  const [currentRsvpEvent, setCurrentRsvpEvent] = useState(null);
  
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
        const eventsResponse = await axios.get(`${getApiUrl()}/events`, {
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
              // Skip metadata fields and ensure users is an array
              if (rsvpStatus.startsWith('_') || !Array.isArray(users)) {
                continue;
              }
              if (users.some(user => user.username === username)) {
                rsvpMap[event.id] = rsvpStatus.toLowerCase(); // Normalize to lowercase for UI consistency
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

        // Fetch categories for event creation/editing
        try {
          const categoriesResponse = await axios.get(`${getApiUrl()}/events/categories`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          console.log('Categories loaded:', categoriesResponse.data);
          setCategories(categoriesResponse.data);
        } catch (error) {
          console.error('Error loading categories:', error);
          // Don't fail the entire load if categories fail
        }

        // Fetch templates for admin users
        if (role === 'Admin' || role === 'admin' || role === 'super_admin') {
          try {
            const templatesResponse = await axios.get(`${getApiUrl()}/events/templates`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            console.log('Templates loaded:', templatesResponse.data);
            setTemplates(templatesResponse.data);
          } catch (error) {
            console.error('Error loading templates:', error);
            // Don't fail the entire load if templates fail
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

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showDropdown && !event.target.closest('.btn-group')) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [showDropdown]);

  const handleRSVP = async (eventId, rsvpData) => {
    console.log(`Starting RSVP update for event ${eventId} with data:`, rsvpData);
    
    try {
      const token = localStorage.getItem('token');
      const username = localStorage.getItem('username');
      
      if (!token) {
        showErrorMessage('Authentication required. Please log in.');
        return;
      }

      console.log(`Current user: ${username}`);
      console.log(`Sending RSVP request to: ${getApiUrl()}/events/${eventId}/rsvp`);
      console.log(`Request payload:`, rsvpData);

      const response = await axios.post(`${getApiUrl()}/events/${eventId}/rsvp`, rsvpData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('RSVP API response:', response.data);
      console.log('RSVP API response status:', response.status);

      // Update local state immediately for better UX - normalize to lowercase for UI consistency
      const normalizedStatus = rsvpData.status.toLowerCase();
      setRsvps(prev => ({
        ...prev,
        [eventId]: normalizedStatus
      }));

      // Store detailed RSVP data
      setRsvpDetails(prev => ({
        ...prev,
        [eventId]: {
          status: rsvpData.status,
          comments: rsvpData.comments,
          likelihood: rsvpData.likelihood,
          updated_at: new Date().toISOString()
        }
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
            // Skip metadata fields and ensure users is an array
            if (rsvpStatus.startsWith('_') || !Array.isArray(users)) {
              continue;
            }
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
      
      showSuccessMessage(statusMessages[rsvpData.status] || 'RSVP updated successfully!');

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

  // Enhanced RSVP Functions
  const openEnhancedRSVP = (event) => {
    setCurrentRsvpEvent(event);
    setShowRsvpModal(true);
  };

  const handleEnhancedRSVP = async (rsvpData) => {
    if (currentRsvpEvent) {
      await handleRSVP(currentRsvpEvent.id, rsvpData);
      
      // Show enhanced success message
      const statusMessages = {
        'Yes': `RSVP confirmed for "${currentRsvpEvent.title}"! See you there! 🎉`,
        'No': `RSVP updated for "${currentRsvpEvent.title}" - marked as not attending`,
        'Maybe': `RSVP updated for "${currentRsvpEvent.title}" - marked as maybe attending${rsvpData.likelihood ? ` (${rsvpData.likelihood}% likely)` : ''}`
      };
      
      showSuccessMessage(statusMessages[rsvpData.status] || 'RSVP updated successfully!');
    }
  };

  // Quick RSVP functions for backward compatibility with simple button clicks
  const handleQuickRSVP = async (eventId, status) => {
    const rsvpData = { status };
    
    // For "Maybe" responses without enhanced modal, default to 50% likelihood
    if (status === 'Maybe') {
      rsvpData.likelihood = 50;
    }
    
    await handleRSVP(eventId, rsvpData);
    
    // Show success message
    const statusMessages = {
      'Yes': 'RSVP confirmed! See you there! 🎉',
      'No': 'RSVP updated - marked as not attending',
      'Maybe': 'RSVP updated - marked as maybe attending'
    };
    
    showSuccessMessage(statusMessages[status] || 'RSVP updated successfully!');
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
      const eventsResponse = await axios.get(`${getApiUrl()}/events`, {
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
      const eventsResponse = await axios.get(`${getApiUrl()}/events`, {
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

  // Toggle voting display for multiple date events
  const toggleVoting = (eventId) => {
    setShowVoting(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  // Open edit form with event data
  const openEditForm = (event) => {
    setEditingEvent(event);
    setShowEditForm(true);
  };

  // Template functions
  const openTemplatesModal = () => {
    setShowTemplatesModal(true);
  };

  const closeTemplatesModal = () => {
    setShowTemplatesModal(false);
    setSelectedTemplate(null);
    setTemplateDate('');
    setTemplateLocation('');
  };

  const selectTemplate = (template) => {
    setSelectedTemplate(template);
    setShowTemplatesModal(false);
  };

  const createEventFromTemplate = async () => {
    if (!selectedTemplate || !templateDate) {
      showErrorMessage('Please select a date for the event');
      return;
    }

    setTemplateLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${getApiUrl()}/events/from-template/${selectedTemplate.id}`, {
        date: templateDate,
        location_address: templateLocation,
        title: selectedTemplate.template_name || selectedTemplate.title
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      showSuccessMessage('Event created successfully from template! 🎉');
      
      // Close modal and reset state
      setSelectedTemplate(null);
      setTemplateDate('');
      setTemplateLocation('');
      
      // Refresh events list
      const eventsResponse = await axios.get(`${getApiUrl()}/events`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const sortedEvents = eventsResponse.data.sort((a, b) => new Date(a.date) - new Date(b.date));
      setEvents(sortedEvents);
      
    } catch (error) {
      console.error('Error creating event from template:', error);
      showErrorMessage(error.response?.data?.error || 'Failed to create event from template');
    } finally {
      setTemplateLoading(false);
    }
  };

  // Template creation functions
  const handleTemplateInputChange = (field, value) => {
    setNewTemplate(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const resetTemplateForm = () => {
    setNewTemplate({
      template_name: '',
      description: '',
      category_id: '',
      default_location_address: '',
      default_start_time: '',
      default_end_time: '',
      default_arrive_by_time: '',
      default_rsvp_required: true,
      default_rsvp_deadline_hours: 24,
      default_reminder_hours: 24,
      default_send_invitations: true
    });
  };

  const createTemplate = async () => {
    if (!newTemplate.template_name.trim()) {
      showErrorMessage('Please enter a template name');
      return;
    }

    setCreateTemplateLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const templateData = {
        ...newTemplate,
        template_name: newTemplate.template_name.trim(),
        description: newTemplate.description.trim(),
        category_id: newTemplate.category_id || null,
        default_location_address: newTemplate.default_location_address.trim() || null,
        default_start_time: newTemplate.default_start_time || null,
        default_end_time: newTemplate.default_end_time || null,
        default_arrive_by_time: newTemplate.default_arrive_by_time || null
      };

      await axios.post(`${getApiUrl()}/events/templates`, templateData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      showSuccessMessage('Template created successfully! 🎉');
      
      // Close modal and reset form
      setShowCreateTemplateForm(false);
      resetTemplateForm();
      
      // Refresh templates list
      if (role === 'Admin' || role === 'admin' || role === 'super_admin') {
        try {
          const templatesResponse = await axios.get(`${getApiUrl()}/events/templates`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setTemplates(templatesResponse.data);
        } catch (error) {
          console.error('Error reloading templates:', error);
        }
      }
      
    } catch (error) {
      console.error('Error creating template:', error);
      showErrorMessage(error.response?.data?.error || 'Failed to create template');
    } finally {
      setCreateTemplateLoading(false);
    }
  };

  // Delete event handler
  const handleDeleteEvent = async (event) => {
    if (!window.confirm(`Are you sure you want to delete "${event.title || event.name || 'this event'}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      
      await axios.delete(`${getApiUrl()}/events/${event.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Refresh events list
      const eventsResponse = await axios.get(`${getApiUrl()}/events`, {
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

      <style>
        {`
          .template-card:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
          }
          .dropdown-menu.show {
            display: block;
          }
        `}
      </style>

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
                {/* Create Event Button with Dropdown - Admin Only */}
                {(role === 'Admin' || role === 'admin' || role === 'super_admin') && (
                  <div className="btn-group" style={{ position: 'relative' }}>
                    <button 
                      className="btn btn-success"
                      onClick={() => setShowCreateForm(true)}
                    >
                      <i className="fas fa-plus me-2"></i>
                      Create Event
                    </button>
                    <button 
                      className="btn btn-success dropdown-toggle dropdown-toggle-split" 
                      type="button" 
                      onClick={() => setShowDropdown(!showDropdown)}
                      aria-expanded={showDropdown}
                      style={{ borderLeft: '1px solid rgba(255,255,255,0.2)' }}
                    >
                      <span className="visually-hidden">Toggle Dropdown</span>
                    </button>
                    {showDropdown && (
                      <ul className="dropdown-menu show" style={{ position: 'absolute', top: '100%', right: 0, zIndex: 1000 }}>
                        <li>
                          <button 
                            className="dropdown-item" 
                            onClick={() => {
                              setShowCreateForm(true);
                              setShowDropdown(false);
                            }}
                          >
                            <i className="fas fa-plus me-2 text-primary"></i>
                            Create New Event
                          </button>
                        </li>
                        <li><hr className="dropdown-divider" /></li>
                        <li>
                          <button 
                            className="dropdown-item" 
                            onClick={() => {
                              openTemplatesModal();
                              setShowDropdown(false);
                            }}
                          >
                            <i className="fas fa-file-alt me-2 text-success"></i>
                            Create from Template
                          </button>
                        </li>
                        <li><hr className="dropdown-divider" /></li>
                        <li>
                          <button 
                            className="dropdown-item" 
                            onClick={() => {
                              setShowCreateTemplateForm(true);
                              setShowDropdown(false);
                            }}
                          >
                            <i className="fas fa-save me-2 text-warning"></i>
                            Create Template
                          </button>
                        </li>
                      </ul>
                    )}
                  </div>
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
                              <h6 className="mb-1 fw-bold text-dark">{event.title || event.name || 'Untitled Event'}</h6>
                              <small className="text-muted">{event.type || event.event_type || 'Event'}</small>
                            </div>
                          </div>
                          
                          {/* Location - More prominent */}
                          {(event.location_address || event.location) && (
                            <div className="d-flex align-items-center gap-2 text-muted">
                              <i className="fas fa-map-marker-alt"></i>
                              <span className="fw-medium">
                                {(() => {
                                  const location = event.location_address || event.location;
                                  return location.length > 40 ? `${location.substring(0, 40)}...` : location;
                                })()}
                              </span>
                            </div>
                          )}
                          
                          {/* Time Display - Support Multiple Dates */}
                          <div className="d-flex align-items-center gap-2 text-muted">
                            <i className="fas fa-clock"></i>
                            <span className="fw-medium">
                              {event.has_multiple_dates ? (
                                event.final_date_selected ? 
                                  formatEventTiming(event) : 
                                  'Multiple dates - voting in progress'
                              ) : (
                                formatEventTiming(event)
                              )}
                            </span>
                            {event.has_multiple_dates && !event.final_date_selected && (
                              <button
                                className="btn btn-sm btn-outline-primary"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleVoting(event.id);
                                }}
                                style={{ borderRadius: '8px', fontSize: '0.75rem' }}
                              >
                                {showVoting[event.id] ? 'Hide Voting' : 'Vote on Dates'}
                              </button>
                            )}
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
                                  handleQuickRSVP(event.id, 'Yes');
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
                                  handleQuickRSVP(event.id, 'Maybe');
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
                                  handleQuickRSVP(event.id, 'No');
                                }}
                                style={{ borderRadius: '8px', minWidth: '60px' }}
                                title="Can't Go"
                              >
                                <i className="fas fa-times"></i>
                              </button>
                              
                              {/* Enhanced RSVP Button */}
                              <button
                                className="btn btn-sm btn-outline-primary"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  openEnhancedRSVP(event);
                                }}
                                style={{ borderRadius: '8px', minWidth: '40px' }}
                                title="Add comments or details to your RSVP"
                              >
                                <i className="fas fa-comment-alt"></i>
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
                          
                          {/* Multiple Date Voting Component */}
                          {event.has_multiple_dates && !event.final_date_selected && showVoting[event.id] && (
                            <div className="col-12">
                              <EventDateVoting eventId={event.id} />
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
        {showCreateForm && (
          <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
            <div className="modal-dialog modal-lg">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    <i className="bi bi-calendar-plus me-2"></i>
                    Create New Event
                  </h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={() => setShowCreateForm(false)}
                    aria-label="Close"
                  ></button>
                </div>
                <div className="modal-body">
                  <EventForm
                    onSubmit={handleCreateEvent}
                    onCancel={() => setShowCreateForm(false)}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

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

        {/* Enhanced RSVP Modal */}
        <EnhancedRSVPModal
          show={showRsvpModal}
          onHide={() => {
            setShowRsvpModal(false);
            setCurrentRsvpEvent(null);
          }}
          eventTitle={currentRsvpEvent?.title || ''}
          currentStatus={currentRsvpEvent ? (rsvpDetails[currentRsvpEvent.id]?.status || '') : ''}
          currentComments={currentRsvpEvent ? (rsvpDetails[currentRsvpEvent.id]?.comments || '') : ''}
          currentLikelihood={currentRsvpEvent ? (rsvpDetails[currentRsvpEvent.id]?.likelihood || 50) : 50}
          onSubmit={handleEnhancedRSVP}
        />

        {/* Templates Selection Modal */}
        {showTemplatesModal && (
          <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
            <div className="modal-dialog modal-lg">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    <i className="fas fa-file-alt me-2"></i>
                    Choose Event Template
                  </h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={closeTemplatesModal}
                    aria-label="Close"
                  ></button>
                </div>
                <div className="modal-body">
                  {templates.length === 0 ? (
                    <div className="text-center text-muted py-4">
                      <i className="fas fa-file-alt display-4 mb-3"></i>
                      <p>No templates found. Create an event and save it as a template.</p>
                    </div>
                  ) : (
                    <div className="row">
                      {templates.map(template => (
                        <div key={template.id} className="col-md-6 col-lg-4 mb-3">
                          <div className="card h-100 shadow-sm template-card" 
                               style={{ 
                                 cursor: 'pointer', 
                                 transition: 'transform 0.2s, box-shadow 0.2s'
                               }}
                               onClick={() => selectTemplate(template)}>
                            <div className="card-body">
                              <h6 className="card-title fw-bold text-primary">
                                {template.template_name || 'Untitled Template'}
                              </h6>
                              <p className="card-text small text-muted">
                                {template.description || 'No description'}
                              </p>
                              {template.category && (
                                <div className="mb-2">
                                  <span className="badge bg-secondary">{template.category}</span>
                                </div>
                              )}
                              <div className="d-flex justify-content-between align-items-center">
                                <small className="text-muted">
                                  <i className="fas fa-clock me-1"></i>
                                  {template.default_start_time || 'No time set'}
                                </small>
                                <i className="fas fa-arrow-right text-primary"></i>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={closeTemplatesModal}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        {showTemplatesModal && <div className="modal-backdrop fade show"></div>}

        {/* Create Event from Template Modal */}
        {selectedTemplate && (
          <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    <i className="fas fa-calendar-plus me-2"></i>
                    Create Event from Template
                  </h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setSelectedTemplate(null)}
                  ></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <h6 className="fw-bold text-primary">{selectedTemplate.template_name || selectedTemplate.title}</h6>
                    <p className="text-muted small mb-0">{selectedTemplate.description}</p>
                    {selectedTemplate.category && (
                      <span className="badge bg-secondary mt-1">{selectedTemplate.category}</span>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="template-date" className="form-label">
                      <i className="fas fa-calendar me-1"></i>
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
                      <i className="fas fa-map-marker-alt me-1"></i>
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
                    <i className="fas fa-info-circle me-2"></i>
                    <strong>Note:</strong> This will create a new event using the template's settings. 
                    You can modify the event details after creation.
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setSelectedTemplate(null)}
                    disabled={templateLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn btn-success"
                    onClick={createEventFromTemplate}
                    disabled={templateLoading || !templateDate}
                  >
                    {templateLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Creating...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-plus me-1"></i>
                        Create Event
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        {selectedTemplate && <div className="modal-backdrop fade show"></div>}

        {/* Create Template Modal */}
        {showCreateTemplateForm && (
          <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
            <div className="modal-dialog modal-lg">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    <i className="fas fa-save me-2"></i>
                    Create Event Template
                  </h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => {
                      setShowCreateTemplateForm(false);
                      resetTemplateForm();
                    }}
                  ></button>
                </div>
                <div className="modal-body">
                  <form>
                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label htmlFor="template-name" className="form-label">
                            <i className="fas fa-tag me-1"></i>
                            Template Name *
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            id="template-name"
                            value={newTemplate.template_name}
                            onChange={(e) => handleTemplateInputChange('template_name', e.target.value)}
                            placeholder="e.g., Weekly Rehearsal, Concert Performance"
                            required
                          />
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label htmlFor="template-category" className="form-label">
                            <i className="fas fa-folder me-1"></i>
                            Category
                          </label>
                          <select
                            className="form-select"
                            id="template-category"
                            value={newTemplate.category_id}
                            onChange={(e) => handleTemplateInputChange('category_id', e.target.value)}
                          >
                            <option value="">Select category (optional)</option>
                            {categories.map(category => (
                              <option key={category.id} value={category.id}>
                                {category.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>

                    <div className="mb-3">
                      <label htmlFor="template-description" className="form-label">
                        <i className="fas fa-align-left me-1"></i>
                        Description
                      </label>
                      <textarea
                        className="form-control"
                        id="template-description"
                        rows="3"
                        value={newTemplate.description}
                        onChange={(e) => handleTemplateInputChange('description', e.target.value)}
                        placeholder="Describe what this template is for..."
                      />
                    </div>

                    <div className="mb-3">
                      <label htmlFor="template-location" className="form-label">
                        <i className="fas fa-map-marker-alt me-1"></i>
                        Default Location
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="template-location"
                        value={newTemplate.default_location_address}
                        onChange={(e) => handleTemplateInputChange('default_location_address', e.target.value)}
                        placeholder="Default location for events created from this template"
                      />
                    </div>

                    <div className="row">
                      <div className="col-md-4">
                        <div className="mb-3">
                          <label htmlFor="template-arrive-time" className="form-label">
                            <i className="fas fa-clock me-1"></i>
                            Arrive By Time
                          </label>
                          <input
                            type="time"
                            className="form-control"
                            id="template-arrive-time"
                            value={newTemplate.default_arrive_by_time}
                            onChange={(e) => handleTemplateInputChange('default_arrive_by_time', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="mb-3">
                          <label htmlFor="template-start-time" className="form-label">
                            <i className="fas fa-play me-1"></i>
                            Start Time
                          </label>
                          <input
                            type="time"
                            className="form-control"
                            id="template-start-time"
                            value={newTemplate.default_start_time}
                            onChange={(e) => handleTemplateInputChange('default_start_time', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="mb-3">
                          <label htmlFor="template-end-time" className="form-label">
                            <i className="fas fa-stop me-1"></i>
                            End Time
                          </label>
                          <input
                            type="time"
                            className="form-control"
                            id="template-end-time"
                            value={newTemplate.default_end_time}
                            onChange={(e) => handleTemplateInputChange('default_end_time', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label htmlFor="template-rsvp-deadline" className="form-label">
                            <i className="fas fa-calendar-check me-1"></i>
                            RSVP Deadline (hours before)
                          </label>
                          <input
                            type="number"
                            className="form-control"
                            id="template-rsvp-deadline"
                            value={newTemplate.default_rsvp_deadline_hours}
                            onChange={(e) => handleTemplateInputChange('default_rsvp_deadline_hours', parseInt(e.target.value))}
                            min="1"
                            max="168"
                          />
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="mb-3">
                          <label htmlFor="template-reminder" className="form-label">
                            <i className="fas fa-bell me-1"></i>
                            Reminder (hours before)
                          </label>
                          <input
                            type="number"
                            className="form-control"
                            id="template-reminder"
                            value={newTemplate.default_reminder_hours}
                            onChange={(e) => handleTemplateInputChange('default_reminder_hours', parseInt(e.target.value))}
                            min="1"
                            max="168"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="row">
                      <div className="col-md-6">
                        <div className="form-check mb-3">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="template-rsvp-required"
                            checked={newTemplate.default_rsvp_required}
                            onChange={(e) => handleTemplateInputChange('default_rsvp_required', e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor="template-rsvp-required">
                            RSVP Required
                          </label>
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="form-check mb-3">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="template-send-invitations"
                            checked={newTemplate.default_send_invitations}
                            onChange={(e) => handleTemplateInputChange('default_send_invitations', e.target.checked)}
                          />
                          <label className="form-check-label" htmlFor="template-send-invitations">
                            Send Invitations by Default
                          </label>
                        </div>
                      </div>
                    </div>

                    <div className="alert alert-info">
                      <i className="fas fa-info-circle me-2"></i>
                      <strong>Template Usage:</strong> Once created, this template will be available in the "Create from Template" option. When using the template, you'll be able to set the specific date and override any defaults as needed.
                    </div>
                  </form>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowCreateTemplateForm(false);
                      resetTemplateForm();
                    }}
                    disabled={createTemplateLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="btn btn-warning"
                    onClick={createTemplate}
                    disabled={createTemplateLoading || !newTemplate.template_name.trim()}
                  >
                    {createTemplateLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Creating...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-save me-1"></i>
                        Create Template
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        {showCreateTemplateForm && <div className="modal-backdrop fade show"></div>}
      </div>
    </div>
  );
}

export default Events;
