import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import { 
  DataLoadingState, 
  ErrorState, 
  EmptyState 
} from '../components/LoadingComponents';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

function Events() {
  const [events, setEvents] = useState([]);
  const [rsvps, setRsvps] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const role = localStorage.getItem('role');

  // Enhanced notification functions
  const showSuccessMessage = (message) => {
    if (window.showSuccess) window.showSuccess(message);
  };

  const showErrorMessage = (message) => {
    if (window.showError) window.showError(message);
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
  }, []);

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
              </div>
            </div>
          </div>
        </div>

        {/* Events List */}
        {events.length === 0 ? (
          <EmptyState 
            title="No Events Found"
            message="There are no events scheduled at the moment."
            actionText="Refresh"
            onAction={() => window.location.reload()}
          />
        ) : (
          <div className="row">
            {events.map(event => (
              <div key={event.id} className="col-12 mb-3">
                <div className="card border-0 shadow-sm">
                  <div className="card-header bg-white border-bottom-0">
                    <div className="d-flex justify-content-between align-items-center">
                      <div className="flex-grow-1">
                        <h5 className="card-title mb-1 fw-bold text-dark">
                          {event.name}
                        </h5>
                        <div className="d-flex flex-wrap gap-2">
                          <span className="badge bg-info">
                            <i className="fas fa-clock me-1"></i>
                            {formatDateTime(event.dateTime)}
                          </span>
                          {event.location && (
                            <span className="badge bg-info">
                              <i className="fas fa-map-marker-alt me-1"></i>
                              {event.location}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="d-flex align-items-center gap-2">
                        <div className="btn-group" role="group">
                          <button
                            className={getRSVPButtonClass('yes', rsvps[event.id])}
                            onClick={() => handleRSVP(event.id, 'yes')}
                          >
                            <i className="fas fa-check me-1"></i>
                            Going
                          </button>
                          <button
                            className={getRSVPButtonClass('maybe', rsvps[event.id])}
                            onClick={() => handleRSVP(event.id, 'maybe')}
                          >
                            <i className="fas fa-question me-1"></i>
                            Maybe
                          </button>
                          <button
                            className={getRSVPButtonClass('no', rsvps[event.id])}
                            onClick={() => handleRSVP(event.id, 'no')}
                          >
                            <i className="fas fa-times me-1"></i>
                            Can't Go
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {event.description && (
                    <div className="card-body">
                      <p className="card-text text-muted mb-0">{event.description}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Events;
