"""
Multiple Date Event API endpoints
Handles events with multiple possible dates and voting functionality
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Event, EventPossibleDate, EventDateVote, User, UserOrganization
from datetime import datetime
import json

multiple_dates_bp = Blueprint('multiple_dates', __name__)

@multiple_dates_bp.route('/events/<int:event_id>/possible-dates', methods=['GET'])
@jwt_required()
def get_possible_dates(event_id):
    """Get all possible dates for an event"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user has access to this event
        event = Event.query.get_or_404(event_id)
        user = User.query.get(current_user_id)
        
        # Check if user belongs to the organization
        user_org = UserOrganization.query.filter_by(
            user_id=current_user_id, 
            organization_id=event.organization_id
        ).first()
        
        if not user_org:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get possible dates with vote counts
        possible_dates = EventPossibleDate.query.filter_by(event_id=event_id).all()
        
        # Get user's votes for this event
        user_votes = {vote.possible_date_id: vote for vote in 
                     EventDateVote.query.filter_by(user_id=current_user_id, event_id=event_id).all()}
        
        result = []
        for pdate in possible_dates:
            user_vote = user_votes.get(pdate.id)
            result.append({
                'id': pdate.id,
                'date': pdate.date.isoformat() if pdate.date else None,
                'end_date': pdate.end_date.isoformat() if pdate.end_date else None,
                'arrive_by_time': pdate.arrive_by_time.strftime('%H:%M') if pdate.arrive_by_time else None,
                'start_time': pdate.start_time.strftime('%H:%M') if pdate.start_time else None,
                'end_time': pdate.end_time.strftime('%H:%M') if pdate.end_time else None,
                'vote_count': pdate.vote_count,
                'is_selected': pdate.is_selected,
                'user_vote': {
                    'can_attend': user_vote.can_attend if user_vote else None,
                    'preference_order': user_vote.preference_order if user_vote else None
                } if user_vote else None
            })
        
        return jsonify({
            'possible_dates': result,
            'event': {
                'id': event.id,
                'title': event.title,
                'has_multiple_dates': event.has_multiple_dates,
                'final_date_selected': event.final_date_selected,
                'date_selection_deadline': event.date_selection_deadline.isoformat() if event.date_selection_deadline else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@multiple_dates_bp.route('/events/<int:event_id>/possible-dates', methods=['POST'])
@jwt_required()
def add_possible_date(event_id):
    """Add a new possible date to an event (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user is admin for this event's organization
        event = Event.query.get_or_404(event_id)
        user_org = UserOrganization.query.filter_by(
            user_id=current_user_id, 
            organization_id=event.organization_id,
            role='Admin'
        ).first()
        
        if not user_org:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Parse dates and times
        date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data.get('end_date') else None
        
        arrive_by_time = datetime.strptime(data['arrive_by_time'], '%H:%M').time() if data.get('arrive_by_time') else None
        start_time = datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None
        end_time = datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None
        
        # Create new possible date
        possible_date = EventPossibleDate(
            event_id=event_id,
            date=date,
            end_date=end_date,
            arrive_by_time=arrive_by_time,
            start_time=start_time,
            end_time=end_time
        )
        
        db.session.add(possible_date)
        
        # Mark event as having multiple dates
        event.has_multiple_dates = True
        event.final_date_selected = False
        
        db.session.commit()
        
        return jsonify({
            'message': 'Possible date added successfully',
            'possible_date': {
                'id': possible_date.id,
                'date': possible_date.date.isoformat(),
                'end_date': possible_date.end_date.isoformat() if possible_date.end_date else None,
                'arrive_by_time': possible_date.arrive_by_time.strftime('%H:%M') if possible_date.arrive_by_time else None,
                'start_time': possible_date.start_time.strftime('%H:%M') if possible_date.start_time else None,
                'end_time': possible_date.end_time.strftime('%H:%M') if possible_date.end_time else None,
                'vote_count': possible_date.vote_count,
                'is_selected': possible_date.is_selected
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multiple_dates_bp.route('/events/<int:event_id>/vote-dates', methods=['POST'])
@jwt_required()
def vote_for_dates(event_id):
    """Vote for preferred dates for an event"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user has access to this event
        event = Event.query.get_or_404(event_id)
        user_org = UserOrganization.query.filter_by(
            user_id=current_user_id, 
            organization_id=event.organization_id
        ).first()
        
        if not user_org:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        votes = data.get('votes', [])  # List of {possible_date_id, can_attend, preference_order}
        
        # Remove existing votes for this user and event
        EventDateVote.query.filter_by(user_id=current_user_id, event_id=event_id).delete()
        
        # Add new votes
        for vote_data in votes:
            vote = EventDateVote(
                user_id=current_user_id,
                event_id=event_id,
                possible_date_id=vote_data['possible_date_id'],
                can_attend=vote_data.get('can_attend', True),
                preference_order=vote_data.get('preference_order', 1)
            )
            db.session.add(vote)
        
        # Update vote counts for each possible date
        possible_dates = EventPossibleDate.query.filter_by(event_id=event_id).all()
        for pdate in possible_dates:
            pdate.vote_count = EventDateVote.query.filter_by(
                possible_date_id=pdate.id, 
                can_attend=True
            ).count()
        
        db.session.commit()
        
        return jsonify({'message': 'Votes submitted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multiple_dates_bp.route('/events/<int:event_id>/select-final-date', methods=['POST'])
@jwt_required()
def select_final_date(event_id):
    """Select the final date for an event (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user is admin for this event's organization
        event = Event.query.get_or_404(event_id)
        user_org = UserOrganization.query.filter_by(
            user_id=current_user_id, 
            organization_id=event.organization_id,
            role='Admin'
        ).first()
        
        if not user_org:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        selected_date_id = data.get('possible_date_id')
        
        if not selected_date_id:
            return jsonify({'error': 'possible_date_id is required'}), 400
        
        # Get the selected possible date
        selected_date = EventPossibleDate.query.get_or_404(selected_date_id)
        
        if selected_date.event_id != event_id:
            return jsonify({'error': 'Date does not belong to this event'}), 400
        
        # Update event with final date
        event.date = selected_date.date
        event.end_date = selected_date.end_date
        event.arrive_by_time = selected_date.arrive_by_time
        event.start_time = selected_date.start_time
        event.end_time = selected_date.end_time
        event.final_date_selected = True
        
        # Mark the selected date
        EventPossibleDate.query.filter_by(event_id=event_id).update({'is_selected': False})
        selected_date.is_selected = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Final date selected successfully',
            'event': {
                'id': event.id,
                'title': event.title,
                'date': event.date.isoformat() if event.date else None,
                'end_date': event.end_date.isoformat() if event.end_date else None,
                'final_date_selected': event.final_date_selected
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@multiple_dates_bp.route('/events/<int:event_id>/date-votes-summary', methods=['GET'])
@jwt_required()
def get_date_votes_summary(event_id):
    """Get voting summary for event dates (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user is admin for this event's organization
        event = Event.query.get_or_404(event_id)
        user_org = UserOrganization.query.filter_by(
            user_id=current_user_id, 
            organization_id=event.organization_id,
            role='Admin'
        ).first()
        
        if not user_org:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all possible dates with detailed vote information
        possible_dates = EventPossibleDate.query.filter_by(event_id=event_id).all()
        
        result = []
        for pdate in possible_dates:
            votes = EventDateVote.query.filter_by(possible_date_id=pdate.id).all()
            
            voters = []
            for vote in votes:
                voter = User.query.get(vote.user_id)
                voters.append({
                    'user_id': voter.id,
                    'name': voter.name or voter.username,
                    'can_attend': vote.can_attend,
                    'preference_order': vote.preference_order
                })
            
            result.append({
                'id': pdate.id,
                'date': pdate.date.isoformat(),
                'vote_count': pdate.vote_count,
                'total_votes': len(votes),
                'can_attend_count': len([v for v in votes if v.can_attend]),
                'voters': sorted(voters, key=lambda x: x['preference_order'])
            })
        
        return jsonify({'date_votes': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
