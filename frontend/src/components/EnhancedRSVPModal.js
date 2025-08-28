import React, { useState, useEffect } from 'react';
import { Modal, Button, Form, Row, Col } from 'react-bootstrap';

function EnhancedRSVPModal({ 
  show, 
  onHide, 
  eventTitle,
  currentStatus,
  currentComments,
  currentLikelihood,
  onSubmit 
}) {
  const [status, setStatus] = useState(currentStatus || '');
  const [comments, setComments] = useState(currentComments || '');
  const [likelihood, setLikelihood] = useState(currentLikelihood || 50);

  // Reset form when modal opens with new data
  useEffect(() => {
    setStatus(currentStatus || '');
    setComments(currentComments || '');
    setLikelihood(currentLikelihood || 50);
  }, [currentStatus, currentComments, currentLikelihood, show]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const rsvpData = {
      status: status,
      comments: comments.trim() || null
    };

    // Only include likelihood for "Maybe" responses
    if (status === 'Maybe') {
      rsvpData.likelihood = likelihood;
    }

    onSubmit(rsvpData);
    onHide();
  };

  const handleStatusChange = (newStatus) => {
    setStatus(newStatus);
    // Reset likelihood to default when status changes
    if (newStatus === 'Maybe' && !currentLikelihood) {
      setLikelihood(50);
    }
  };

  const getStatusIcon = (statusValue) => {
    switch (statusValue) {
      case 'Yes': return 'fas fa-check-circle text-success';
      case 'Maybe': return 'fas fa-question-circle text-warning';
      case 'No': return 'fas fa-times-circle text-danger';
      default: return 'far fa-circle text-muted';
    }
  };

  const getLikelihoodColor = () => {
    if (likelihood >= 80) return '#28a745'; // Green
    if (likelihood >= 60) return '#ffc107'; // Yellow
    if (likelihood >= 40) return '#fd7e14'; // Orange
    return '#dc3545'; // Red
  };

  return (
    <Modal show={show} onHide={onHide} centered size="md">
      <Modal.Header closeButton>
        <Modal.Title>
          <i className="fas fa-reply me-2"></i>
          RSVP Response
        </Modal.Title>
      </Modal.Header>
      
      <Modal.Body>
        <div className="mb-3">
          <h6 className="text-muted mb-2">Event:</h6>
          <p className="fw-bold mb-3">{eventTitle}</p>
        </div>

        <Form onSubmit={handleSubmit}>
          {/* Status Selection */}
          <Form.Group className="mb-4">
            <Form.Label className="fw-bold">Your Response *</Form.Label>
            <div className="d-grid gap-2">
              <Row>
                <Col>
                  <Button
                    variant={status === 'Yes' ? 'success' : 'outline-success'}
                    className="w-100 d-flex align-items-center justify-content-center"
                    onClick={() => handleStatusChange('Yes')}
                    style={{ height: '50px' }}
                  >
                    <i className={getStatusIcon('Yes')} style={{ marginRight: '8px' }}></i>
                    Yes, I'll be there
                  </Button>
                </Col>
                <Col>
                  <Button
                    variant={status === 'Maybe' ? 'warning' : 'outline-warning'}
                    className="w-100 d-flex align-items-center justify-content-center"
                    onClick={() => handleStatusChange('Maybe')}
                    style={{ height: '50px' }}
                  >
                    <i className={getStatusIcon('Maybe')} style={{ marginRight: '8px' }}></i>
                    Maybe
                  </Button>
                </Col>
                <Col>
                  <Button
                    variant={status === 'No' ? 'danger' : 'outline-danger'}
                    className="w-100 d-flex align-items-center justify-content-center"
                    onClick={() => handleStatusChange('No')}
                    style={{ height: '50px' }}
                  >
                    <i className={getStatusIcon('No')} style={{ marginRight: '8px' }}></i>
                    Can't make it
                  </Button>
                </Col>
              </Row>
            </div>
          </Form.Group>

          {/* Likelihood Slider for Maybe responses */}
          {status === 'Maybe' && (
            <Form.Group className="mb-4">
              <Form.Label className="fw-bold d-flex align-items-center justify-content-between">
                <span>How likely are you to attend?</span>
                <span 
                  className="badge fs-6 px-3 py-2"
                  style={{ 
                    backgroundColor: getLikelihoodColor(),
                    color: 'white'
                  }}
                >
                  {likelihood}%
                </span>
              </Form.Label>
              <Form.Range
                min={1}
                max={100}
                value={likelihood}
                onChange={(e) => setLikelihood(parseInt(e.target.value))}
                className="custom-range"
                style={{
                  background: `linear-gradient(to right, #dc3545 0%, #fd7e14 40%, #ffc107 60%, #28a745 100%)`
                }}
              />
              <div className="d-flex justify-content-between text-muted small mt-1">
                <span>Unlikely</span>
                <span>Very Likely</span>
              </div>
            </Form.Group>
          )}

          {/* Comments */}
          <Form.Group className="mb-4">
            <Form.Label className="fw-bold">
              Comments <span className="text-muted fw-normal">(optional)</span>
            </Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Any additional notes, dietary restrictions, transportation needs, etc."
              maxLength={500}
            />
            <Form.Text className="text-muted">
              {comments.length}/500 characters
            </Form.Text>
          </Form.Group>
        </Form>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={handleSubmit}
          disabled={!status}
        >
          <i className="fas fa-save me-2"></i>
          Update RSVP
        </Button>
      </Modal.Footer>

      <style>{`
        .custom-range::-webkit-slider-thumb {
          background: ${getLikelihoodColor()};
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .custom-range::-moz-range-thumb {
          background: ${getLikelihoodColor()};
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
      `}</style>
    </Modal>
  );
}

export default EnhancedRSVPModal;
