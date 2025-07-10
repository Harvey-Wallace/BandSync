import React, { useState, useEffect, useRef } from 'react';
import { Loader } from '@googlemaps/js-api-loader';

function EventForm({ onSubmit, initialData, onCancel }) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [type, setType] = useState(initialData?.type || 'Rehearsal');
  const [description, setDescription] = useState(initialData?.description || '');
  const [date, setDate] = useState(initialData?.date ? initialData.date.slice(0, 16) : '');
  const [location, setLocation] = useState(initialData?.location || '');
  const [locationAddress, setLocationAddress] = useState(initialData?.location_address || '');
  const [locationLat, setLocationLat] = useState(initialData?.location_lat || null);
  const [locationLng, setLocationLng] = useState(initialData?.location_lng || null);
  const [locationPlaceId, setLocationPlaceId] = useState(initialData?.location_place_id || '');
  
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

  useEffect(() => {
    initializeGoogleMaps();
  }, []);

  useEffect(() => {
    if (mapInstance.current && locationLat && locationLng) {
      updateMapLocation(locationLat, locationLng);
    }
  }, [locationLat, locationLng]);

  const initializeGoogleMaps = async () => {
    try {
      const loader = new Loader({
        apiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY || 'YOUR_GOOGLE_MAPS_API_KEY',
        version: 'weekly',
        libraries: ['places']
      });

      const google = await loader.load();
      
      // Initialize map
      const map = new google.maps.Map(mapRef.current, {
        center: { lat: 51.5074, lng: -0.1278 }, // Default to London
        zoom: 13,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
      });
      
      mapInstance.current = map;

      // Initialize autocomplete
      const autocomplete = new google.maps.places.Autocomplete(
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
          setLocationPlaceId(place.place_id || '');
          setLocation(place.name || place.formatted_address || '');
          
          updateMapLocation(lat, lng);
        }
      });

      // Add click listener to map for manual pin placement
      map.addListener('click', (event) => {
        const lat = event.latLng.lat();
        const lng = event.latLng.lng();
        
        setLocationLat(lat);
        setLocationLng(lng);
        updateMapLocation(lat, lng);
        
        // Reverse geocode to get address
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode(
          { location: { lat, lng } },
          (results, status) => {
            if (status === 'OK' && results[0]) {
              setLocationAddress(results[0].formatted_address);
              if (!location) {
                setLocation(results[0].formatted_address);
              }
            }
          }
        );
      });

      // If we have initial coordinates, show them on the map
      if (initialData?.location_lat && initialData?.location_lng) {
        updateMapLocation(initialData.location_lat, initialData.location_lng);
      }

    } catch (error) {
      console.error('Error loading Google Maps:', error);
    }
  };

  const updateMapLocation = (lat, lng) => {
    if (!mapInstance.current) return;

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

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ 
      title, 
      type,
      description, 
      date, 
      location,
      location_address: locationAddress,
      location_lat: locationLat,
      location_lng: locationLng,
      location_place_id: locationPlaceId
    });
  };

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

          <div className="mb-3">
            <label className="form-label">
              <i className="bi bi-calendar-event me-1"></i>
              Date & Time *
            </label>
            <input 
              type="datetime-local" 
              className="form-control" 
              value={date} 
              onChange={e => setDate(e.target.value)} 
              required 
            />
          </div>

          {process.env.REACT_APP_GOOGLE_MAPS_API_KEY ? (
            <>
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

              {process.env.REACT_APP_GOOGLE_MAPS_API_KEY && process.env.REACT_APP_GOOGLE_MAPS_API_KEY !== 'YOUR_GOOGLE_MAPS_API_KEY_HERE' ? (
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
