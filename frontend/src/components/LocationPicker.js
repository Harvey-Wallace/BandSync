import React, { useState, useRef, useEffect } from 'react';
import { Form, Card, Button } from 'react-bootstrap';
import { getGoogleMapsApiKey } from '../config/constants';

// Inject CSS for Google Places autocomplete
const injectGooglePlacesCSS = () => {
  if (document.getElementById('google-places-styles')) return;

  const styles = document.createElement('style');
  styles.id = 'google-places-styles';
  styles.textContent = `
    .pac-container {
      z-index: 9999 !important;
      border-radius: 8px !important;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
      border: 1px solid #dee2e6 !important;
      margin-top: 2px !important;
    }
    .pac-item {
      padding: 8px 12px !important;
      border-bottom: 1px solid #f1f3f4 !important;
      cursor: pointer !important;
    }
    .pac-item:hover {
      background-color: #f8f9fa !important;
    }
    .pac-item-selected {
      background-color: #e7f3ff !important;
    }
    .pac-matched {
      font-weight: 600 !important;
    }
  `;
  document.head.appendChild(styles);
};

const LocationPicker = ({ 
  value = '',
  coordinates = { lat: null, lng: null },
  placeId = '',
  onChange,
  onLocationSelect,
  placeholder = "Search for a location..."
}) => {
  const [isMapVisible, setIsMapVisible] = useState(false);
  const [isScriptLoaded, setIsScriptLoaded] = useState(false);
  const [scriptError, setScriptError] = useState(null);
  const inputRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const autocompleteRef = useRef(null);
  const mapInstanceRef = useRef(null);

  // Default map center (you can change this to your preferred location)
  const defaultCenter = { lat: 52.4862, lng: -1.8904 }; // Birmingham, UK

  useEffect(() => {
    injectGooglePlacesCSS();
    loadGoogleMapsApi();
    
    // Cleanup function
    return () => {
      if (autocompleteRef.current) {
        window.google?.maps?.event?.clearInstanceListeners(autocompleteRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isScriptLoaded && inputRef.current) {
      initializeAutocomplete();
    }
  }, [isScriptLoaded]);

  const loadGoogleMapsApi = () => {
    // Check if Google Maps is already loaded
    if (window.google && window.google.maps && window.google.maps.places) {
      setIsScriptLoaded(true);
      return;
    }

    // Check if script is already being loaded
    const existingScript = document.querySelector('script[src*="maps.googleapis.com"]');
    if (existingScript) {
      existingScript.addEventListener('load', () => setIsScriptLoaded(true));
      existingScript.addEventListener('error', () => setScriptError('Failed to load Google Maps'));
      return;
    }

    // Load the script
    const script = document.createElement('script');
    const apiKey = getGoogleMapsApiKey();
    
    if (!apiKey) {
      setScriptError('Google Maps API key not found');
      return;
    }

    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initGoogleMaps`;
    script.async = true;
    script.defer = true;
    
    // Create global callback
    window.initGoogleMaps = () => {
      setIsScriptLoaded(true);
      console.log('Google Maps API loaded successfully');
    };
    
    script.onerror = () => {
      setScriptError('Failed to load Google Maps API');
      console.error('Failed to load Google Maps API');
    };
    
    document.head.appendChild(script);
  };

  const initializeAutocomplete = () => {
    if (!window.google || !window.google.maps || !window.google.maps.places || !inputRef.current) {
      console.log('Google Maps API not ready for autocomplete');
      return;
    }

    try {
      // Clear any existing autocomplete
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(autocompleteRef.current);
      }

      const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
        types: ['establishment', 'geocode'],
        fields: ['place_id', 'geometry', 'name', 'formatted_address', 'address_components']
      });

      // Ensure the dropdown appears above modals
      const pacContainer = document.querySelector('.pac-container');
      if (pacContainer) {
        pacContainer.style.zIndex = '9999';
      }

      autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace();
        console.log('Place selected:', place);
        
        if (place.geometry && place.geometry.location) {
          const location = {
            address: place.formatted_address || place.name,
            lat: place.geometry.location.lat(),
            lng: place.geometry.location.lng(),
            placeId: place.place_id
          };

          onChange(location.address);
          onLocationSelect(location);
          
          // Update map if visible
          if (isMapVisible && mapInstanceRef.current) {
            updateMapLocation(location);
          }
        }
      });

      autocompleteRef.current = autocomplete;
      console.log('Autocomplete initialized successfully');

      // Force style the pac-container after a short delay
      setTimeout(() => {
        const pacContainer = document.querySelector('.pac-container');
        if (pacContainer) {
          pacContainer.style.zIndex = '9999';
          pacContainer.style.position = 'absolute';
        }
      }, 100);

    } catch (error) {
      console.error('Error initializing autocomplete:', error);
      setScriptError('Error initializing location search');
    }
  };

  const initializeMap = () => {
    if (!window.google || !mapRef.current) return;

    const center = coordinates.lat && coordinates.lng 
      ? { lat: coordinates.lat, lng: coordinates.lng }
      : defaultCenter;

    const map = new window.google.maps.Map(mapRef.current, {
      zoom: 15,
      center: center,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });

    const marker = new window.google.maps.Marker({
      position: center,
      map: map,
      draggable: true,
      title: 'Event Location'
    });

    // Add click listener to map
    map.addListener('click', (event) => {
      const clickedLocation = {
        lat: event.latLng.lat(),
        lng: event.latLng.lng()
      };
      
      marker.setPosition(clickedLocation);
      reverseGeocode(clickedLocation);
    });

    // Add drag listener to marker
    marker.addListener('dragend', (event) => {
      const draggedLocation = {
        lat: event.latLng.lat(),
        lng: event.latLng.lng()
      };
      
      reverseGeocode(draggedLocation);
    });

    mapInstanceRef.current = map;
    markerRef.current = marker;
  };

  const updateMapLocation = (location) => {
    if (mapInstanceRef.current && markerRef.current) {
      const position = { lat: location.lat, lng: location.lng };
      mapInstanceRef.current.setCenter(position);
      markerRef.current.setPosition(position);
    }
  };

  const reverseGeocode = (location) => {
    if (!window.google) return;

    const geocoder = new window.google.maps.Geocoder();
    geocoder.geocode({ location: location }, (results, status) => {
      if (status === 'OK' && results[0]) {
        const result = results[0];
        const locationData = {
          address: result.formatted_address,
          lat: location.lat,
          lng: location.lng,
          placeId: result.place_id
        };

        // Only update if user hasn't typed a custom address
        if (!inputRef.current || inputRef.current.value.trim() === '') {
          onChange(locationData.address);
        }
        
        onLocationSelect(locationData);
      }
    });
  };

  const toggleMap = () => {
    setIsMapVisible(!isMapVisible);
    if (!isMapVisible) {
      // Small delay to ensure the map container is rendered
      setTimeout(() => {
        initializeMap();
      }, 100);
    }
  };

  const handleInputChange = (e) => {
    onChange(e.target.value);
  };

  return (
    <Form.Group className="mb-3">
      <Form.Label>Location</Form.Label>
      <div className="d-flex gap-2 mb-2">
        <div className="flex-grow-1 position-relative">
          <Form.Control
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleInputChange}
            placeholder={isScriptLoaded ? placeholder : "Loading location search..."}
            disabled={!isScriptLoaded && !scriptError}
            className="flex-grow-1"
          />
          {!isScriptLoaded && !scriptError && (
            <div className="position-absolute top-50 end-0 translate-middle-y me-2">
              <div className="spinner-border spinner-border-sm text-muted" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}
        </div>
        <Button 
          variant="outline-primary"
          onClick={toggleMap}
          disabled={!isScriptLoaded}
          title={isMapVisible ? 'Hide Map' : 'Show Map'}
        >
          <i className={`fas ${isMapVisible ? 'fa-eye-slash' : 'fa-map-marker-alt'}`}></i>
        </Button>
      </div>
      
      {scriptError && (
        <Form.Text className="text-danger">
          <i className="fas fa-exclamation-triangle me-1"></i>
          {scriptError}
        </Form.Text>
      )}
      
      {isScriptLoaded && !autocompleteRef.current && (
        <Form.Text className="text-warning">
          <i className="fas fa-clock me-1"></i>
          Setting up location search...
        </Form.Text>
      )}

      {/* Debug info - remove in production */}
      {process.env.NODE_ENV === 'development' && (
        <Form.Text className="text-info small">
          API Key: {getGoogleMapsApiKey() ? '✓ Found' : '✗ Missing'} | 
          Script: {isScriptLoaded ? '✓ Loaded' : '✗ Loading'} | 
          Autocomplete: {autocompleteRef.current ? '✓ Ready' : '✗ Not Ready'}
        </Form.Text>
      )}
      
      {coordinates.lat && coordinates.lng && (
        <Form.Text className="text-muted">
          Coordinates: {coordinates.lat.toFixed(6)}, {coordinates.lng.toFixed(6)}
        </Form.Text>
      )}

      {isMapVisible && (
        <Card className="mt-2">
          <Card.Header className="bg-light">
            <small className="text-muted">
              <i className="fas fa-info-circle me-1"></i>
              Click on the map or drag the pin to set the exact location
            </small>
          </Card.Header>
          <Card.Body className="p-0">
            <div
              ref={mapRef}
              style={{ 
                height: '300px', 
                width: '100%',
                borderRadius: '0 0 0.375rem 0.375rem'
              }}
            />
          </Card.Body>
        </Card>
      )}
    </Form.Group>
  );
};

export default LocationPicker;
