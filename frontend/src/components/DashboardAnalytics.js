import React, { useState, useEffect, useMemo } from 'react';
import { getApiUrl } from '../utils/apiUrl';
import axios from 'axios';

const DashboardAnalytics = ({ events, rsvps, allRsvps }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('3months'); // 1month, 3months, 6months, 1year

  // Calculate analytics from events and RSVP data
  const analytics = useMemo(() => {
    if (!events || events.length === 0) return null;

    const now = new Date();
    const username = localStorage.getItem('username');
    
    // Filter events based on timeframe
    const getDateThreshold = (timeframe) => {
      const date = new Date();
      switch (timeframe) {
        case '1month':
          date.setMonth(date.getMonth() - 1);
          break;
        case '3months':
          date.setMonth(date.getMonth() - 3);
          break;
        case '6months':
          date.setMonth(date.getMonth() - 6);
          break;
        case '1year':
          date.setFullYear(date.getFullYear() - 1);
          break;
        default:
          date.setMonth(date.getMonth() - 3);
      }
      return date;
    };

    const threshold = getDateThreshold(timeframe);
    const timeframeEvents = events.filter(event => new Date(event.date) >= threshold);
    
    // Calculate participation metrics
    const totalEvents = timeframeEvents.length;
    const upcomingEvents = timeframeEvents.filter(event => new Date(event.date) >= now).length;
    const pastEvents = timeframeEvents.filter(event => new Date(event.date) < now).length;
    
    // Calculate RSVP statistics
    let attendedCount = 0;
    let respondedCount = 0;
    let yesRsvps = 0;
    let noRsvps = 0;
    let maybeRsvps = 0;
    
    const monthlyData = {};
    const eventTypeBreakdown = {};
    const rsvpTrends = [];
    
    timeframeEvents.forEach(event => {
      const eventDate = new Date(event.date);
      const monthKey = `${eventDate.getFullYear()}-${String(eventDate.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = {
          total: 0,
          attended: 0,
          responded: 0,
          yes: 0,
          no: 0,
          maybe: 0
        };
      }
      
      monthlyData[monthKey].total++;
      
      // Track event types
      const eventType = event.type || 'Other';
      if (!eventTypeBreakdown[eventType]) {
        eventTypeBreakdown[eventType] = { total: 0, attended: 0 };
      }
      eventTypeBreakdown[eventType].total++;
      
      // Check user's RSVP for this event
      const userRsvp = rsvps[event.id];
      if (userRsvp) {
        respondedCount++;
        monthlyData[monthKey].responded++;
        
        switch (userRsvp) {
          case 'Yes':
            yesRsvps++;
            monthlyData[monthKey].yes++;
            if (eventDate < now) {
              attendedCount++;
              monthlyData[monthKey].attended++;
              eventTypeBreakdown[eventType].attended++;
            }
            break;
          case 'No':
            noRsvps++;
            monthlyData[monthKey].no++;
            break;
          case 'Maybe':
            maybeRsvps++;
            monthlyData[monthKey].maybe++;
            break;
        }
        
        // Add to trends data
        rsvpTrends.push({
          date: eventDate,
          event: event.title,
          type: event.type,
          rsvp: userRsvp,
          eventId: event.id
        });
      }
    });
    
    // Calculate percentages
    const responseRate = totalEvents > 0 ? Math.round((respondedCount / totalEvents) * 100) : 0;
    const attendanceRate = yesRsvps > 0 ? Math.round((attendedCount / yesRsvps) * 100) : 0;
    const yesRate = respondedCount > 0 ? Math.round((yesRsvps / respondedCount) * 100) : 0;
    
    // Calculate engagement score (0-100)
    const engagementScore = Math.round((responseRate * 0.4) + (attendanceRate * 0.4) + (yesRate * 0.2));
    
    // Sort monthly data by date
    const sortedMonthlyData = Object.entries(monthlyData)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, data]) => ({
        month,
        ...data,
        monthName: new Date(month + '-01').toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
      }));
    
    // Find upcoming events needing RSVP
    const upcomingNeedingRsvp = events.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate >= now && !rsvps[event.id];
    }).slice(0, 5);
    
    // Find events with deadlines approaching (within 7 days)
    const urgentDeadlines = events.filter(event => {
      const eventDate = new Date(event.date);
      const daysUntilEvent = Math.ceil((eventDate - now) / (1000 * 60 * 60 * 24));
      return daysUntilEvent > 0 && daysUntilEvent <= 7 && !rsvps[event.id];
    });

    return {
      summary: {
        totalEvents,
        upcomingEvents,
        pastEvents,
        respondedCount,
        responseRate,
        attendanceRate,
        engagementScore,
        yesRsvps,
        noRsvps,
        maybeRsvps
      },
      trends: {
        monthlyData: sortedMonthlyData,
        rsvpTrends: rsvpTrends.sort((a, b) => a.date - b.date),
        eventTypeBreakdown
      },
      actionItems: {
        upcomingNeedingRsvp,
        urgentDeadlines
      }
    };
  }, [events, rsvps, timeframe]);

  // Fetch additional analytics data from backend if needed
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        // We can add backend analytics calls here if needed
        // For now, we're using client-side calculations
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
        setLoading(false);
      }
    };

    if (events && events.length > 0) {
      fetchAnalytics();
    }
  }, [events, timeframe]);

  if (loading || !analytics) {
    return (
      <div className="card card-enhanced mb-4">
        <div className="card-body text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading analytics...</span>
          </div>
          <p className="mt-2 text-muted">Analyzing your participation data...</p>
        </div>
      </div>
    );
  }

  const { summary, trends, actionItems } = analytics;

  return (
    <div className="analytics-dashboard mb-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">
          <i className="bi bi-graph-up me-2 text-primary"></i>
          Your Participation Analytics
        </h5>
        <div className="btn-group btn-group-sm">
          {[
            { key: '1month', label: '1M' },
            { key: '3months', label: '3M' },
            { key: '6months', label: '6M' },
            { key: '1year', label: '1Y' }
          ].map(({ key, label }) => (
            <button
              key={key}
              className={`btn ${timeframe === key ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setTimeframe(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="row g-3 mb-4">
        <div className="col-6 col-md-3">
          <div className="card analytics-card h-100">
            <div className="card-body text-center">
              <div className="analytics-icon text-primary mb-2">
                <i className="bi bi-calendar-check"></i>
              </div>
              <h3 className="analytics-number">{summary.totalEvents}</h3>
              <p className="analytics-label mb-0">Total Events</p>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="card analytics-card h-100">
            <div className="card-body text-center">
              <div className="analytics-icon text-success mb-2">
                <i className="bi bi-percent"></i>
              </div>
              <h3 className="analytics-number">{summary.responseRate}%</h3>
              <p className="analytics-label mb-0">Response Rate</p>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="card analytics-card h-100">
            <div className="card-body text-center">
              <div className="analytics-icon text-info mb-2">
                <i className="bi bi-person-check"></i>
              </div>
              <h3 className="analytics-number">{summary.attendanceRate}%</h3>
              <p className="analytics-label mb-0">Attendance Rate</p>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="card analytics-card h-100">
            <div className="card-body text-center">
              <div className="analytics-icon text-warning mb-2">
                <i className="bi bi-star-fill"></i>
              </div>
              <h3 className="analytics-number">{summary.engagementScore}</h3>
              <p className="analytics-label mb-0">Engagement Score</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="row g-4 mb-4">
        {/* RSVP Distribution */}
        <div className="col-md-6">
          <div className="card analytics-card h-100">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="bi bi-pie-chart me-2"></i>
                RSVP Distribution
              </h6>
            </div>
            <div className="card-body">
              {summary.respondedCount > 0 ? (
                <div className="rsvp-donut-chart">
                  <div className="text-center mb-3">
                    <div className="rsvp-chart-container">
                      <svg width="160" height="160" className="mx-auto">
                        <circle
                          cx="80"
                          cy="80"
                          r="60"
                          fill="none"
                          stroke="#e9ecef"
                          strokeWidth="20"
                        />
                        <circle
                          cx="80"
                          cy="80"
                          r="60"
                          fill="none"
                          stroke="#28a745"
                          strokeWidth="20"
                          strokeDasharray={`${(summary.yesRsvps / summary.respondedCount) * 377} 377`}
                          strokeDashoffset="0"
                          transform="rotate(-90 80 80)"
                        />
                        <circle
                          cx="80"
                          cy="80"
                          r="60"
                          fill="none"
                          stroke="#ffc107"
                          strokeWidth="20"
                          strokeDasharray={`${(summary.maybeRsvps / summary.respondedCount) * 377} 377`}
                          strokeDashoffset={`-${(summary.yesRsvps / summary.respondedCount) * 377}`}
                          transform="rotate(-90 80 80)"
                        />
                        <text x="80" y="85" textAnchor="middle" className="analytics-chart-text">
                          {summary.respondedCount}
                        </text>
                        <text x="80" y="100" textAnchor="middle" className="analytics-chart-subtext">
                          RSVPs
                        </text>
                      </svg>
                    </div>
                  </div>
                  <div className="rsvp-legend">
                    <div className="d-flex justify-content-between">
                      <div className="legend-item">
                        <span className="legend-color bg-success"></span>
                        <span className="legend-text">Yes ({summary.yesRsvps})</span>
                      </div>
                      <div className="legend-item">
                        <span className="legend-color bg-warning"></span>
                        <span className="legend-text">Maybe ({summary.maybeRsvps})</span>
                      </div>
                      <div className="legend-item">
                        <span className="legend-color bg-danger"></span>
                        <span className="legend-text">No ({summary.noRsvps})</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted py-4">
                  <i className="bi bi-bar-chart display-4 mb-3"></i>
                  <p>No RSVP data available for the selected timeframe</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Monthly Trend */}
        <div className="col-md-6">
          <div className="card analytics-card h-100">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="bi bi-graph-up me-2"></i>
                Monthly Participation Trend
              </h6>
            </div>
            <div className="card-body">
              {trends.monthlyData.length > 0 ? (
                <div className="trend-chart">
                  <div className="chart-container">
                    {trends.monthlyData.map((month, index) => {
                      const maxHeight = 80;
                      const maxEvents = Math.max(...trends.monthlyData.map(m => m.total));
                      const height = maxEvents > 0 ? (month.total / maxEvents) * maxHeight : 0;
                      
                      return (
                        <div key={month.month} className="chart-bar-group">
                          <div className="chart-bar-container" style={{ height: `${maxHeight}px` }}>
                            <div 
                              className="chart-bar chart-bar-total"
                              style={{ height: `${height}px` }}
                              title={`${month.total} total events`}
                            ></div>
                            <div 
                              className="chart-bar chart-bar-attended"
                              style={{ 
                                height: `${maxEvents > 0 ? (month.yes / maxEvents) * maxHeight : 0}px` 
                              }}
                              title={`${month.yes} attended`}
                            ></div>
                          </div>
                          <div className="chart-label">{month.monthName}</div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="chart-legend mt-3">
                    <div className="d-flex justify-content-center gap-3">
                      <div className="legend-item">
                        <span className="legend-color chart-color-total"></span>
                        <span className="legend-text">Total Events</span>
                      </div>
                      <div className="legend-item">
                        <span className="legend-color chart-color-attended"></span>
                        <span className="legend-text">Attended</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted py-4">
                  <i className="bi bi-graph-up display-4 mb-3"></i>
                  <p>No trend data available for the selected timeframe</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Action Items */}
      {(actionItems.urgentDeadlines.length > 0 || actionItems.upcomingNeedingRsvp.length > 0) && (
        <div className="row g-4">
          {/* Urgent Deadlines */}
          {actionItems.urgentDeadlines.length > 0 && (
            <div className="col-md-6">
              <div className="card analytics-card border-warning">
                <div className="card-header bg-warning bg-opacity-10">
                  <h6 className="mb-0 text-warning">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    Urgent: RSVP Needed
                  </h6>
                </div>
                <div className="card-body">
                  {actionItems.urgentDeadlines.map(event => {
                    const daysUntil = Math.ceil((new Date(event.date) - new Date()) / (1000 * 60 * 60 * 24));
                    return (
                      <div key={event.id} className="deadline-item">
                        <div className="d-flex justify-content-between align-items-center">
                          <div>
                            <strong>{event.title}</strong>
                            <div className="text-muted small">
                              {new Date(event.date).toLocaleDateString('en-US', {
                                weekday: 'long',
                                month: 'short',
                                day: 'numeric'
                              })}
                            </div>
                          </div>
                          <div className="text-end">
                            <span className="badge bg-warning">{daysUntil} day{daysUntil !== 1 ? 's' : ''}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Upcoming Events Needing RSVP */}
          {actionItems.upcomingNeedingRsvp.length > 0 && (
            <div className="col-md-6">
              <div className="card analytics-card border-info">
                <div className="card-header bg-info bg-opacity-10">
                  <h6 className="mb-0 text-info">
                    <i className="bi bi-clock me-2"></i>
                    Pending RSVPs
                  </h6>
                </div>
                <div className="card-body">
                  {actionItems.upcomingNeedingRsvp.slice(0, 5).map(event => (
                    <div key={event.id} className="deadline-item">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <strong>{event.title}</strong>
                          <div className="text-muted small">
                            {new Date(event.date).toLocaleDateString('en-US', {
                              weekday: 'long',
                              month: 'short',
                              day: 'numeric'
                            })}
                          </div>
                        </div>
                        <div>
                          <span className="badge bg-info">Pending</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  {actionItems.upcomingNeedingRsvp.length > 5 && (
                    <div className="text-center mt-2">
                      <small className="text-muted">
                        +{actionItems.upcomingNeedingRsvp.length - 5} more events
                      </small>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DashboardAnalytics;
