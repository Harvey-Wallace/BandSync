import React, { useState, useRef, useEffect } from 'react';
import { Form, Card, Button } from 'react-bootstrap';
import { getGoogleMapsApiKey } from '../config/constants';

const LocationPicker = ({ 
  value = '',
  coordinates = { lat: null, lng: null },
  placeId = '',
  onChange,
  onLocationSelect,
  placeholder = "Search for a location..."
}) => {
  const [isMapVisible, setIsMapVisible] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const inputRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const autocompleteRef = useRef(null);
  const mapInstanceRef = useRef(null);

  // Default map center (you can change this to your preferred location)
  const defaultCenter = { lat: 52.4862, lng: -1.8904 }; // Birmingham, UK

  useEffect(() => {
    if (!window.google) {
      loadGoogleMapsScript();
    } else {
      initializeAutocomplete();
    }
  }, []);

  const loadGoogleMapsScript = () => {
    if (document.querySelector('script[src*="maps.googleapis.com"]')) {
      return;
    }

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${getGoogleMapsApiKey()}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setMapLoaded(true);
      initializeAutocomplete();
    };
    document.head.appendChild(script);
  };

  const initializeAutocomplete = () => {
    if (!window.google || !inputRef.current) return;

    const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
      types: ['establishment', 'geocode'],
      fields: ['place_id', 'geometry', 'name', 'formatted_address']
    });

    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      
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
        <Form.Control
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="flex-grow-1"
        />
        <Button 
          variant="outline-primary"
          onClick={toggleMap}
          title={isMapVisible ? 'Hide Map' : 'Show Map'}
        >
          <i className={`fas ${isMapVisible ? 'fa-eye-slash' : 'fa-map-marker-alt'}`}></i>
        </Button>
      </div>
      
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
