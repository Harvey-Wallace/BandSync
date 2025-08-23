import React, { useMemo } from 'react';

const PerformanceSummary = ({ events, rsvps, allRsvps }) => {
  const performanceData = useMemo(() => {
    if (!events || events.length === 0) return null;

    const username = localStorage.getItem('username');
    const now = new Date();
    
    // Calculate user's performance
    const userResponses = Object.keys(rsvps).length;
    const userYesResponses = Object.values(rsvps).filter(rsvp => rsvp === 'Yes').length;
    const totalEvents = events.length;
    
    const userResponseRate = totalEvents > 0 ? (userResponses / totalEvents) * 100 : 0;
    const userAttendanceRate = userResponses > 0 ? (userYesResponses / userResponses) * 100 : 0;
    
    // Calculate organization averages
    let totalOrgResponses = 0;
    let totalOrgYesResponses = 0;
    let totalPossibleResponses = 0;
    
    Object.values(allRsvps).forEach(eventRsvps => {
      // Skip events without proper RSVP data
      if (!eventRsvps || typeof eventRsvps !== 'object') return;
      
      const yesCount = Array.isArray(eventRsvps.Yes) ? eventRsvps.Yes.length : 0;
      const noCount = Array.isArray(eventRsvps.No) ? eventRsvps.No.length : 0;
      const maybeCount = Array.isArray(eventRsvps.Maybe) ? eventRsvps.Maybe.length : 0;
      
      const eventTotalResponses = yesCount + noCount + maybeCount;
      totalOrgResponses += eventTotalResponses;
      totalOrgYesResponses += yesCount;
      
      // Estimate total possible responses (this is an approximation)
      // In a real scenario, you'd have the actual member count
      const estimatedMembers = Math.max(eventTotalResponses, 10); // Minimum assumption
      totalPossibleResponses += estimatedMembers;
    });
    
    const avgOrgResponseRate = totalPossibleResponses > 0 ? (totalOrgResponses / totalPossibleResponses) * 100 : 0;
    const avgOrgAttendanceRate = totalOrgResponses > 0 ? (totalOrgYesResponses / totalOrgResponses) * 100 : 0;
    
    // Calculate recent activity (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const recentEvents = events.filter(event => new Date(event.date) >= thirtyDaysAgo);
    const recentResponses = recentEvents.filter(event => rsvps[event.id]).length;
    const recentAttendance = recentEvents.filter(event => rsvps[event.id] === 'Yes').length;
    
    // Calculate performance indicators
    const responseComparison = userResponseRate - avgOrgResponseRate;
    const attendanceComparison = userAttendanceRate - avgOrgAttendanceRate;
    
    // Determine performance level
    let performanceLevel = 'Average';
    let performanceColor = 'warning';
    let performanceIcon = '📊';
    
    if (responseComparison > 20 && attendanceComparison > 10) {
      performanceLevel = 'Excellent';
      performanceColor = 'success';
      performanceIcon = '🌟';
    } else if (responseComparison > 10 || attendanceComparison > 5) {
      performanceLevel = 'Good';
      performanceColor = 'info';
      performanceIcon = '👍';
    } else if (responseComparison < -20 || attendanceComparison < -20) {
      performanceLevel = 'Needs Improvement';
      performanceColor = 'danger';
      performanceIcon = '📈';
    }
    
    return {
      user: {
        responseRate: Math.round(userResponseRate),
        attendanceRate: Math.round(userAttendanceRate),
        totalResponses: userResponses,
        totalAttendance: userYesResponses
      },
      organization: {
        avgResponseRate: Math.round(avgOrgResponseRate),
        avgAttendanceRate: Math.round(avgOrgAttendanceRate)
      },
      recent: {
        events: recentEvents.length,
        responses: recentResponses,
        attendance: recentAttendance
      },
      performance: {
        level: performanceLevel,
        color: performanceColor,
        icon: performanceIcon,
        responseComparison: Math.round(responseComparison),
        attendanceComparison: Math.round(attendanceComparison)
      }
    };
  }, [events, rsvps, allRsvps]);

  if (!performanceData) {
    return null;
  }

  const { user, organization, recent, performance } = performanceData;

  return (
    <div className="performance-summary mb-4">
      <div className="card card-enhanced">
        <div className="card-header">
          <h6 className="mb-0">
            <i className="bi bi-trophy me-2 text-warning"></i>
            Your Performance Summary
          </h6>
        </div>
        <div className="card-body">
          {/* Performance Level Badge */}
          <div className="text-center mb-4">
            <div className="performance-badge">
              <div className="performance-icon-large">{performance.icon}</div>
              <h5 className={`text-${performance.color} mb-1`}>{performance.level}</h5>
              <p className="text-muted mb-0">Overall Performance</p>
            </div>
          </div>

          {/* Comparison Metrics */}
          <div className="row g-3 mb-4">
            <div className="col-md-6">
              <div className="comparison-metric">
                <div className="metric-header">
                  <span className="metric-title">Response Rate</span>
                  <span className={`metric-comparison ${performance.responseComparison >= 0 ? 'text-success' : 'text-danger'}`}>
                    {performance.responseComparison >= 0 ? '+' : ''}{performance.responseComparison}%
                  </span>
                </div>
                <div className="metric-bars">
                  <div className="metric-bar">
                    <div className="bar-label">You</div>
                    <div className="bar-container">
                      <div 
                        className="bar-fill bg-primary" 
                        style={{ width: `${Math.min(user.responseRate, 100)}%` }}
                      ></div>
                    </div>
                    <div className="bar-value">{user.responseRate}%</div>
                  </div>
                  <div className="metric-bar">
                    <div className="bar-label">Avg</div>
                    <div className="bar-container">
                      <div 
                        className="bar-fill bg-secondary" 
                        style={{ width: `${Math.min(organization.avgResponseRate, 100)}%` }}
                      ></div>
                    </div>
                    <div className="bar-value">{organization.avgResponseRate}%</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="col-md-6">
              <div className="comparison-metric">
                <div className="metric-header">
                  <span className="metric-title">Attendance Rate</span>
                  <span className={`metric-comparison ${performance.attendanceComparison >= 0 ? 'text-success' : 'text-danger'}`}>
                    {performance.attendanceComparison >= 0 ? '+' : ''}{performance.attendanceComparison}%
                  </span>
                </div>
                <div className="metric-bars">
                  <div className="metric-bar">
                    <div className="bar-label">You</div>
                    <div className="bar-container">
                      <div 
                        className="bar-fill bg-success" 
                        style={{ width: `${Math.min(user.attendanceRate, 100)}%` }}
                      ></div>
                    </div>
                    <div className="bar-value">{user.attendanceRate}%</div>
                  </div>
                  <div className="metric-bar">
                    <div className="bar-label">Avg</div>
                    <div className="bar-container">
                      <div 
                        className="bar-fill bg-secondary" 
                        style={{ width: `${Math.min(organization.avgAttendanceRate, 100)}%` }}
                      ></div>
                    </div>
                    <div className="bar-value">{organization.avgAttendanceRate}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="recent-activity">
            <h6 className="mb-3">
              <i className="bi bi-clock-history me-2"></i>
              Last 30 Days
            </h6>
            <div className="row g-3">
              <div className="col-4">
                <div className="activity-stat">
                  <div className="activity-number">{recent.events}</div>
                  <div className="activity-label">Events</div>
                </div>
              </div>
              <div className="col-4">
                <div className="activity-stat">
                  <div className="activity-number">{recent.responses}</div>
                  <div className="activity-label">Responses</div>
                </div>
              </div>
              <div className="col-4">
                <div className="activity-stat">
                  <div className="activity-number">{recent.attendance}</div>
                  <div className="activity-label">Attended</div>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Tips */}
          <div className="performance-tips mt-4">
            <div className={`alert alert-${performance.color} alert-sm`}>
              <div className="d-flex align-items-center">
                <i className="bi bi-lightbulb me-2"></i>
                <div>
                  <strong>Tip:</strong>
                  {performance.level === 'Excellent' && ' Keep up the amazing work! Your engagement is inspiring others.'}
                  {performance.level === 'Good' && ' You\'re doing great! Consider responding to events a bit sooner.'}
                  {performance.level === 'Average' && ' Try to respond to more events to stay engaged with the group.'}
                  {performance.level === 'Needs Improvement' && ' Regular participation helps build a stronger musical community.'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceSummary;
