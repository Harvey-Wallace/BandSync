import React, { useMemo } from 'react';

const ParticipationInsights = ({ events, rsvps, allRsvps }) => {
  const insights = useMemo(() => {
    if (!events || events.length === 0) return null;

    const now = new Date();
    const username = localStorage.getItem('username');
    
    // Calculate streaks and patterns
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 0;
    
    // Get past events sorted by date
    const pastEvents = events
      .filter(event => new Date(event.date) < now)
      .sort((a, b) => new Date(b.date) - new Date(a.date)); // Most recent first
    
    // Calculate attendance streak
    for (const event of pastEvents) {
      const userRsvp = rsvps[event.id];
      if (userRsvp === 'Yes') {
        tempStreak++;
        if (currentStreak === tempStreak - 1) {
          currentStreak = tempStreak;
        }
        longestStreak = Math.max(longestStreak, tempStreak);
      } else if (userRsvp) {
        // Reset streak if user responded but didn't attend
        tempStreak = 0;
        if (currentStreak > 0) {
          currentStreak = 0;
        }
      }
    }
    
    // Calculate favorite event types
    const eventTypeStats = {};
    events.forEach(event => {
      const type = event.type || 'Other';
      if (!eventTypeStats[type]) {
        eventTypeStats[type] = { total: 0, attended: 0 };
      }
      eventTypeStats[type].total++;
      if (rsvps[event.id] === 'Yes') {
        eventTypeStats[type].attended++;
      }
    });
    
    // Find favorite event type
    let favoriteType = null;
    let highestAttendanceRate = 0;
    
    Object.entries(eventTypeStats).forEach(([type, stats]) => {
      if (stats.total >= 2) { // Only consider types with at least 2 events
        const rate = stats.attended / stats.total;
        if (rate > highestAttendanceRate) {
          highestAttendanceRate = rate;
          favoriteType = type;
        }
      }
    });
    
    // Calculate response time patterns
    let quickResponses = 0;
    let totalResponses = 0;
    
    events.forEach(event => {
      if (rsvps[event.id]) {
        totalResponses++;
        // Assume quick response if user has RSVP'd (we don't have timestamp data)
        // This could be enhanced with actual response timestamps
        quickResponses++;
      }
    });
    
    // Find next event needing RSVP
    const nextEvent = events
      .filter(event => new Date(event.date) >= now && !rsvps[event.id])
      .sort((a, b) => new Date(a.date) - new Date(b.date))[0];
    
    // Calculate upcoming event density
    const next30Days = new Date();
    next30Days.setDate(next30Days.getDate() + 30);
    
    const upcomingInMonth = events.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate >= now && eventDate <= next30Days;
    }).length;
    
    return {
      streaks: {
        current: currentStreak,
        longest: longestStreak
      },
      favorite: {
        eventType: favoriteType,
        attendanceRate: Math.round(highestAttendanceRate * 100)
      },
      response: {
        quickResponseRate: totalResponses > 0 ? Math.round((quickResponses / totalResponses) * 100) : 0,
        totalResponses
      },
      upcoming: {
        nextEvent,
        eventsThisMonth: upcomingInMonth,
        daysToNext: nextEvent ? Math.ceil((new Date(nextEvent.date) - now) / (1000 * 60 * 60 * 24)) : null
      }
    };
  }, [events, rsvps, allRsvps]);

  if (!insights) {
    return null;
  }

  const getStreakIcon = (streak) => {
    if (streak >= 10) return '🔥';
    if (streak >= 5) return '⭐';
    if (streak >= 3) return '👍';
    return '📅';
  };

  const getEventTypeIcon = (eventType) => {
    const icons = {
      'Performance': '🎵',
      'Rehearsal': '🎼',
      'Concert': '🎵',
      'Meeting': '💼',
      'Social': '🎉',
      'Other': '📅'
    };
    return icons[eventType] || icons['Other'];
  };

  return (
    <div className="participation-insights mb-4">
      <div className="card card-enhanced">
        <div className="card-header">
          <h6 className="mb-0">
            <i className="bi bi-lightbulb me-2 text-warning"></i>
            Your Participation Insights
          </h6>
        </div>
        <div className="card-body">
          <div className="row g-3">
            {/* Attendance Streak */}
            <div className="col-md-6 col-lg-3">
              <div className="insight-item">
                <div className="insight-icon">{getStreakIcon(insights.streaks.current)}</div>
                <div className="insight-content">
                  <div className="insight-title">Current Streak</div>
                  <div className="insight-value">
                    {insights.streaks.current} event{insights.streaks.current !== 1 ? 's' : ''}
                  </div>
                  <div className="insight-subtitle">
                    Best: {insights.streaks.longest}
                  </div>
                </div>
              </div>
            </div>

            {/* Favorite Event Type */}
            {insights.favorite.eventType && (
              <div className="col-md-6 col-lg-3">
                <div className="insight-item">
                  <div className="insight-icon">{getEventTypeIcon(insights.favorite.eventType)}</div>
                  <div className="insight-content">
                    <div className="insight-title">Favorite Type</div>
                    <div className="insight-value">{insights.favorite.eventType}</div>
                    <div className="insight-subtitle">
                      {insights.favorite.attendanceRate}% attendance
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Response Rate */}
            <div className="col-md-6 col-lg-3">
              <div className="insight-item">
                <div className="insight-icon">⚡</div>
                <div className="insight-content">
                  <div className="insight-title">Response Rate</div>
                  <div className="insight-value">{insights.response.quickResponseRate}%</div>
                  <div className="insight-subtitle">
                    {insights.response.totalResponses} total RSVPs
                  </div>
                </div>
              </div>
            </div>

            {/* Upcoming Activity */}
            <div className="col-md-6 col-lg-3">
              <div className="insight-item">
                <div className="insight-icon">
                  {insights.upcoming.eventsThisMonth >= 5 ? '🗓️' : 
                   insights.upcoming.eventsThisMonth >= 2 ? '📅' : '🕐'}
                </div>
                <div className="insight-content">
                  <div className="insight-title">This Month</div>
                  <div className="insight-value">
                    {insights.upcoming.eventsThisMonth} event{insights.upcoming.eventsThisMonth !== 1 ? 's' : ''}
                  </div>
                  {insights.upcoming.nextEvent && (
                    <div className="insight-subtitle">
                      Next in {insights.upcoming.daysToNext} day{insights.upcoming.daysToNext !== 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Next Action Recommendation */}
          {insights.upcoming.nextEvent && (
            <div className="row mt-3">
              <div className="col-12">
                <div className="insight-recommendation">
                  <div className="d-flex align-items-center">
                    <div className="recommendation-icon me-3">
                      <i className="bi bi-arrow-right-circle text-primary"></i>
                    </div>
                    <div className="flex-grow-1">
                      <strong>Action Needed:</strong> RSVP for "{insights.upcoming.nextEvent.title}"
                      <div className="text-muted small">
                        {new Date(insights.upcoming.nextEvent.date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          month: 'long',
                          day: 'numeric'
                        })} - {insights.upcoming.daysToNext} days away
                      </div>
                    </div>
                    <a href="#events" className="btn btn-sm btn-primary">
                      View Event
                    </a>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ParticipationInsights;
