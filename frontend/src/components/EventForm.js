import React, { useState, useEffect, useRef } from 'react';
import { getGoogleMapsApiKey } from '../config/constants';
import { Loader } from '@googlemaps/js-api-loader';
import { getApiUrl } from '../utils/apiUrl';

function EventForm({ onSubmit, initialData, onCancel }) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [type, setType] = useState(initialData?.event_type || initialData?.type || 'Rehearsal');
  const [description, setDescription] = useState(initialData?.description || '');
  
  // Handle date values for date-only input
  const getDateValue = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toISOString().slice(0, 10); // YYYY-MM-DD format
  };
  
  const [date, setDate] = useState(
    initialData?.date ? getDateValue(initialData.date) : ''
  );
  const [endDate, setEndDate] = useState(initialData?.end_date ? getDateValue(initialData.end_date) : '');
  const [location, setLocation] = useState(initialData?.location || '');
  const [locationAddress, setLocationAddress] = useState(initialData?.location_address || '');
  const [locationLat, setLocationLat] = useState(initialData?.lat || null);
  const [locationLng, setLocationLng] = useState(initialData?.lng || null);
  const [locationPlaceId, setLocationPlaceId] = useState(initialData?.location_place_id || '');
  
  // New fields for enhanced features
  const [categoryId, setCategoryId] = useState(initialData?.category_id || '');
  const [categories, setCategories] = useState([]);
  const [isRecurring, setIsRecurring] = useState(initialData?.is_recurring || false);
  const [recurringPattern, setRecurringPattern] = useState(initialData?.recurring_pattern || 'weekly');
  const [recurringInterval, setRecurringInterval] = useState(initialData?.recurring_interval || 1);
  const [recurringEndDate, setRecurringEndDate] = useState(initialData?.recurring_end_date ? initialData.recurring_end_date.slice(0, 10) : '');
  const [isTemplate, setIsTemplate] = useState(initialData?.is_template || false);
  const [templateName, setTemplateName] = useState(initialData?.template_name || '');
  const [sendReminders, setSendReminders] = useState(initialData?.send_reminders !== undefined ? initialData.send_reminders : true);
  const [reminderDaysBefore, setReminderDaysBefore] = useState(initialData?.reminder_days_before || 1);
  const [sendNotification, setSendNotification] = useState(initialData?.send_notification !== undefined ? initialData.send_notification : true);
  
  // Time fields
  const [arriveByTime, setArriveByTime] = useState(initialData?.arrive_by_time || '');
  const [startTime, setStartTime] = useState(initialData?.start_time || '');
  const [endTime, setEndTime] = useState(initialData?.end_time || '');
  
  // Multiple dates feature
  const [hasMultipleDates, setHasMultipleDates] = useState(initialData?.has_multiple_dates || false);
  const [dateSelectionDeadline, setDateSelectionDeadline] = useState(initialData?.date_selection_deadline || '');
  const [possibleDates, setPossibleDates] = useState(initialData?.possible_dates || []);
  
  const mapRef = useRef(null);
  const autocompleteRef = useRef(null);
  const markerRef = useRef(null);
  const mapInstance = useRef(null);

  const eventTypes = [
    'Rehearsal',
    'Concert',
    'Committee Meeting',
    'AGM'
  ];

  // Update form fields when initialData changes (e.g., when switching from create to edit)
  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || '');
      setType(initialData.event_type || initialData.type || 'Rehearsal');
      setDescription(initialData.description || '');
      setDate(initialData.date ? getDateValue(initialData.date) : '');
      setEndDate(initialData.end_date ? getDateValue(initialData.end_date) : '');
      setLocation(initialData.location || '');
      setLocationAddress(initialData.location_address || '');
      setLocationLat(initialData.lat || null);
      setLocationLng(initialData.lng || null);
      setLocationPlaceId(initialData.location_place_id || '');
      setCategoryId(initialData.category_id || '');
      setIsRecurring(initialData.is_recurring || false);
      setRecurringPattern(initialData.recurring_pattern || 'weekly');
      setRecurringInterval(initialData.recurring_interval || 1);
      setRecurringEndDate(initialData.recurring_end_date ? initialData.recurring_end_date.slice(0, 10) : '');
      setIsTemplate(initialData.is_template || false);
      setTemplateName(initialData.template_name || '');
      setSendReminders(initialData.send_reminders !== undefined ? initialData.send_reminders : true);
      setReminderDaysBefore(initialData.reminder_days_before || 1);
      setSendNotification(initialData.send_notification !== undefined ? initialData.send_notification : true);
      setArriveByTime(initialData.arrive_by_time || '');
      setStartTime(initialData.start_time || '');
      setEndTime(initialData.end_time || '');
    }
  }, [initialData]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const token = localStorage.getItem('token');
        console.log('Fetching categories...', { token: token ? 'present' : 'missing' });
        
        const response = await fetch(`${getApiUrl()}/events/categories`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log('Categories response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Categories data received:', data);
          setCategories(data);
        } else {
          console.error('Failed to fetch categories:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    const initializeGoogleMaps = async () => {
      if (window.google && window.google.maps) {
        console.log('Google Maps already loaded, initializing map...');
        initializeMap();
        return;
      }
      
      try {
        console.log('Loading Google Maps with API key:', googleMapsApiKey ? 'Key present' : 'No key');
        const loader = new Loader({
          apiKey: googleMapsApiKey,
          version: "weekly",
          libraries: ["places"]
        });

        await loader.load();
        console.log('Google Maps script loaded successfully, initializing map...');
        
        // Add a small delay to ensure DOM is ready
        setTimeout(() => {
          initializeMap();
        }, 100);
      } catch (error) {
        console.error('Error loading Google Maps:', error);
        console.error('API Key used:', googleMapsApiKey);
        // Show a user-friendly message
        if (error.message.includes('InvalidKeyMapError')) {
          console.error('Google Maps API key is invalid or has restrictions');
        } else if (error.message.includes('RefererNotAllowedMapError')) {
          console.error('Domain not allowed for this Google Maps API key');
        }
      }
    };

    const initializeMap = () => {
      if (!window.google || !window.google.maps || !mapRef.current) {
        console.error('Google Maps not loaded or map ref not available');
        return;
      }

      try {
        console.log('Initializing Google Maps...');
        
        // Initialize map
        const map = new window.google.maps.Map(mapRef.current, {
          center: { lat: 51.5074, lng: -0.1278 }, // Default to London
          zoom: 13,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: false,
        });
        
        mapInstance.current = map;

        // Initialize autocomplete if input exists
        if (autocompleteRef.current) {
          const autocomplete = new window.google.maps.places.Autocomplete(
            autocompleteRef.current,
            {
              types: ['establishment', 'geocode'],
              fields: ['place_id', 'formatted_address', 'geometry', 'name']
            }
          );

          autocomplete.addListener('place_changed', () => {
            const place = autocomplete.getPlace();
            if (place.geometry) {
              const lat = place.geometry.location.lat();
              const lng = place.geometry.location.lng();
              
              setLocationAddress(place.formatted_address || '');
              setLocationLat(lat);
              setLocationLng(lng);
              setLocation(place.name || place.formatted_address || '');
              updateMapLocation(lat, lng);
            }
          });
        }

        // Add click listener to map
        map.addListener('click', (event) => {
          const lat = event.latLng.lat();
          const lng = event.latLng.lng();
          setLocationLat(lat);
          setLocationLng(lng);
          updateMapLocation(lat, lng);
        });

        console.log('Google Maps initialized successfully');
      } catch (error) {
        console.error('Error initializing Google Maps:', error);
      }
    };

    fetchCategories();
    if (googleMapsApiKey && googleMapsApiKey !== 'YOUR_GOOGLE_MAPS_API_KEY_HERE') {
      initializeGoogleMaps().catch(console.error);
    }
  }, []);

  useEffect(() => {
    if (mapInstance.current && locationLat && locationLng) {
      updateMapLocation(locationLat, locationLng);
    }
  }, [locationLat, locationLng]);

  const updateMapLocation = (lat, lng) => {
    if (!mapInstance.current || !window.google) return;

    const position = { lat, lng };
    
    // Clear existing marker
    if (markerRef.current) {
      markerRef.current.setMap(null);
    }
    
    // Create new marker
    markerRef.current = new window.google.maps.Marker({
      position: position,
      map: mapInstance.current,
      draggable: true,
      title: 'Event Location'
    });
    
    // Add drag listener to marker
    markerRef.current.addListener('dragend', (event) => {
      const newLat = event.latLng.lat();
      const newLng = event.latLng.lng();
      
      setLocationLat(newLat);
      setLocationLng(newLng);
      
      // Reverse geocode the new position
      const geocoder = new window.google.maps.Geocoder();
      geocoder.geocode(
        { location: { lat: newLat, lng: newLng } },
        (results, status) => {
          if (status === 'OK' && results[0]) {
            setLocationAddress(results[0].formatted_address);
          }
        }
      );
    });
    
    // Center map on the location
    mapInstance.current.setCenter(position);
    mapInstance.current.setZoom(15);
  };

  // Multiple dates functions
  const addPossibleDate = () => {
    setPossibleDates(prev => [...prev, {
      date: '',
      end_date: '',
      arrive_by_time: '',
      start_time: '',
      end_time: ''
    }]);
  };

  const removePossibleDate = (index) => {
    setPossibleDates(prev => prev.filter((_, i) => i !== index));
  };

  const updatePossibleDate = (index, field, value) => {
    setPossibleDates(prev => 
      prev.map((dateOption, i) => 
        i === index ? { ...dateOption, [field]: value } : dateOption
      )
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Filter out incomplete possible dates (those without a date)
    const validPossibleDates = hasMultipleDates ? 
      possibleDates.filter(pdate => pdate.date && pdate.date !== '') : [];
    
    const eventData = { 
      title, 
      type,
      description, 
      date,
      end_date: endDate || null,
      location,
      location_address: locationAddress,
      lat: locationLat,
      lng: locationLng,
      location_place_id: locationPlaceId,
      category_id: categoryId || null,
      is_recurring: isRecurring,
      recurring_pattern: isRecurring ? recurringPattern : null,
      recurring_interval: isRecurring ? recurringInterval : null,
      recurring_end_date: isRecurring && recurringEndDate ? recurringEndDate : null,
      is_template: isTemplate,
      template_name: isTemplate ? templateName : null,
      send_reminders: sendReminders,
      reminder_days_before: reminderDaysBefore,
      send_notification: sendNotification,
      arrive_by_time: arriveByTime || null,
      start_time: startTime || null,
      end_time: endTime || null,
      // Multiple dates support
      has_multiple_dates: hasMultipleDates,
      date_selection_deadline: hasMultipleDates ? dateSelectionDeadline : null,
      possible_dates: validPossibleDates
    };
    
    console.log('Submitting event data:', eventData);
    console.log('Valid possible dates:', validPossibleDates);
    
    onSubmit(eventData);
  };

  // Direct hardcoded values as final fallback
  const HARDCODED_API_KEY = 'AIzaSyC11N3v1N5Gl14LJ2Cl9TjasJNzE5wVkEc';
  
  const hasGoogleMaps = (process.env.REACT_APP_GOOGLE_MAPS_API_KEY || getGoogleMapsApiKey() || HARDCODED_API_KEY) && 
                       (process.env.REACT_APP_GOOGLE_MAPS_API_KEY || getGoogleMapsApiKey() || HARDCODED_API_KEY) !== 'YOUR_GOOGLE_MAPS_API_KEY_HERE';
  
  // Get the API key from environment, fallback, or hardcoded
  const googleMapsApiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || getGoogleMapsApiKey() || HARDCODED_API_KEY;
  
  // Debug logging
  console.log('Google Maps API Key Check:', {
    envKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY ? 'Present' : 'Missing',
    fallbackKey: getGoogleMapsApiKey() ? 'Present' : 'Missing',
    hardcodedKey: HARDCODED_API_KEY ? 'Present' : 'Missing',
    finalKey: googleMapsApiKey ? 'Present' : 'Missing',
    hasGoogleMaps
  });

  return (
    <div className="card">
      <div className="card-body">
        <h5 className="card-title">
          <i className="bi bi-calendar-plus me-2"></i>
          {initialData ? 'Edit Event' : 'Create New Event'}
        </h5>
        
        <form onSubmit={handleSubmit}>
          <div className="row">
            <div className="col-md-8">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-type me-1"></i>
                  Event Title *
                </label>
                <input 
                  className="form-control" 
                  value={title} 
                  onChange={e => setTitle(e.target.value)} 
                  required 
                  placeholder="Enter event title"
                />
              </div>
            </div>
            
            <div className="col-md-4">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-tag me-1"></i>
                  Event Type *
                </label>
                <select 
                  className="form-select" 
                  value={type} 
                  onChange={e => setType(e.target.value)}
                  required
                >
                  {eventTypes.map(eventType => (
                    <option key={eventType} value={eventType}>{eventType}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="row">
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-bookmark me-1"></i>
                  Category
                </label>
                <select 
                  className="form-select" 
                  value={categoryId} 
                  onChange={e => setCategoryId(e.target.value)}
                >
                  <option value="">Select a category</option>
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-bell me-1"></i>
                  Reminder Settings
                </label>
                <div className="d-flex align-items-center gap-2">
                  <div className="form-check">
                    <input 
                      className="form-check-input" 
                      type="checkbox" 
                      id="sendReminders"
                      checked={sendReminders}
                      onChange={e => setSendReminders(e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor="sendReminders">
                      Send reminders
                    </label>
                  </div>
                  {sendReminders && (
                    <div className="d-flex align-items-center">
                      <input 
                        type="number" 
                        className="form-control form-control-sm" 
                        style={{ width: '60px' }}
                        value={reminderDaysBefore}
                        onChange={e => setReminderDaysBefore(parseInt(e.target.value) || 1)}
                        min="1"
                        max="30"
                      />
                      <span className="ms-1 small">days before</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Email Notification Section */}
          <div className="mb-3">
            <div className="form-check">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="sendNotification"
                checked={sendNotification}
                onChange={e => setSendNotification(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="sendNotification">
                <i className="bi bi-envelope me-1"></i>
                Send email notification to all members when event is created
              </label>
            </div>
            <small className="text-muted">
              This will send an email to all organization members asking them to RSVP to the new event.
            </small>
          </div>

          <div className="mb-3">
            <label className="form-label">
              <i className="bi bi-text-paragraph me-1"></i>
              Description / Information
            </label>
            <textarea 
              className="form-control" 
              rows="3"
              value={description} 
              onChange={e => setDescription(e.target.value)} 
              placeholder="Add event details, instructions, or other information..."
            />
          </div>

          <div className="row">
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-calendar-event me-1"></i>
                  Start Date *
                </label>
                <div className="d-flex align-items-center gap-2">
                  <input 
                    type="date" 
                    className="form-control" 
                    value={date} 
                    onChange={e => setDate(e.target.value)} 
                    required 
                  />
                  <button
                    type="button"
                    className="btn btn-outline-primary btn-sm"
                    onClick={() => {
                      setHasMultipleDates(true);
                      if (possibleDates.length === 0 && date) {
                        addPossibleDate();
                      }
                    }}
                    title="Add multiple date options for voting"
                  >
                    <i className="bi bi-plus-circle me-1"></i>
                    Multiple Dates
                  </button>
                </div>
                {!hasMultipleDates && (
                  <small className="text-muted">
                    Click "Multiple Dates" to create a poll with date options for members to vote on
                  </small>
                )}
              </div>
            </div>
            
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-calendar-check me-1"></i>
                  End Date
                </label>
                <input 
                  type="date" 
                  className="form-control" 
                  value={endDate} 
                  onChange={e => setEndDate(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Multiple Dates Section */}
          {hasMultipleDates && (
            <div className="border rounded p-3 mb-3 bg-light">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h6 className="mb-0">
                  <i className="bi bi-calendar-plus me-2"></i>
                  Multiple Date Options
                </h6>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => {
                    setHasMultipleDates(false);
                    setPossibleDates([]);
                    setDateSelectionDeadline('');
                  }}
                >
                  <i className="bi bi-x-circle me-1"></i>
                  Remove Multiple Dates
                </button>
              </div>
              
              <div className="alert alert-info">
                <i className="bi bi-info-circle me-2"></i>
                <strong>Multiple Date Poll:</strong> Members will be able to vote on their preferred dates. You can select the final date after collecting votes.
              </div>

              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-clock me-1"></i>
                  Voting Deadline
                </label>
                <input 
                  type="datetime-local" 
                  className="form-control" 
                  value={dateSelectionDeadline} 
                  onChange={e => setDateSelectionDeadline(e.target.value)}
                />
                <small className="text-muted">When should voting close?</small>
              </div>

              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <label className="form-label mb-0">Date Options</label>
                  <button
                    type="button"
                    className="btn btn-sm btn-success"
                    onClick={addPossibleDate}
                  >
                    <i className="bi bi-plus-circle me-1"></i>
                    Add Date Option
                  </button>
                </div>
                
                {possibleDates.map((dateOption, index) => (
                  <div key={index} className="border rounded p-3 mb-2 bg-white">
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <h6 className="mb-0">Option {index + 1}</h6>
                      {possibleDates.length > 1 && (
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => removePossibleDate(index)}
                        >
                          <i className="bi bi-trash"></i>
                        </button>
                      )}
                    </div>
                    
                    <div className="row">
                      <div className="col-md-6">
                        <div className="mb-2">
                          <label className="form-label form-label-sm">Start Date</label>
                          <input 
                            type="date" 
                            className="form-control form-control-sm" 
                            value={dateOption.date} 
                            onChange={e => updatePossibleDate(index, 'date', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="mb-2">
                          <label className="form-label form-label-sm">End Date</label>
                          <input 
                            type="date" 
                            className="form-control form-control-sm" 
                            value={dateOption.end_date} 
                            onChange={e => updatePossibleDate(index, 'end_date', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div className="row">
                      <div className="col-md-4">
                        <div className="mb-2">
                          <label className="form-label form-label-sm">Arrive By</label>
                          <input 
                            type="time" 
                            className="form-control form-control-sm" 
                            value={dateOption.arrive_by_time} 
                            onChange={e => updatePossibleDate(index, 'arrive_by_time', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="mb-2">
                          <label className="form-label form-label-sm">Start Time</label>
                          <input 
                            type="time" 
                            className="form-control form-control-sm" 
                            value={dateOption.start_time} 
                            onChange={e => updatePossibleDate(index, 'start_time', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="mb-2">
                          <label className="form-label form-label-sm">End Time</label>
                          <input 
                            type="time" 
                            className="form-control form-control-sm" 
                            value={dateOption.end_time} 
                            onChange={e => updatePossibleDate(index, 'end_time', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {possibleDates.length === 0 && (
                  <div className="text-center text-muted py-3">
                    <i className="bi bi-calendar-plus display-6"></i>
                    <p className="mb-1">No date options added yet</p>
                    <p className="small">Click "Add Date Option" to start creating your poll</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Time Fields Section */}
          <div className="row">
            <div className="col-md-4">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-clock me-1"></i>
                  Arrive By Time
                </label>
                <input 
                  type="time" 
                  className="form-control" 
                  value={arriveByTime} 
                  onChange={e => setArriveByTime(e.target.value)}
                />
                <small className="text-muted">When participants need to arrive</small>
              </div>
            </div>
            
            <div className="col-md-4">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-play-circle me-1"></i>
                  Start Time
                </label>
                <input 
                  type="time" 
                  className="form-control" 
                  value={startTime} 
                  onChange={e => setStartTime(e.target.value)}
                />
                <small className="text-muted">When the event actually starts</small>
              </div>
            </div>
            
            <div className="col-md-4">
              <div className="mb-3">
                <label className="form-label">
                  <i className="bi bi-stop-circle me-1"></i>
                  End Time
                </label>
                <input 
                  type="time" 
                  className="form-control" 
                  value={endTime} 
                  onChange={e => setEndTime(e.target.value)}
                />
                <small className="text-muted">When the event ends</small>
              </div>
            </div>
          </div>

          {/* Recurring Events Section */}
          <div className="mb-3">
            <div className="form-check">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="isRecurring"
                checked={isRecurring}
                onChange={e => setIsRecurring(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="isRecurring">
                <i className="bi bi-arrow-repeat me-1"></i>
                Make this a recurring event
              </label>
            </div>
          </div>

          {isRecurring && (
            <div className="border rounded p-3 mb-3 bg-light">
              <h6 className="mb-3">Recurring Event Settings</h6>
              <div className="row">
                <div className="col-md-4">
                  <div className="mb-3">
                    <label className="form-label">Pattern</label>
                    <select 
                      className="form-select" 
                      value={recurringPattern} 
                      onChange={e => setRecurringPattern(e.target.value)}
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="yearly">Yearly</option>
                    </select>
                  </div>
                </div>
                
                <div className="col-md-4">
                  <div className="mb-3">
                    <label className="form-label">Every</label>
                    <div className="d-flex align-items-center">
                      <input 
                        type="number" 
                        className="form-control" 
                        value={recurringInterval}
                        onChange={e => setRecurringInterval(parseInt(e.target.value) || 1)}
                        min="1"
                        max="52"
                      />
                      <span className="ms-2">
                        {recurringPattern === 'daily' && 'day(s)'}
                        {recurringPattern === 'weekly' && 'week(s)'}
                        {recurringPattern === 'monthly' && 'month(s)'}
                        {recurringPattern === 'yearly' && 'year(s)'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="col-md-4">
                  <div className="mb-3">
                    <label className="form-label">Until (optional)</label>
                    <input 
                      type="date" 
                      className="form-control" 
                      value={recurringEndDate}
                      onChange={e => setRecurringEndDate(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Template Section */}
          <div className="mb-3">
            <div className="form-check">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="isTemplate"
                checked={isTemplate}
                onChange={e => setIsTemplate(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="isTemplate">
                <i className="bi bi-file-earmark-text me-1"></i>
                Save as template for future events
              </label>
            </div>
          </div>

          {isTemplate && (
            <div className="mb-3">
              <label className="form-label">Template Name</label>
              <input 
                className="form-control" 
                value={templateName} 
                onChange={e => setTemplateName(e.target.value)} 
                placeholder="Enter a name for this template"
                required={isTemplate}
              />
            </div>
          )}

          <div className="mb-3">
            <label className="form-label">
              <i className="bi bi-geo-alt me-1"></i>
              Location
            </label>
            <input 
              ref={autocompleteRef}
              className="form-control mb-2" 
              value={location} 
              onChange={e => setLocation(e.target.value)} 
              placeholder="Search for a location or enter manually..."
            />
            {locationAddress && (
              <small className="text-muted">
                <i className="bi bi-info-circle me-1"></i>
                Address: {locationAddress}
              </small>
            )}
          </div>

          {hasGoogleMaps ? (
            <div className="mb-3">
              <label className="form-label">
                <i className="bi bi-map me-1"></i>
                Location on Map
                <small className="text-muted ms-2">(Click to set location, drag pin to adjust)</small>
              </label>
              <div 
                ref={mapRef} 
                style={{ height: '300px', width: '100%' }}
                className="border rounded"
              ></div>
              {locationLat && locationLng && (
                <small className="text-muted d-block mt-1">
                  <i className="bi bi-crosshair me-1"></i>
                  Coordinates: {locationLat.toFixed(6)}, {locationLng.toFixed(6)}
                </small>
              )}
            </div>
          ) : (
            <div className="mb-3">
              <label className="form-label">
                <i className="bi bi-building me-1"></i>
                Full Address (Optional)
              </label>
              <textarea
                className="form-control"
                rows="2"
                value={locationAddress}
                onChange={e => setLocationAddress(e.target.value)}
                placeholder="Enter full address for better directions..."
              />
              <small className="text-muted">
                <i className="bi bi-info-circle me-1"></i>
                Add Google Maps API key to enable location search and mapping features.
              </small>
            </div>
          )}

          <div className="d-flex gap-2">
            <button className="btn btn-primary" type="submit">
              <i className="bi bi-check-lg me-1"></i>
              {initialData ? 'Update Event' : 'Create Event'}
            </button>
            {onCancel && (
              <button className="btn btn-outline-secondary" type="button" onClick={onCancel}>
                <i className="bi bi-x-lg me-1"></i>
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

export default EventForm;
