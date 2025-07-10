import React from 'react';

const Toast = ({ show, message, type = 'success', onClose }) => {
  if (!show) return null;
  return (
    <div className={`toast align-items-center text-bg-${type} show position-fixed bottom-0 end-0 m-3`} role="alert" aria-live="assertive" aria-atomic="true" style={{zIndex: 9999, minWidth: 250}}>
      <div className="d-flex">
        <div className="toast-body">{message}</div>
        <button type="button" className="btn-close btn-close-white me-2 m-auto" aria-label="Close" onClick={onClose}></button>
      </div>
    </div>
  );
};

export default Toast;
