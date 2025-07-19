import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { OrganizationProvider } from './contexts/OrganizationContext';
import SessionTimeout from './components/SessionTimeout';
import IOSDebugger from './components/IOSDebugger';
import IOSErrorBoundary from './components/IOSErrorBoundary';
import './utils/superAdminHelper'; // Import super admin helper for global access
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import PasswordResetPage from './pages/PasswordResetPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import SuperAdminPage from './pages/SuperAdminPage';
import EventsPage from './pages/EventsPage';
import ProfilePage from './pages/ProfilePage';
import EmailPreferencesPage from './pages/EmailPreferencesPage';
import CalendarIntegrationPage from './pages/CalendarIntegrationPage';
import MessagingPage from './pages/MessagingPage';
import SubstitutionPage from './pages/SubstitutionPage';
import BulkOperationsPage from './pages/BulkOperationsPage';
import QuickPollsPage from './pages/QuickPollsPage';
import './styles/custom.css';

console.log('🎯 App.js loading...');

function App() {
  console.log('🎯 App component rendering...');
  
  // iOS detection and simple fallback
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  
  if (isIOS) {
    console.log('📱 iOS detected in App.js');
    
    // Simple iOS fallback - just show a basic login for now
    return (
      <IOSErrorBoundary>
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
          <h1>BandSync</h1>
          <p>iOS Version Loading...</p>
          <div style={{ marginTop: '20px' }}>
            <ThemeProvider>
              <OrganizationProvider>
                <Router>
                  <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/reset-password" element={<PasswordResetPage />} />
                    <Route path="/change-password" element={<ChangePasswordPage />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/admin" element={<AdminDashboard />} />
                    <Route path="/super-admin" element={<SuperAdminPage />} />
                    <Route path="/events" element={<EventsPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/email-preferences" element={<EmailPreferencesPage />} />
                    <Route path="/calendar" element={<CalendarIntegrationPage />} />
                    <Route path="/messaging" element={<MessagingPage />} />
                    <Route path="/substitution" element={<SubstitutionPage />} />
                    <Route path="/bulk-operations" element={<BulkOperationsPage />} />
                    <Route path="/polls" element={<QuickPollsPage />} />
                    <Route path="*" element={<LoginPage />} />
                  </Routes>
                </Router>
              </OrganizationProvider>
            </ThemeProvider>
          </div>
        </div>
      </IOSErrorBoundary>
    );
  }
  
  return (
    <IOSErrorBoundary>
      <ThemeProvider>
        <OrganizationProvider>
          <IOSDebugger />
          <Router>
            <SessionTimeout />
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/reset-password" element={<PasswordResetPage />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/super-admin" element={<SuperAdminPage />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/email-preferences" element={<EmailPreferencesPage />} />
              <Route path="/calendar" element={<CalendarIntegrationPage />} />
              <Route path="/messaging" element={<MessagingPage />} />
              <Route path="/substitution" element={<SubstitutionPage />} />
              <Route path="/bulk-operations" element={<BulkOperationsPage />} />
              <Route path="/polls" element={<QuickPollsPage />} />
              <Route path="*" element={<LoginPage />} />
            </Routes>
          </Router>
        </OrganizationProvider>
      </ThemeProvider>
    </IOSErrorBoundary>
  );
}

export default App;
