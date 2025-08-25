import React from 'react';

// Mobile-responsive table wrapper
export const ResponsiveTable = ({ children, className = '' }) => {
  // Filter children to only allow valid React elements, strings, or numbers
  const validChildren = React.Children.toArray(children).filter(child =>
    React.isValidElement(child) || typeof child === 'string' || typeof child === 'number'
  );
  
  return (
    <div className={`table-responsive table-responsive-mobile ${className}`}>
      <div className="table-enhanced">
        {validChildren}
      </div>
    </div>
  );
};

// Mobile-responsive card grid
export const ResponsiveCardGrid = ({ children, className = '' }) => {
  return (
    <div className={`row ${className}`}>
      {React.Children.map(children, (child, index) => {
        // Only render valid React elements, strings, or numbers
        if (React.isValidElement(child) || typeof child === 'string' || typeof child === 'number') {
          return (
            <div key={index} className="col-12 col-md-6 col-lg-4 mb-3">
              {child}
            </div>
          );
        }
        // Skip invalid children (objects, null, undefined, etc.)
        return null;
      })}
    </div>
  );
};

// Mobile-responsive stats grid
export const ResponsiveStatsGrid = ({ stats = [], className = '' }) => {
  return (
    <div className={`row g-4 ${className}`}>
      {stats.filter(stat => 
        stat && typeof stat === 'object' && stat.label
      ).map((stat, index) => (
        <div key={index} className="col-6 col-lg-3 stagger-item">
          <div className="card card-stats hover-lift">
            <div className="card-body text-center">
              {stat.icon && (
                <div className="stats-icon">
                  <i className={`bi bi-${stat.icon}`}></i>
                </div>
              )}
              <h4 className="mb-2">
                {typeof stat.value === 'string' || typeof stat.value === 'number' ? 
                  stat.value : 
                  JSON.stringify(stat.value)
                }
              </h4>
              <h6 className="text-muted mb-1">
                {typeof stat.label === 'string' ? stat.label : JSON.stringify(stat.label)}
              </h6>
              {stat.subtitle && (
                <div className="stats-subtitle">
                  {typeof stat.subtitle === 'string' ? stat.subtitle : JSON.stringify(stat.subtitle)}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Mobile-responsive navigation tabs
export const ResponsiveTabNav = ({ tabs = [], activeTab, onTabChange, className = '' }) => {
  return (
    <ul className={`nav nav-tabs nav-tabs-enhanced ${className}`}>
      {tabs.filter(tab => 
        tab && typeof tab === 'object' && (tab.label || tab.shortLabel)
      ).map((tab) => (
        <li key={tab.id} className="nav-item">
          <button
            className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.icon && <i className={`bi bi-${tab.icon} me-1`}></i>}
            <span className="d-none d-sm-inline">
              {typeof tab.label === 'string' ? tab.label : JSON.stringify(tab.label)}
            </span>
            <span className="d-sm-none">
              {typeof (tab.shortLabel || tab.label) === 'string' ? 
                (tab.shortLabel || tab.label) : 
                JSON.stringify(tab.shortLabel || tab.label)
              }
            </span>
            {tab.badge && tab.badge.value !== null && tab.badge.value !== undefined && (
              <span className={`badge bg-${tab.badge.type || 'primary'} ms-2`}>
                {typeof tab.badge.value === 'string' || typeof tab.badge.value === 'number' ? 
                  tab.badge.value : 
                  JSON.stringify(tab.badge.value)
                }
              </span>
            )}
          </button>
        </li>
      ))}
    </ul>
  );
};

// Mobile-optimized form group
export const ResponsiveFormGroup = ({ 
  label, 
  children, 
  error = null, 
  required = false,
  className = '' 
}) => {
  // Only proceed if children is a valid React element
  if (!React.isValidElement(children)) {
    console.warn('ResponsiveFormGroup: Invalid children provided. Expected a React element.');
    return null;
  }

  return (
    <div className={`mb-3 ${className}`}>
      <label className="form-label">
        {label}
        {required && <span className="text-danger ms-1">*</span>}
      </label>
      <div className="form-control-wrapper">
        {React.cloneElement(children, {
          className: `${children.props.className || ''} form-control-enhanced form-control-mobile`.trim()
        })}
      </div>
      {error && (
        <div className="form-text text-danger">
          <i className="bi bi-exclamation-triangle me-1"></i>
          {error}
        </div>
      )}
    </div>
  );
};

// Mobile-responsive action bar
export const ResponsiveActionBar = ({ 
  title, 
  subtitle = null,
  icon = null,
  actions = [], 
  searchValue = '', 
  onSearchChange = null,
  className = '' 
}) => {
  return (
    <div className={`d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 ${className}`}>
      <div className="mb-2 mb-md-0">
        <h4 className="mb-0">
          {icon && <i className={`bi bi-${icon} me-2`}></i>}
          {title}
        </h4>
        {subtitle && (
          <p className="text-muted mb-0 mt-1">{subtitle}</p>
        )}
      </div>
      
      <div className="d-flex flex-column flex-md-row gap-2 w-100 w-md-auto">
        {onSearchChange && (
          <div className="flex-grow-1 flex-md-grow-0">
            <div className="input-group">
              <span className="input-group-text">
                <i className="bi bi-search"></i>
              </span>
              <input
                type="text"
                className="form-control form-control-enhanced"
                placeholder="Search..."
                value={searchValue}
                onChange={(e) => onSearchChange(e.target.value)}
              />
            </div>
          </div>
        )}
        
        {actions.length > 0 && (
          <div className="btn-group-mobile">
            {actions.filter(action => 
              action && typeof action === 'object' && action.label
            ).map((action, index) => (
              <button
                key={`action-${index}-${action.label}`}
                className={`btn ${action.variant || 'btn-primary'} btn-enhanced`}
                onClick={action.onClick}
                disabled={action.disabled}
              >
                {action.icon && <i className={`bi bi-${action.icon} me-1`}></i>}
                <span className="d-none d-sm-inline">{typeof action.label === 'string' ? action.label : JSON.stringify(action.label)}</span>
                <span className="d-sm-none">{typeof (action.shortLabel || action.label) === 'string' ? (action.shortLabel || action.label) : JSON.stringify(action.shortLabel || action.label)}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Mobile-responsive data table with enhanced features
export const ResponsiveDataTable = ({ 
  headers = [], 
  data = [], 
  loading = false,
  error = null,
  emptyMessage = 'No data available',
  onRowClick = null,
  className = '' 
}) => {
  if (loading) {
    return (
      <div className="table-responsive">
        <table className="table table-enhanced">
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={index}>
                  <div className="skeleton skeleton-text" style={{ width: '80%' }}></div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 5 }, (_, rowIndex) => (
              <tr key={rowIndex}>
                {headers.map((_, colIndex) => (
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
  }

  if (error) {
    return (
      <div className="alert alert-danger">
        <i className="bi bi-exclamation-triangle me-2"></i>
        {error}
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-5">
        <i className="bi bi-inbox" style={{ fontSize: '3rem', color: '#6c757d' }}></i>
        <h5 className="text-muted mt-3">{emptyMessage}</h5>
      </div>
    );
  }

  return (
    <div className={`table-responsive table-responsive-mobile ${className}`}>
      <table className="table table-enhanced">
        <thead>
          <tr>
            {headers.map((header, index) => (
              <th key={index} className={header.className || ''}>
                {header.label}
                {header.sortable && (
                  <i className="bi bi-arrow-down-up ms-1" style={{ fontSize: '0.8rem' }}></i>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr 
              key={index} 
              className={onRowClick ? 'cursor-pointer' : ''}
              onClick={() => onRowClick && onRowClick(row, index)}
            >
              {headers.map((header, colIndex) => (
                <td key={colIndex} className={header.className || ''}>
                  {header.render ? 
                    header.render(row[header.key], row, index) : 
                    (typeof row[header.key] === 'string' || typeof row[header.key] === 'number' || row[header.key] === null || row[header.key] === undefined ? 
                      row[header.key] : 
                      JSON.stringify(row[header.key])
                    )
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Mobile-responsive pagination
export const ResponsivePagination = ({ 
  currentPage = 1, 
  totalPages = 1, 
  onPageChange, 
  className = '' 
}) => {
  const maxVisiblePages = 5;
  const startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
  
  const pages = Array.from(
    { length: endPage - startPage + 1 }, 
    (_, index) => startPage + index
  );

  return (
    <nav className={`d-flex justify-content-center ${className}`}>
      <ul className="pagination pagination-sm">
        <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
          <button 
            className="page-link"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            <i className="bi bi-chevron-left"></i>
          </button>
        </li>
        
        {pages.map(page => (
          <li key={page} className={`page-item ${currentPage === page ? 'active' : ''}`}>
            <button 
              className="page-link"
              onClick={() => onPageChange(page)}
            >
              {page}
            </button>
          </li>
        ))}
        
        <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
          <button 
            className="page-link"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            <i className="bi bi-chevron-right"></i>
          </button>
        </li>
      </ul>
    </nav>
  );
};

// Export all components  
const ResponsiveComponentsExports = {
  ResponsiveTable,
  ResponsiveCardGrid,
  ResponsiveStatsGrid,
  ResponsiveTabNav,
  ResponsiveFormGroup,
  ResponsiveActionBar,
  ResponsiveDataTable,
  ResponsivePagination
};

export default ResponsiveComponentsExports;
