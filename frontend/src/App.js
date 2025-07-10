import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { OrganizationProvider } from './contexts/OrganizationContext';
import SessionTimeout from './components/SessionTimeout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import EventsPage from './pages/EventsPage';
import ProfilePage from './pages/ProfilePage';
import EmailPreferencesPage from './pages/EmailPreferencesPage';
import CalendarIntegrationPage from './pages/CalendarIntegrationPage';
import MessagingPage from './pages/MessagingPage';
import SubstitutionPage from './pages/SubstitutionPage';
import BulkOperationsPage from './pages/BulkOperationsPage';
import QuickPollsPage from './pages/QuickPollsPage';
import './styles/custom.css';

function App() {
  return (
    <ThemeProvider>
      <OrganizationProvider>
        <Router>
          <SessionTimeout />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
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
  );
}

export default App;
