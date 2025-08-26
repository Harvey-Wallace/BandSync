import React, { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader, Button, Alert, Badge, Progress } from 'reactstrap';
import { Calendar, Clock, Users, CheckCircle, XCircle, Vote } from 'lucide-react';
import { getApiUrl } from '../utils/api';

const EventDateVoting = ({ eventId, isAdmin = false, onVoteUpdate, onDateSelected }) => {
  const [possibleDates, setPossibleDates] = useState([]);
  const [userVotes, setUserVotes] = useState([]);
  const [votesSummary, setVotesSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchPossibleDates();
    fetchVotesSummary();
  }, [eventId]);

  const fetchPossibleDates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/multiple-dates/${eventId}/possible-dates`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPossibleDates(data.possible_dates || []);
        setUserVotes(data.user_votes || []);
      }
    } catch (err) {
      setError('Failed to load possible dates');
    } finally {
      setLoading(false);
    }
  };

  const fetchVotesSummary = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/multiple-dates/${eventId}/votes-summary`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setVotesSummary(data);
      }
    } catch (err) {
      console.error('Failed to load votes summary:', err);
    }
  };

  const handleVoteChange = (dateId, canAttend) => {
    setUserVotes(prev => {
      const existingVote = prev.find(vote => vote.possible_date_id === dateId);
      if (existingVote) {
        return prev.map(vote => 
          vote.possible_date_id === dateId 
            ? { ...vote, can_attend: canAttend }
            : vote
        );
      } else {
        return [...prev, { possible_date_id: dateId, can_attend: canAttend }];
      }
    });
  };

  const submitVotes = async () => {
    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/multiple-dates/${eventId}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ votes: userVotes })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit votes');
      }

      setSuccess('Your votes have been submitted successfully!');
      await fetchVotesSummary();
      
      if (onVoteUpdate) {
        onVoteUpdate();
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const selectFinalDate = async (dateId) => {
    setSubmitting(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${getApiUrl()}/multiple-dates/${eventId}/select-final-date`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ possible_date_id: dateId })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to select final date');
      }

      setSuccess('Final date has been selected!');
      
      if (onDateSelected) {
        onDateSelected(dateId);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getVoteCount = (dateId, voteType) => {
    const summary = votesSummary[dateId];
    if (!summary) return 0;
    return voteType === 'yes' ? summary.yes_votes : summary.no_votes;
  };

  const getTotalVotes = (dateId) => {
    const summary = votesSummary[dateId];
    if (!summary) return 0;
    return summary.total_votes;
  };

  const getVotePercentage = (dateId, voteType) => {
    const total = getTotalVotes(dateId);
    if (total === 0) return 0;
    const count = getVoteCount(dateId, voteType);
    return Math.round((count / total) * 100);
  };

  const getUserVote = (dateId) => {
    const vote = userVotes.find(v => v.possible_date_id === dateId);
    return vote ? vote.can_attend : null;
  };

  if (loading) {
    return (
      <Card>
        <CardBody className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </CardBody>
      </Card>
    );
  }

  if (possibleDates.length === 0) {
    return (
      <Card>
        <CardBody className="text-center">
          <Calendar size={48} className="text-muted mb-3" />
          <h5>No multiple dates available</h5>
          <p className="text-muted">This event doesn't have multiple date options.</p>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <h5 className="mb-0">
          <Vote className="me-2" size={20} />
          Vote on Event Dates
          {isAdmin && (
            <Badge color="warning" className="ms-2">Admin View</Badge>
          )}
        </h5>
      </CardHeader>
      <CardBody>
        {error && <Alert color="danger">{error}</Alert>}
        {success && <Alert color="success">{success}</Alert>}
        
        <div className="space-y-4">
          {possibleDates.map((date) => {
            const userVote = getUserVote(date.id);
            const yesCount = getVoteCount(date.id, 'yes');
            const noCount = getVoteCount(date.id, 'no');
            const totalVotes = getTotalVotes(date.id);
            const yesPercentage = getVotePercentage(date.id, 'yes');
            
            return (
              <Card key={date.id} className={`border-2 ${userVote === true ? 'border-success' : userVote === false ? 'border-danger' : 'border-secondary'}`}>
                <CardBody>
                  <div className="d-flex justify-content-between align-items-start mb-3">
                    <div>
                      <h6 className="mb-1">
                        <Calendar size={16} className="me-2" />
                        {formatDateTime(date.date)}
                      </h6>
                      {date.end_date && (
                        <p className="mb-1 text-muted">
                          <Clock size={14} className="me-1" />
                          Ends: {formatDateTime(date.end_date)}
                        </p>
                      )}
                      <div className="d-flex gap-3 text-sm text-muted">
                        {date.arrive_by_time && (
                          <span>Arrive by: {formatTime(date.arrive_by_time)}</span>
                        )}
                        {date.start_time && (
                          <span>Start: {formatTime(date.start_time)}</span>
                        )}
                        {date.end_time && (
                          <span>End: {formatTime(date.end_time)}</span>
                        )}
                      </div>
                    </div>
                    
                    {isAdmin && (
                      <Button
                        color="primary"
                        size="sm"
                        onClick={() => selectFinalDate(date.id)}
                        disabled={submitting}
                      >
                        Select This Date
                      </Button>
                    )}
                  </div>

                  {/* Voting Buttons */}
                  {!isAdmin && (
                    <div className="d-flex gap-2 mb-3">
                      <Button
                        color={userVote === true ? "success" : "outline-success"}
                        size="sm"
                        onClick={() => handleVoteChange(date.id, true)}
                      >
                        <CheckCircle size={16} className="me-1" />
                        I can attend
                      </Button>
                      <Button
                        color={userVote === false ? "danger" : "outline-danger"}
                        size="sm"
                        onClick={() => handleVoteChange(date.id, false)}
                      >
                        <XCircle size={16} className="me-1" />
                        I can't attend
                      </Button>
                    </div>
                  )}

                  {/* Vote Summary */}
                  {totalVotes > 0 && (
                    <div className="mb-2">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <span className="text-sm text-muted">
                          <Users size={14} className="me-1" />
                          {yesCount} can attend, {noCount} cannot ({totalVotes} total votes)
                        </span>
                        <span className="text-sm fw-bold">{yesPercentage}%</span>
                      </div>
                      <Progress value={yesPercentage} color="success" />
                    </div>
                  )}

                  {totalVotes === 0 && (
                    <p className="text-muted text-sm mb-0">
                      <Users size={14} className="me-1" />
                      No votes yet
                    </p>
                  )}
                </CardBody>
              </Card>
            );
          })}
        </div>

        {!isAdmin && userVotes.length > 0 && (
          <div className="text-center mt-4">
            <Button
              color="primary"
              onClick={submitVotes}
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Submit My Votes'}
            </Button>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default EventDateVoting;
