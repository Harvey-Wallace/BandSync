from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Event, EventSurvey, SurveyQuestion, SurveyResponse
import json
from datetime import datetime

surveys_bp = Blueprint('surveys', __name__)

# Survey Management
@surveys_bp.route('/api/events/<int:event_id>/surveys', methods=['GET'])
@jwt_required()
def get_event_surveys(event_id):
    """Get surveys for an event"""
    try:
        event = Event.query.get_or_404(event_id)
        surveys = EventSurvey.query.filter_by(event_id=event_id).order_by(EventSurvey.created_at.desc()).all()
        
        surveys_data = []
        for survey in surveys:
            survey_data = {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'is_active': survey.is_active,
                'is_anonymous': survey.is_anonymous,
                'created_by': {
                    'id': survey.creator.id,
                    'username': survey.creator.username,
                    'name': survey.creator.name
                },
                'created_at': survey.created_at.isoformat(),
                'deadline': survey.deadline.isoformat() if survey.deadline else None,
                'question_count': len(survey.questions),
                'response_count': len(set(response.user_id for response in survey.responses if response.user_id))
            }
            surveys_data.append(survey_data)
        
        return jsonify(surveys_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_bp.route('/api/events/<int:event_id>/surveys', methods=['POST'])
@jwt_required()
def create_survey(event_id):
    """Create a new survey for an event"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        
        # Parse deadline if provided
        deadline = None
        if data.get('deadline'):
            deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        
        # Create survey
        survey = EventSurvey(
            event_id=event_id,
            title=data['title'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True),
            is_anonymous=data.get('is_anonymous', False),
            created_by=user.id,
            deadline=deadline
        )
        
        db.session.add(survey)
        db.session.flush()  # Get the survey ID
        
        # Add questions
        questions = data.get('questions', [])
        for i, question_data in enumerate(questions):
            question = SurveyQuestion(
                survey_id=survey.id,
                question_text=question_data['question_text'],
                question_type=question_data['question_type'],
                question_options=json.dumps(question_data.get('question_options')) if question_data.get('question_options') else None,
                required=question_data.get('required', False),
                display_order=i
            )
            db.session.add(question)
        
        db.session.commit()
        
        return jsonify({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'is_active': survey.is_active,
            'is_anonymous': survey.is_anonymous,
            'created_by': {
                'id': user.id,
                'username': user.username,
                'name': user.name
            },
            'created_at': survey.created_at.isoformat(),
            'deadline': survey.deadline.isoformat() if survey.deadline else None,
            'question_count': len(questions)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_bp.route('/api/events/<int:event_id>/surveys/<int:survey_id>', methods=['GET'])
@jwt_required()
def get_survey_details(event_id, survey_id):
    """Get detailed survey information including questions"""
    try:
        survey = EventSurvey.query.get_or_404(survey_id)
        if survey.event_id != event_id:
            return jsonify({'error': 'Survey does not belong to this event'}), 400
        
        # Get questions
        questions = SurveyQuestion.query.filter_by(survey_id=survey_id).order_by(SurveyQuestion.display_order).all()
        
        questions_data = []
        for question in questions:
            question_data = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'question_options': json.loads(question.question_options) if question.question_options else None,
                'required': question.required,
                'display_order': question.display_order
            }
            questions_data.append(question_data)
        
        # Get user's responses if not anonymous
        user_responses = {}
        if not survey.is_anonymous:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            responses = SurveyResponse.query.filter_by(survey_id=survey_id, user_id=user.id).all()
            for response in responses:
                user_responses[response.question_id] = response.response_value
        
        return jsonify({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'is_active': survey.is_active,
            'is_anonymous': survey.is_anonymous,
            'created_by': {
                'id': survey.creator.id,
                'username': survey.creator.username,
                'name': survey.creator.name
            },
            'created_at': survey.created_at.isoformat(),
            'deadline': survey.deadline.isoformat() if survey.deadline else None,
            'questions': questions_data,
            'user_responses': user_responses
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_bp.route('/api/events/<int:event_id>/surveys/<int:survey_id>/responses', methods=['POST'])
@jwt_required()
def submit_survey_responses(event_id, survey_id):
    """Submit responses to a survey"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        survey = EventSurvey.query.get_or_404(survey_id)
        if survey.event_id != event_id:
            return jsonify({'error': 'Survey does not belong to this event'}), 400
        
        if not survey.is_active:
            return jsonify({'error': 'Survey is not active'}), 400
        
        # Check deadline
        if survey.deadline and datetime.utcnow() > survey.deadline:
            return jsonify({'error': 'Survey deadline has passed'}), 400
        
        data = request.get_json()
        responses = data.get('responses', {})
        
        # Process each response
        for question_id, response_value in responses.items():
            question_id = int(question_id)
            
            # Verify question belongs to this survey
            question = SurveyQuestion.query.get(question_id)
            if not question or question.survey_id != survey_id:
                continue
            
            # Check if response already exists
            existing_response = SurveyResponse.query.filter_by(
                survey_id=survey_id,
                question_id=question_id,
                user_id=user.id if not survey.is_anonymous else None
            ).first()
            
            if existing_response:
                # Update existing response
                existing_response.response_value = response_value
            else:
                # Create new response
                new_response = SurveyResponse(
                    survey_id=survey_id,
                    question_id=question_id,
                    user_id=user.id if not survey.is_anonymous else None,
                    response_value=response_value
                )
                db.session.add(new_response)
        
        db.session.commit()
        
        return jsonify({'message': 'Survey responses submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_bp.route('/api/events/<int:event_id>/surveys/<int:survey_id>/results', methods=['GET'])
@jwt_required()
def get_survey_results(event_id, survey_id):
    """Get survey results (Admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        survey = EventSurvey.query.get_or_404(survey_id)
        if survey.event_id != event_id:
            return jsonify({'error': 'Survey does not belong to this event'}), 400
        
        # Get questions and responses
        questions = SurveyQuestion.query.filter_by(survey_id=survey_id).order_by(SurveyQuestion.display_order).all()
        
        results = {
            'survey': {
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'is_anonymous': survey.is_anonymous,
                'total_responses': len(set(response.user_id for response in survey.responses if response.user_id))
            },
            'questions': []
        }
        
        for question in questions:
            responses = SurveyResponse.query.filter_by(question_id=question.id).all()
            
            question_result = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'question_options': json.loads(question.question_options) if question.question_options else None,
                'total_responses': len(responses),
                'responses': []
            }
            
            # Aggregate responses
            if question.question_type in ['multiple_choice', 'checkbox']:
                # Count responses by option
                response_counts = {}
                for response in responses:
                    value = response.response_value
                    if value:
                        if question.question_type == 'checkbox':
                            # Handle multiple selections
                            selections = json.loads(value) if value.startswith('[') else [value]
                            for selection in selections:
                                response_counts[selection] = response_counts.get(selection, 0) + 1
                        else:
                            response_counts[value] = response_counts.get(value, 0) + 1
                
                question_result['response_counts'] = response_counts
            
            elif question.question_type == 'rating':
                # Calculate average rating
                ratings = []
                for response in responses:
                    try:
                        rating = float(response.response_value)
                        ratings.append(rating)
                    except (ValueError, TypeError):
                        continue
                
                if ratings:
                    question_result['average_rating'] = sum(ratings) / len(ratings)
                    question_result['rating_distribution'] = {
                        str(i): ratings.count(i) for i in range(1, 6)
                    }
            
            # Individual responses (if not anonymous)
            if not survey.is_anonymous:
                individual_responses = []
                for response in responses:
                    individual_responses.append({
                        'user_id': response.user_id,
                        'username': response.user.username if response.user else 'Anonymous',
                        'name': response.user.name if response.user else 'Anonymous',
                        'response_value': response.response_value,
                        'submitted_at': response.created_at.isoformat()
                    })
                question_result['individual_responses'] = individual_responses
            
            results['questions'].append(question_result)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_bp.route('/api/events/<int:event_id>/surveys/<int:survey_id>', methods=['PUT'])
@jwt_required()
def update_survey(event_id, survey_id):
    """Update a survey"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        survey = EventSurvey.query.get_or_404(survey_id)
        if survey.event_id != event_id:
            return jsonify({'error': 'Survey does not belong to this event'}), 400
        
        data = request.get_json()
        
        # Update survey properties
        if 'title' in data:
            survey.title = data['title']
        if 'description' in data:
            survey.description = data['description']
        if 'is_active' in data:
            survey.is_active = data['is_active']
        if 'deadline' in data:
            if data['deadline']:
                survey.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            else:
                survey.deadline = None
        
        db.session.commit()
        
        return jsonify({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'is_active': survey.is_active,
            'is_anonymous': survey.is_anonymous,
            'deadline': survey.deadline.isoformat() if survey.deadline else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surveys_bp.route('/api/events/<int:event_id>/surveys/<int:survey_id>', methods=['DELETE'])
@jwt_required()
def delete_survey(event_id, survey_id):
    """Delete a survey"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        survey = EventSurvey.query.get_or_404(survey_id)
        if survey.event_id != event_id:
            return jsonify({'error': 'Survey does not belong to this event'}), 400
        
        db.session.delete(survey)
        db.session.commit()
        
        return jsonify({'message': 'Survey deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
