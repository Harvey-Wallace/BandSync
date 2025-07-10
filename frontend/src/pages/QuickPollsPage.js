import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import QuickPolls from '../components/QuickPolls';
import Toast from '../components/Toast';
import { useTheme } from '../contexts/ThemeContext';

function QuickPollsPage() {
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const { orgThemeColor } = useTheme();
  
  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
  };

  const handleClose = () => {
    setToast({ show: false, message: '', type: 'success' });
  };

  return (
    <div className="min-vh-100" style={{ backgroundColor: '#f8f9fa' }}>
      <Navbar />
      
      <div className="container-fluid mt-3">
        <div className="row">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h1 className="h3 mb-0">
                <i className="bi bi-bar-chart me-2" style={{ color: orgThemeColor }}></i>
                Quick Polls
              </h1>
            </div>
            
            <div className="row">
              <div className="col-12">
                <QuickPolls showToast={showToast} />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <Toast 
        show={toast.show} 
        message={toast.message} 
        type={toast.type} 
        onClose={handleClose}
      />
    </div>
  );
}

export default QuickPollsPage;
