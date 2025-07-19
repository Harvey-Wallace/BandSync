import React from 'react';

// Enhanced Loading Spinner
export const LoadingSpinner = ({ size = 'md', text = 'Loading...', className = '' }) => {
  const sizeClass = {
    sm: 'spinner-border-sm',
    md: '',
    lg: 'loading-spinner-enhanced'
  };

  return (
    <div className={`text-center py-3 ${className}`}>
      <div className={`spinner-border ${sizeClass[size]} text-primary`} role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
      {text && <div className="mt-2 text-muted">{text}</div>}
    </div>
  );
};

// Loading Button Component
export const LoadingButton = ({ 
  loading = false, 
  children, 
  className = '', 
  disabled = false,
  ...props 
}) => {
  return (
    <button 
      className={`btn ${loading ? 'btn-loading' : ''} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Processing...
        </>
      ) : (
        children
      )}
    </button>
  );
};

// Skeleton Loading Component
export const SkeletonLoader = ({ type = 'text', count = 1, className = '' }) => {
  const skeletons = Array.from({ length: count }, (_, index) => (
    <div key={index} className={`skeleton skeleton-${type} ${className}`}></div>
  ));

  return <div className="skeleton-container">{skeletons}</div>;
};

// Card Skeleton
export const CardSkeleton = ({ className = '' }) => {
  return (
    <div className={`card card-enhanced ${className}`}>
      <div className="card-body">
        <div className="skeleton skeleton-text" style={{ width: '60%' }}></div>
        <div className="skeleton skeleton-text" style={{ width: '100%' }}></div>
        <div className="skeleton skeleton-text" style={{ width: '80%' }}></div>
        <div className="skeleton skeleton-text" style={{ width: '40%' }}></div>
      </div>
    </div>
  );
};

// Table Skeleton
export const TableSkeleton = ({ rows = 5, columns = 4, className = '' }) => {
  return (
    <div className={`table-responsive ${className}`}>
      <table className="table table-enhanced">
        <thead>
          <tr>
            {Array.from({ length: columns }, (_, index) => (
              <th key={index}>
                <div className="skeleton skeleton-text" style={{ width: '80%' }}></div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }, (_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }, (_, colIndex) => (
                <td key={colIndex}>
                  <div className="skeleton skeleton-text" style={{ width: '70%' }}></div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Stats Card Skeleton
export const StatsCardSkeleton = ({ className = '' }) => {
  return (
    <div className={`card card-enhanced text-center ${className}`}>
      <div className="card-body">
        <div className="skeleton skeleton-text mx-auto mb-2" style={{ width: '60%', height: '1.5rem' }}></div>
        <div className="skeleton skeleton-text mx-auto mb-2" style={{ width: '40%', height: '2rem' }}></div>
        <div className="skeleton skeleton-text mx-auto" style={{ width: '80%', height: '1rem' }}></div>
      </div>
    </div>
  );
};

// Data Loading State Component
export const DataLoadingState = ({ 
  type = 'spinner', 
  message = 'Loading data...', 
  className = '' 
}) => {
  if (type === 'skeleton') {
    return (
      <div className={`row ${className}`}>
        {Array.from({ length: 4 }, (_, index) => (
          <div key={index} className="col-md-3 mb-3">
            <StatsCardSkeleton />
          </div>
        ))}
        <div className="col-12">
          <TableSkeleton />
        </div>
      </div>
    );
  }

  return <LoadingSpinner text={message} className={className} />;
};

// Error State Component
export const ErrorState = ({ 
  message = 'Something went wrong', 
  onRetry = null, 
  className = '' 
}) => {
  return (
    <div className={`error-container ${className}`}>
      <div className="error-icon">
        <i className="bi bi-exclamation-triangle"></i>
      </div>
      <div className="error-message">{message}</div>
      {onRetry && (
        <button className="btn btn-primary btn-enhanced" onClick={onRetry}>
          <i className="bi bi-arrow-clockwise me-2"></i>
          Try Again
        </button>
      )}
    </div>
  );
};

// Empty State Component
export const EmptyState = ({ 
  icon = 'inbox', 
  title = 'No data available', 
  description = 'There is no data to display at the moment.',
  action = null,
  className = '' 
}) => {
  return (
    <div className={`text-center py-5 ${className}`}>
      <div className="mb-3">
        <i className={`bi bi-${icon}`} style={{ fontSize: '3rem', color: '#6c757d' }}></i>
      </div>
      <h5 className="text-muted">{title}</h5>
      <p className="text-muted">{description}</p>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
};

// Success State Component
export const SuccessState = ({ 
  message = 'Operation completed successfully!', 
  action = null,
  className = '' 
}) => {
  return (
    <div className={`success-container ${className}`}>
      <div className="success-icon">
        <i className="bi bi-check-circle"></i>
      </div>
      <div className="success-message">{message}</div>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
};

export default {
  LoadingSpinner,
  LoadingButton,
  SkeletonLoader,
  CardSkeleton,
  TableSkeleton,
  StatsCardSkeleton,
  DataLoadingState,
  ErrorState,
  EmptyState,
  SuccessState
};
