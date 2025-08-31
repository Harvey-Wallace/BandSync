import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { OrganizationProvider } from './contexts/OrganizationContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { NotificationToastContainer } from './components/NotificationComponents';
import SessionTimeout from './components/SessionTimeout';
import IOSDebugger from './components/IOSDebugger';
import IOSErrorBoundary from './components/IOSErrorBoundary';
import ErrorBoundary from './components/ErrorBoundary';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import PasswordResetPage from './pages/PasswordResetPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import MagicLoginPage from './pages/MagicLoginPage';
import Dashboard from './pages/Dashboard';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AdminDashboard from './pages/AdminDashboard';
import Events from './pages/Events';
import EventsPage from './pages/EventsPage';
import ProfilePage from './pages/ProfilePage';
import EmailPreferencesPage from './pages/EmailPreferencesPage';
import CalendarIntegrationPage from './pages/CalendarIntegrationPage';
import MessagingPage from './pages/MessagingPage';
import SubstitutionPage from './pages/SubstitutionPage';
import BulkOperationsPage from './pages/BulkOperationsPage';
import QuickPollsPage from './pages/QuickPollsPage';
import AdminOversightPage from './pages/AdminOversightPage';
import MultipleDatesDemo from './pages/MultipleDatesDemo';
import SubscriptionPage from './pages/Subscription';
import SubscriptionSuccess from './pages/SubscriptionSuccess';
import './styles/custom.css';

console.log('🎯 App.js loading...');

function App() {
  console.log('🎯 App component rendering...');
  
  // Initialize WebSocket notifications
  useEffect(() => {
    console.log('🔔 WebSocket notification system initialized');
  }, []);
  
  // Precise iOS detection - only actual iOS devices, not macOS Safari
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && 
                !window.MSStream && 
                !(/Macintosh|Intel Mac OS X/.test(navigator.userAgent));
  
  console.log('🔍 Device detection:', {
    userAgent: navigator.userAgent,
    isIOS: isIOS,
    isMac: /Macintosh|Intel Mac OS X/.test(navigator.userAgent)
  });
  
  if (isIOS) {
    console.log('📱 iOS detected in App.js');
    
    // Simple iOS fallback - just show a basic login for now
    return (
      <ErrorBoundary>
        <IOSErrorBoundary>
          <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>BandSync</h1>
            <p>iOS Version Loading...</p>
            <div style={{ marginTop: '20px' }}>
              <ThemeProvider>
                <OrganizationProvider>
                  <WebSocketProvider>
                    <Router>
                      <NotificationToastContainer />
                      <Routes>
                      <Route path="/login" element={<LoginPage />} />
                      <Route path="/register" element={<RegisterPage />} />
                      <Route path="/reset-password" element={<PasswordResetPage />} />
                      <Route path="/change-password" element={<ChangePasswordPage />} />
                      <Route path="/magic-login" element={<MagicLoginPage />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/analytics" element={<AnalyticsDashboard />} />
                      <Route path="/admin" element={<AdminDashboard />} />
                      <Route path="/events" element={<Events />} />
                      <Route path="/events-old" element={<EventsPage />} />
                      <Route path="/profile" element={<ProfilePage />} />
                      <Route path="/email-preferences" element={<EmailPreferencesPage />} />
                      <Route path="/calendar" element={<CalendarIntegrationPage />} />
                      <Route path="/messaging" element={<MessagingPage />} />
                      <Route path="/substitution" element={<SubstitutionPage />} />
                      <Route path="/bulk-operations" element={<BulkOperationsPage />} />
                      <Route path="/polls" element={<QuickPollsPage />} />
                      <Route path="/admin-oversight" element={<AdminOversightPage />} />
                      <Route path="/multiple-dates-demo" element={<MultipleDatesDemo />} />
                      <Route path="/subscription" element={<SubscriptionPage />} />
                      <Route path="/subscription/success" element={<SubscriptionSuccess />} />
                      <Route path="*" element={<LoginPage />} />
                    </Routes>
                  </Router>
                </WebSocketProvider>
              </OrganizationProvider>
            </ThemeProvider>
            </div>
          </div>
        </IOSErrorBoundary>
      </ErrorBoundary>
    );
  }
  
  return (
    <ErrorBoundary>
      <IOSErrorBoundary>
        <ThemeProvider>
          <OrganizationProvider>
            <WebSocketProvider>
              <IOSDebugger />
              <Router>
                <NotificationToastContainer />
                <SessionTimeout />
                <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/reset-password" element={<PasswordResetPage />} />
                <Route path="/change-password" element={<ChangePasswordPage />} />
                <Route path="/magic-login" element={<MagicLoginPage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/events" element={<Events />} />
                <Route path="/events-old" element={<EventsPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/email-preferences" element={<EmailPreferencesPage />} />
                <Route path="/calendar" element={<CalendarIntegrationPage />} />
                <Route path="/messaging" element={<MessagingPage />} />
                <Route path="/substitution" element={<SubstitutionPage />} />
                <Route path="/bulk-operations" element={<BulkOperationsPage />} />
                <Route path="/polls" element={<QuickPollsPage />} />
                <Route path="/admin-oversight" element={<AdminOversightPage />} />
                <Route path="/multiple-dates-demo" element={<MultipleDatesDemo />} />
                <Route path="/subscription" element={<SubscriptionPage />} />
                <Route path="/subscription/success" element={<SubscriptionSuccess />} />
                <Route path="*" element={<LoginPage />} />
              </Routes>
            </Router>
          </WebSocketProvider>
        </OrganizationProvider>
      </ThemeProvider>
    </IOSErrorBoundary>
  </ErrorBoundary>
  );
}

export default App;
