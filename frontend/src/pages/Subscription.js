/**
 * Subscription Page
 * Main page for subscription management and billing
 */

import React from 'react';
import SubscriptionManager from '../components/SubscriptionManager';

const SubscriptionPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <SubscriptionManager />
    </div>
  );
};

export default SubscriptionPage;
