/**
 * Event Time Utilities
 * Helper functions for determining if events are past, current, or upcoming
 * based on both date and start_time fields
 */

/**
 * Check if an event is past (started)
 * @param {Object|string} event - Event object with date and start_time, or dateTime string
 * @returns {boolean} - True if event has started
 */
export const isEventPast = (event) => {
  // Handle different input formats for backwards compatibility
  if (typeof event === 'string') {
    // Old format: just dateTime string
    if (!event) return false;
    const eventDate = new Date(event);
    const now = new Date();
    return eventDate < now;
  }
  
  // New format: event object with date and start_time
  if (!event || !event.date) return false; // TBD events are not past
  
  // If event has dateTime field that includes time, use it
  if (event.dateTime) {
    const eventDate = new Date(event.dateTime);
    const now = new Date();
    return eventDate < now;
  }
  
  // Otherwise combine date and start_time
  const eventDate = new Date(event.date);
  if (isNaN(eventDate.getTime())) return false;
  
  // If no start_time, just compare dates (current behavior)
  if (!event.start_time) {
    const now = new Date();
    // Set both dates to midnight for date-only comparison
    eventDate.setHours(23, 59, 59, 999); // End of event day
    return eventDate < now;
  }
  
  // Combine date and start_time for accurate comparison
  const [hours, minutes] = event.start_time.split(':').map(Number);
  if (isNaN(hours) || isNaN(minutes)) {
    // Invalid time format, fall back to date comparison
    const now = new Date();
    eventDate.setHours(23, 59, 59, 999);
    return eventDate < now;
  }
  
  eventDate.setHours(hours, minutes, 0, 0);
  const now = new Date();
  return eventDate < now;
};

/**
 * Check if an event is upcoming (not started yet)
 * @param {Object|string} event - Event object with date and start_time, or dateTime string  
 * @returns {boolean} - True if event hasn't started yet
 */
export const isEventUpcoming = (event) => {
  return !isEventPast(event);
};

/**
 * Get the actual start datetime of an event
 * @param {Object} event - Event object with date and start_time
 * @returns {Date|null} - Combined date and time, or null if invalid
 */
export const getEventStartDateTime = (event) => {
  if (!event || !event.date) return null;
  
  // If event has dateTime field, use it
  if (event.dateTime) {
    return new Date(event.dateTime);
  }
  
  const eventDate = new Date(event.date);
  if (isNaN(eventDate.getTime())) return null;
  
  // If no start_time, return date at start of day
  if (!event.start_time) {
    eventDate.setHours(0, 0, 0, 0);
    return eventDate;
  }
  
  // Combine date and start_time
  const [hours, minutes] = event.start_time.split(':').map(Number);
  if (isNaN(hours) || isNaN(minutes)) {
    // Invalid time format, return date at start of day
    eventDate.setHours(0, 0, 0, 0);
    return eventDate;
  }
  
  eventDate.setHours(hours, minutes, 0, 0);
  return eventDate;
};
