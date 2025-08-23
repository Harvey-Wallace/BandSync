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
        const organizationId = localStorage.getItem('organization_id'); // Fix: use organization_id
        
        if (!token || !organizationId) {
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

        // Fetch all necessary data for analytics
        const [eventsResponse, rsvpResponse, allRsvpsResponse, usersResponse] = await Promise.all([
          axios.get(`${getApiUrl()}/events/organization/${organizationId}`, config),
          axios.get(`${getApiUrl()}/rsvps/user`, config),
          axios.get(`${getApiUrl()}/rsvps/all/${organizationId}`, config),
          axios.get(`${getApiUrl()}/users/organization/${organizationId}`, config)
        ]);

        setEvents(eventsResponse.data);
        
        // Convert user RSVP array to object for easier lookup
        const rsvpMap = {};
        if (rsvpResponse.data && Array.isArray(rsvpResponse.data)) {
          rsvpResponse.data.forEach(rsvp => {
            rsvpMap[rsvp.eventId] = rsvp.status;
          });
        }
        setRsvps(rsvpMap);

        // Process all RSVPs data for analytics
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

        setAllUsers(usersResponse.data || []);

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
