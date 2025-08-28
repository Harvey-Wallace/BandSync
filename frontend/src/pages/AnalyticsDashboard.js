import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import NotificationSystem from '../components/NotificationSystem';
import DashboardAnalytics from '../components/DashboardAnalytics';
import ParticipationInsights from '../components/ParticipationInsights';
import PerformanceSummary from '../components/PerformanceSummary';
import { 
  DataLoadingState, 
  ErrorState, 
  EmptyState 
} from '../components/LoadingComponents';
import { useTheme } from '../contexts/ThemeContext';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

function AnalyticsDashboard() {
  const [events, setEvents] = useState([]);
  const [rsvps, setRsvps] = useState({});
  const [allRsvps, setAllRsvps] = useState({});
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        
        if (!token) {
          setError('Authentication required. Please log in.');
          setLoading(false);
          return;
        }

        const config = {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        };

        // First get events using the basic endpoint (like EventsPage)
        const eventsResponse = await axios.get(`${getApiUrl()}/events`, config);
        const sortedEvents = eventsResponse.data.sort((a, b) => new Date(a.date) - new Date(b.date));
        setEvents(sortedEvents);

        // Get user's RSVPs using the same method as EventsPage
        const username = localStorage.getItem('username');
        const rsvpMap = {};
        for (const event of sortedEvents) {
          try {
            const rsvpRes = await axios.get(`${getApiUrl()}/events/${event.id}/rsvps`, config);
            // Find user's RSVP status
            for (const [rsvpStatus, users] of Object.entries(rsvpRes.data)) {
              // Skip metadata fields and ensure users is an array
              if (rsvpStatus.startsWith('_') || !Array.isArray(users)) {
                continue;
              }
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

        // Try to get organization-specific data for enhanced analytics
        const organizationId = localStorage.getItem('organization_id');
        if (organizationId) {
          try {
            // Use correct endpoints - admin/users for organization users
            const usersResponse = await axios.get(`${getApiUrl()}/admin/users`, config);
            
            console.log('Successfully loaded organization users for analytics');
            // Process the users data if needed for analytics
            // Note: All RSVPs data is already loaded per event above
            
            console.log('Successfully loaded organization users for analytics');
            setAllUsers(usersResponse.data || []);
            
            // All RSVPs are already loaded per event above in the main events loop
            // No need for a separate all RSVPs endpoint
            setAllRsvps({});
          } catch (orgError) {
            console.warn('Organization data not available:', orgError);
            // Continue with basic analytics
            setAllRsvps({});
            setAllUsers([]);
          }
        } else {
          // No organization context - use basic analytics only
          setAllRsvps({});
          setAllUsers([]);
        }

      } catch (error) {
        console.error('Error fetching analytics data:', error);
        if (error.response?.status === 401) {
          setError('Session expired. Please log in again.');
          localStorage.removeItem('token');
          window.location.href = '/login';
        } else {
          setError(error.response?.data?.message || 'Failed to load analytics data. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
    fetchAnalyticsData();
  }, []);

  if (loading) {
    return (
      <div className="min-vh-100 bg-light">
        <Navbar />
        <div className="container-fluid mt-4">
          <DataLoadingState 
            title="Loading Analytics Dashboard..."
            subtitle="Analyzing your participation data and generating insights"
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
            title="Unable to Load Analytics"
            message={error}
            onRetry={() => window.location.reload()}
          />
        </div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="min-vh-100 bg-light">
        <Navbar />
        <NotificationSystem />
        <div className="container-fluid mt-4">
          <EmptyState 
            title="No Analytics Data Available"
            message="Analytics will be available once your organization has events and participation data."
            actionText="View Events"
            onAction={() => window.location.href = '/events'}
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
                  <i className="fas fa-chart-line me-2 text-primary"></i>
                  Analytics Dashboard
                </h1>
                <p className="text-muted mb-0">Insights into your participation and performance</p>
              </div>
              <div className="d-flex align-items-center gap-3">
                <a href="/events" className="btn btn-outline-primary">
                  <i className="fas fa-calendar-alt me-2"></i>
                  Back to Events
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Analytics Components */}
        <div className="row g-4">
          {/* Main Dashboard Analytics */}
          <div className="col-12 stagger-item">
            <DashboardAnalytics 
              events={events} 
              rsvps={rsvps}
              allRsvps={allRsvps}
              role={role}
            />
          </div>

          {/* Participation Insights and Performance Summary */}
          <div className="col-lg-6 stagger-item">
            <ParticipationInsights 
              events={events} 
              rsvps={rsvps}
              allUsers={allUsers}
            />
          </div>

          <div className="col-lg-6 stagger-item">
            <PerformanceSummary 
              events={events} 
              rsvps={rsvps}
              allRsvps={allRsvps}
              allUsers={allUsers}
            />
          </div>
        </div>

        {/* Additional Analytics Sections */}
        <div className="row g-4 mt-2">
          <div className="col-12">
            <div className="card border-0 shadow-sm">
              <div className="card-header bg-white border-bottom">
                <h5 className="card-title mb-0">
                  <i className="fas fa-lightbulb me-2 text-warning"></i>
                  Quick Insights
                </h5>
              </div>
              <div className="card-body">
                <div className="row g-3">
                  <div className="col-md-4">
                    <div className="text-center p-3 bg-light rounded">
                      <div className="h4 text-primary mb-1">
                        {events.filter(event => new Date(event.dateTime) >= new Date()).length}
                      </div>
                      <div className="small text-muted">Upcoming Events</div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center p-3 bg-light rounded">
                      <div className="h4 text-success mb-1">
                        {Object.values(rsvps).filter(status => status === 'yes').length}
                      </div>
                      <div className="small text-muted">Events Attending</div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center p-3 bg-light rounded">
                      <div className="h4 text-info mb-1">
                        {Math.round((Object.values(rsvps).filter(status => status === 'yes').length / Object.keys(rsvps).length) * 100) || 0}%
                      </div>
                      <div className="small text-muted">Attendance Rate</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Spacing */}
        <div className="pb-5"></div>
      </div>
    </div>
  );
}

export default AnalyticsDashboard;
