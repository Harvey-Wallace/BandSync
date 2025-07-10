import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import Toast from '../components/Toast';
import Spinner from '../components/Spinner';

function CalendarIntegrationPage() {
  const [calendars, setCalendars] = useState({});
  const [loading, setLoading] = useState(true);
  const [copying, setCopying] = useState({});
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchCalendarInfo();
  }, []);

  const fetchCalendarInfo = async () => {
    try {
      const response = await api.get('/calendar/subscription-info');
      setCalendars(response.data.calendars);
    } catch (error) {
      setToast({ type: 'error', message: 'Failed to load calendar information' });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text, calendarType) => {
    setCopying({ ...copying, [calendarType]: true });
    try {
      await navigator.clipboard.writeText(text);
      setToast({ type: 'success', message: 'Calendar URL copied to clipboard!' });
    } catch (error) {
      setToast({ type: 'error', message: 'Failed to copy URL' });
    } finally {
      setCopying({ ...copying, [calendarType]: false });
    }
  };

  const downloadCalendar = (url, name) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = `${name.replace(/[^a-z0-9]/gi, '_')}_calendar.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderCalendarCard = (calendar, type, title) => (
    <div className="card mb-3" key={type}>
      <div className="card-body">
        <h5 className="card-title">
          <i className="fas fa-calendar-alt me-2"></i>
          {title}
        </h5>
        <p className="card-text text-muted">{calendar.description}</p>
        
        <div className="input-group mb-3">
          <input
            type="text"
            className="form-control"
            value={calendar.url}
            readOnly
            style={{ fontSize: '12px' }}
          />
          <button
            className="btn btn-outline-primary"
            onClick={() => copyToClipboard(calendar.url, type)}
            disabled={copying[type]}
          >
            {copying[type] ? (
              <span className="spinner-border spinner-border-sm me-1"></span>
            ) : (
              <i className="fas fa-copy me-1"></i>
            )}
            Copy URL
          </button>
        </div>
        
        <div className="d-flex gap-2 flex-wrap">
          <button
            className="btn btn-sm btn-success"
            onClick={() => downloadCalendar(calendar.url, calendar.name)}
          >
            <i className="fas fa-download me-1"></i>
            Download .ics
          </button>
          
          <a
            href={`https://calendar.google.com/calendar/render?cid=${encodeURIComponent(calendar.url)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-sm btn-info"
          >
            <i className="fab fa-google me-1"></i>
            Add to Google
          </a>
          
          <a
            href={`outlook://calendar/action/compose?subject=${encodeURIComponent(calendar.name)}&body=${encodeURIComponent(calendar.url)}`}
            className="btn btn-sm btn-warning"
          >
            <i className="fab fa-microsoft me-1"></i>
            Add to Outlook
          </a>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return <Spinner />;
  }

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-md-10">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title mb-0">
                <i className="fas fa-calendar-plus me-2"></i>
                Calendar Integration
              </h3>
            </div>
            <div className="card-body">
              <div className="alert alert-info">
                <i className="fas fa-info-circle me-2"></i>
                <strong>Calendar Sync:</strong> Subscribe to these calendar feeds to automatically sync BandSync events with your favorite calendar app. The calendars will update automatically when events are added or changed.
              </div>

              <div className="row">
                <div className="col-md-12">
                  <h4 className="mb-3">Available Calendar Feeds</h4>
                  
                  {/* Organization Calendar */}
                  {calendars.organization && renderCalendarCard(
                    calendars.organization,
                    'organization',
                    'Organization Calendar'
                  )}
                  
                  {/* Personal Calendar */}
                  {calendars.user && renderCalendarCard(
                    calendars.user,
                    'user',
                    'Personal Calendar'
                  )}
                  
                  {/* Section Calendars */}
                  {calendars.sections && calendars.sections.map((section, index) => 
                    renderCalendarCard(
                      section,
                      `section-${index}`,
                      `Section: ${section.name.split(' - ')[1]}`
                    )
                  )}
                  
                  {/* Public Calendar */}
                  {calendars.public && renderCalendarCard(
                    calendars.public,
                    'public',
                    'Public Calendar'
                  )}
                </div>
              </div>

              <div className="mt-4">
                <h4 className="mb-3">How to Subscribe</h4>
                <div className="row">
                  <div className="col-md-4">
                    <div className="card h-100">
                      <div className="card-body">
                        <h5 className="card-title">
                          <i className="fab fa-google me-2"></i>
                          Google Calendar
                        </h5>
                        <ol className="card-text">
                          <li>Click "Add to Google" button above</li>
                          <li>Or copy the calendar URL</li>
                          <li>In Google Calendar, click "+" → "From URL"</li>
                          <li>Paste the URL and click "Add Calendar"</li>
                        </ol>
                      </div>
                    </div>
                  </div>
                  
                  <div className="col-md-4">
                    <div className="card h-100">
                      <div className="card-body">
                        <h5 className="card-title">
                          <i className="fab fa-microsoft me-2"></i>
                          Outlook
                        </h5>
                        <ol className="card-text">
                          <li>Copy the calendar URL</li>
                          <li>In Outlook, go to Calendar</li>
                          <li>Click "Add Calendar" → "From Internet"</li>
                          <li>Paste the URL and click "OK"</li>
                        </ol>
                      </div>
                    </div>
                  </div>
                  
                  <div className="col-md-4">
                    <div className="card h-100">
                      <div className="card-body">
                        <h5 className="card-title">
                          <i className="fab fa-apple me-2"></i>
                          Apple Calendar
                        </h5>
                        <ol className="card-text">
                          <li>Copy the calendar URL</li>
                          <li>In Calendar, go to File → New Calendar Subscription</li>
                          <li>Paste the URL and click "Subscribe"</li>
                          <li>Choose your sync settings</li>
                        </ol>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-light rounded">
                <h6 className="mb-2">
                  <i className="fas fa-lightbulb me-2"></i>
                  Tips for Better Calendar Sync
                </h6>
                <ul className="mb-0">
                  <li><strong>Automatic Updates:</strong> Your subscribed calendars will automatically update when events change in BandSync</li>
                  <li><strong>Personal Calendar:</strong> Shows only events relevant to you with your RSVP status</li>
                  <li><strong>Organization Calendar:</strong> Shows all events for your organization</li>
                  <li><strong>Public Calendar:</strong> Perfect for sharing on your band's website</li>
                  <li><strong>Mobile Sync:</strong> Calendar subscriptions work on mobile devices too</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

export default CalendarIntegrationPage;
