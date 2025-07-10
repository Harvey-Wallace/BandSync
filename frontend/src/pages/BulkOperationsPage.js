import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import BulkOperations from '../components/BulkOperations';
import Toast from '../components/Toast';
import { useTheme } from '../contexts/ThemeContext';

function BulkOperationsPage() {
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const { orgThemeColor } = useTheme();
  const role = localStorage.getItem('role');
  
  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
  };

  const handleClose = () => {
    setToast({ show: false, message: '', type: 'success' });
  };

  // Only admins can access bulk operations
  if (role !== 'Admin') {
    return (
      <div className="min-vh-100" style={{ backgroundColor: '#f8f9fa' }}>
        <Navbar />
        <div className="container mt-5">
          <div className="alert alert-warning">
            <i className="bi bi-exclamation-triangle me-2"></i>
            You don't have permission to access bulk operations. Admin access required.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100" style={{ backgroundColor: '#f8f9fa' }}>
      <Navbar />
      
      <div className="container-fluid mt-3">
        <div className="row">
          <div className="col-12">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h1 className="h3 mb-0">
                <i className="bi bi-stack me-2" style={{ color: orgThemeColor }}></i>
                Bulk Operations
              </h1>
            </div>
            
            <div className="row">
              <div className="col-12">
                <BulkOperations showToast={showToast} />
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

export default BulkOperationsPage;
