import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import Toast from '../components/Toast';
import Spinner from '../components/Spinner';

function EmailPreferencesPage() {
  const [preferences, setPreferences] = useState({
    email_notifications: true,
    email_event_reminders: true,
    email_new_events: true,
    email_rsvp_reminders: true,
    email_daily_summary: false,
    email_weekly_summary: true,
    email_substitute_requests: true,
    email_admin_attendance_reports: true,
    admin_attendance_report_timing: 120,
    admin_attendance_report_unit: 'minutes',
    email_admin_rsvp_changes: true,
    is_admin: false
  });
  const [timingOptions, setTimingOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/email/preferences');
      setPreferences(response.data);
      
      // Fetch timing options for admin users
      if (response.data.is_admin) {
        try {
          const timingResponse = await api.get('/email/admin/attendance-timing-options');
          setTimingOptions(timingResponse.data.timing_options);
        } catch (error) {
          console.error('Failed to load timing options:', error);
        }
      }
    } catch (error) {
      setToast({ type: 'error', message: 'Failed to load email preferences' });
    } finally {
      setLoading(false);
    }
  };

  const handlePreferenceChange = (field, value) => {
    setPreferences(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const savePreferences = async () => {
    setSaving(true);
    try {
      await api.put('/email/preferences', preferences);
      setToast({ type: 'success', message: 'Email preferences updated successfully' });
    } catch (error) {
      setToast({ type: 'error', message: 'Failed to update email preferences' });
    } finally {
      setSaving(false);
    }
  };

  const sendTestEmail = async () => {
    setSendingTest(true);
    try {
      await api.post('/email/test-email');
      setToast({ type: 'success', message: 'Test email sent successfully! Check your inbox.' });
    } catch (error) {
      setToast({ type: 'error', message: 'Failed to send test email' });
    } finally {
      setSendingTest(false);
    }
  };

  if (loading) {
    return <Spinner />;
  }

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title mb-0">
                <i className="fas fa-envelope me-2"></i>
                Email Preferences
              </h3>
            </div>
            <div className="card-body">
              <p className="text-muted mb-4">
                Manage your email notification preferences. You can choose which types of emails you'd like to receive.
              </p>

              <div className="row">
                <div className="col-md-12">
                  {/* Master Email Toggle */}
                  <div className="form-check mb-4 p-3 border rounded">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="email_notifications"
                      checked={preferences.email_notifications}
                      onChange={(e) => handlePreferenceChange('email_notifications', e.target.checked)}
                    />
                    <label className="form-check-label fw-bold" htmlFor="email_notifications">
                      Enable Email Notifications
                    </label>
                    <div className="form-text">
                      Master toggle for all email notifications. When disabled, you won't receive any emails from BandSync.
                    </div>
                  </div>

                  {/* Individual Email Preferences */}
                  <div className={`email-preferences ${!preferences.email_notifications ? 'opacity-50' : ''}`}>
                    <h5 className="mb-3">Email Types</h5>
                    
                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="email_event_reminders"
                        checked={preferences.email_event_reminders}
                        onChange={(e) => handlePreferenceChange('email_event_reminders', e.target.checked)}
                        disabled={!preferences.email_notifications}
                      />
                      <label className="form-check-label" htmlFor="email_event_reminders">
                        <strong>Event Reminders</strong>
                        <div className="form-text">Get reminded before upcoming events</div>
                      </label>
                    </div>

                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="email_new_events"
                        checked={preferences.email_new_events}
                        onChange={(e) => handlePreferenceChange('email_new_events', e.target.checked)}
                        disabled={!preferences.email_notifications}
                      />
                      <label className="form-check-label" htmlFor="email_new_events">
                        <strong>New Event Notifications</strong>
                        <div className="form-text">Get notified when new events are created</div>
                      </label>
                    </div>

                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="email_rsvp_reminders"
                        checked={preferences.email_rsvp_reminders}
                        onChange={(e) => handlePreferenceChange('email_rsvp_reminders', e.target.checked)}
                        disabled={!preferences.email_notifications}
                      />
                      <label className="form-check-label" htmlFor="email_rsvp_reminders">
                        <strong>RSVP Deadline Reminders</strong>
                        <div className="form-text">Get reminded to RSVP for events</div>
                      </label>
                    </div>

                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="email_substitute_requests"
                        checked={preferences.email_substitute_requests}
                        onChange={(e) => handlePreferenceChange('email_substitute_requests', e.target.checked)}
                        disabled={!preferences.email_notifications}
                      />
                      <label className="form-check-label" htmlFor="email_substitute_requests">
                        <strong>Substitute Requests</strong>
                        <div className="form-text">Get notified when members request substitutes</div>
                      </label>
                    </div>

                    <hr className="my-4" />

                    <h5 className="mb-3">Email Summaries</h5>

                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="email_daily_summary"
                        checked={preferences.email_daily_summary}
                        onChange={(e) => handlePreferenceChange('email_daily_summary', e.target.checked)}
                        disabled={!preferences.email_notifications}
                      />
                      <label className="form-check-label" htmlFor="email_daily_summary">
                        <strong>Daily Summary</strong>
                        <div className="form-text">Get a daily digest of today's and tomorrow's events (8 AM)</div>
                      </label>
                    </div>

                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="email_weekly_summary"
                        checked={preferences.email_weekly_summary}
                        onChange={(e) => handlePreferenceChange('email_weekly_summary', e.target.checked)}
                        disabled={!preferences.email_notifications}
                      />
                      <label className="form-check-label" htmlFor="email_weekly_summary">
                        <strong>Weekly Summary</strong>
                        <div className="form-text">Get a weekly digest of upcoming events (Monday 8 AM)</div>
                      </label>
                    </div>

                    {/* Admin Attendance Preferences */}
                    {preferences.is_admin && (
                      <>
                        <hr className="my-4" />
                        <h5 className="mb-3">
                          <i className="fas fa-users-cog me-2"></i>
                          Admin Attendance Notifications
                        </h5>
                        
                        <div className="form-check mb-3">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="email_admin_attendance_reports"
                            checked={preferences.email_admin_attendance_reports}
                            onChange={(e) => handlePreferenceChange('email_admin_attendance_reports', e.target.checked)}
                            disabled={!preferences.email_notifications}
                          />
                          <label className="form-check-label" htmlFor="email_admin_attendance_reports">
                            <strong>Event Attendance Reports</strong>
                            <div className="form-text">Get attendance reports before events showing who's coming</div>
                          </label>
                        </div>

                        {preferences.email_admin_attendance_reports && (
                          <div className="ms-4 mb-3 p-3 border rounded bg-light">
                            <label className="form-label">
                              <strong>Send report before event:</strong>
                            </label>
                            <select
                              className="form-select"
                              value={`${preferences.admin_attendance_report_timing}-${preferences.admin_attendance_report_unit}`}
                              onChange={(e) => {
                                const [timing, unit] = e.target.value.split('-');
                                handlePreferenceChange('admin_attendance_report_timing', parseInt(timing));
                                handlePreferenceChange('admin_attendance_report_unit', unit);
                              }}
                              disabled={!preferences.email_notifications}
                            >
                              {timingOptions.map((option) => (
                                <option 
                                  key={`${option.value}-${option.unit}`}
                                  value={`${option.value}-${option.unit}`}
                                >
                                  {option.label}
                                </option>
                              ))}
                            </select>
                            <div className="form-text mt-2">
                              Choose how far in advance you want to receive attendance reports
                            </div>
                          </div>
                        )}

                        <div className="form-check mb-3">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            id="email_admin_rsvp_changes"
                            checked={preferences.email_admin_rsvp_changes}
                            onChange={(e) => handlePreferenceChange('email_admin_rsvp_changes', e.target.checked)}
                            disabled={!preferences.email_notifications}
                          />
                          <label className="form-check-label" htmlFor="email_admin_rsvp_changes">
                            <strong>RSVP Change Notifications</strong>
                            <div className="form-text">Get notified when members change their RSVP after attendance report is sent</div>
                          </label>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="d-flex justify-content-between mt-4">
                <button
                  className="btn btn-outline-primary"
                  onClick={sendTestEmail}
                  disabled={sendingTest || !preferences.email_notifications}
                >
                  {sendingTest ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Sending Test Email...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-paper-plane me-2"></i>
                      Send Test Email
                    </>
                  )}
                </button>

                <button
                  className="btn btn-primary"
                  onClick={savePreferences}
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Saving...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-save me-2"></i>
                      Save Preferences
                    </>
                  )}
                </button>
              </div>

              <div className="mt-4 p-3 bg-light rounded">
                <h6 className="mb-2">
                  <i className="fas fa-info-circle me-2"></i>
                  Need to unsubscribe completely?
                </h6>
                <p className="text-muted mb-0">
                  You can use the unsubscribe link in any BandSync email to disable all email notifications instantly.
                </p>
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

export default EmailPreferencesPage;
