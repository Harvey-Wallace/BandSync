import React from 'react';

const Spinner = ({ size = 40 }) => (
  <div className="d-flex justify-content-center align-items-center" style={{ minHeight: size }}>
    <div className="spinner-border text-primary" style={{ width: size, height: size }} role="status">
      <span className="visually-hidden">Loading...</span>
    </div>
  </div>
);

export default Spinner;
