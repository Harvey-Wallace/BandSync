import React from 'react';

// Enhanced Loading Spinner with modern styles
export const LoadingSpinner = ({ size = 'md', text = 'Loading...', className = '', variant = 'primary' }) => {
  const sizeClass = {
    sm: 'loading-spinner-sm',
    md: 'loading-spinner',
    lg: 'loading-spinner-lg'
  };

  return (
    <div className={`text-center py-3 fade-in ${className}`}>
      <div className={`${sizeClass[size]} mx-auto`} style={{ borderTopColor: `var(--theme-${variant})` }}>
        <span className="visually-hidden">Loading...</span>
      </div>
      {text && <div className="mt-2 text-muted page-loading-text">{text}</div>}
    </div>
  );
};

// Enhanced Loading Dots Animation
export const LoadingDots = ({ text = 'Loading', className = '' }) => {
  return (
    <div className={`text-center py-3 fade-in ${className}`}>
      <div className="loading-dots mb-2">
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
      </div>
      <div className="page-loading-text">{text}</div>
    </div>
  );
};

// Loading Button Component with enhanced states
export const LoadingButton = ({ 
  loading = false, 
  children, 
  className = '', 
  disabled = false,
  loadingText = 'Processing...',
  ...props 
}) => {
  return (
    <button 
      className={`btn transition-all duration-200 ${loading ? 'btn-loading' : ''} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="loading-spinner-sm me-2" role="status" aria-hidden="true"></span>
          <span className="btn-text">{loadingText}</span>
        </>
      ) : (
        <span className="btn-text">{children}</span>
      )}
    </button>
  );
};

// Enhanced Skeleton Loading Component
export const SkeletonLoader = ({ type = 'text', count = 1, className = '', width = '100%' }) => {
  const skeletons = Array.from({ length: count }, (_, index) => (
    <div 
      key={index} 
      className={`skeleton skeleton-${type} ${className}`}
      style={{ width, animationDelay: `${index * 0.1}s` }}
    ></div>
  ));

  return <div className="skeleton-container">{skeletons}</div>;
};

// Enhanced Card Skeleton with stagger animation
export const CardSkeleton = ({ className = '', animated = true }) => {
  return (
    <div className={`card card-enhanced ${animated ? 'scale-in' : ''} ${className}`}>
      <div className="card-body">
        <div className="skeleton skeleton-title" style={{ width: '60%' }}></div>
        <div className="skeleton skeleton-text" style={{ width: '100%' }}></div>
        <div className="skeleton skeleton-text" style={{ width: '80%' }}></div>
        <div className="skeleton skeleton-text" style={{ width: '40%' }}></div>
        <div className="d-flex justify-content-between align-items-center mt-3">
          <div className="skeleton skeleton-button"></div>
          <div className="skeleton skeleton-avatar"></div>
        </div>
      </div>
    </div>
  );
};

// Enhanced Table Skeleton
export const TableSkeleton = ({ rows = 5, columns = 4, className = '', animated = true }) => {
  return (
    <div className={`table-responsive ${animated ? 'fade-in' : ''} ${className}`}>
      <table className="table table-enhanced">
        <thead>
          <tr>
            {Array.from({ length: columns }, (_, index) => (
              <th key={index}>
                <div 
                  className="skeleton skeleton-text" 
                  style={{ 
                    width: '80%',
                    animationDelay: `${index * 0.05}s`
                  }}
                ></div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }, (_, rowIndex) => (
            <tr key={rowIndex} className="skeleton-table-row">
              {Array.from({ length: columns }, (_, colIndex) => (
                <td key={colIndex}>
                  <div 
                    className="skeleton skeleton-text" 
                    style={{ 
                      width: `${Math.floor(Math.random() * 40) + 60}%`,
                      animationDelay: `${(rowIndex * columns + colIndex) * 0.02}s`
                    }}
                  ></div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Enhanced Stats Card Skeleton
export const StatsCardSkeleton = ({ className = '', animated = true }) => {
  return (
    <div className={`card card-stats hover-lift ${animated ? 'scale-in' : ''} ${className}`}>
      <div className="card-body text-center">
        <div className="skeleton skeleton-avatar mx-auto mb-3"></div>
        <div className="skeleton skeleton-title mx-auto mb-2" style={{ width: '60%' }}></div>
        <div className="skeleton skeleton-text-lg mx-auto mb-2" style={{ width: '40%' }}></div>
        <div className="skeleton skeleton-text mx-auto" style={{ width: '80%' }}></div>
      </div>
    </div>
  );
};

// Enhanced Data Loading State Component
export const DataLoadingState = ({ 
  type = 'spinner', 
  message = 'Loading data...', 
  className = '',
  animated = true,
  variant = 'primary'
}) => {
  if (type === 'skeleton') {
    return (
      <div className={`${animated ? 'stagger-container' : ''} ${className}`}>
        <div className="row g-4 mb-4">
          {Array.from({ length: 4 }, (_, index) => (
            <div key={index} className="col-6 col-lg-3 stagger-item">
              <StatsCardSkeleton animated={animated} />
            </div>
          ))}
        </div>
        <div className="stagger-item">
          <TableSkeleton animated={animated} />
        </div>
      </div>
    );
  }

  if (type === 'dots') {
    return <LoadingDots text={message} className={className} />;
  }

  if (type === 'page') {
    return (
      <div className={`page-loading ${className}`}>
        <div className="loading-spinner-lg" style={{ borderTopColor: `var(--theme-${variant})` }}></div>
        <div className="page-loading-text">{message}</div>
        <div className="page-loading-subtext">Please wait while we load your content...</div>
      </div>
    );
  }

  return <LoadingSpinner text={message} className={className} variant={variant} />;
};

// Enhanced Page Loading Component
export const PageLoadingState = ({ 
  message = 'Loading page...', 
  submessage = 'This won\'t take long',
  variant = 'primary',
  className = '' 
}) => {
  return (
    <div className={`page-loading ${className}`}>
      <div className="loading-spinner-lg" style={{ borderTopColor: `var(--theme-${variant})` }}></div>
      <div className="page-loading-text">{message}</div>
      <div className="page-loading-subtext">{submessage}</div>
    </div>
  );
};

// Content Loading Overlay
export const LoadingOverlay = ({ 
  visible = false, 
  message = 'Loading...', 
  dark = false,
  className = '' 
}) => {
  if (!visible) return null;

  return (
    <div className={`loading-overlay ${dark ? 'loading-overlay-dark' : ''} ${className}`}>
      <div className="text-center">
        <div className="loading-spinner mb-2"></div>
        <div className="small">{message}</div>
      </div>
    </div>
  );
};

// Progressive Loading Bar
export const LoadingBar = ({ 
  progress = 0, 
  indeterminate = false, 
  className = '',
  variant = 'primary' 
}) => {
  return (
    <div className={`loading-bar ${indeterminate ? 'loading-bar-indeterminate' : ''} ${className}`}>
      {!indeterminate && (
        <div 
          className="h-100 transition-all duration-300"
          style={{ 
            width: `${Math.min(Math.max(progress, 0), 100)}%`,
            background: `var(--theme-${variant})`
          }}
        ></div>
      )}
    </div>
  );
};
export default {
  LoadingSpinner,
  LoadingDots,
  LoadingButton,
  SkeletonLoader,
  CardSkeleton,
  TableSkeleton,
  StatsCardSkeleton,
  DataLoadingState,
  PageLoadingState,
  LoadingOverlay,
  LoadingBar,
  ErrorState,
  EmptyState,
  SuccessState
};
