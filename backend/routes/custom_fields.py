from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Event, EventCustomField, EventFieldResponse, EventAttachment, EventSurvey, SurveyQuestion, SurveyResponse
from werkzeug.utils import secure_filename
import json
import os
import uuid
from datetime import datetime

custom_fields_bp = Blueprint('custom_fields', __name__)

# Custom Fields Management
@custom_fields_bp.route('/api/events/<int:event_id>/custom-fields', methods=['GET'])
@jwt_required()
def get_event_custom_fields(event_id):
    """Get custom fields for an event"""
    try:
        event = Event.query.get_or_404(event_id)
        fields = EventCustomField.query.filter_by(event_id=event_id).order_by(EventCustomField.display_order).all()
        
        fields_data = []
        for field in fields:
            field_data = {
                'id': field.id,
                'field_name': field.field_name,
                'field_type': field.field_type,
                'field_description': field.field_description,
                'required': field.required,
                'display_order': field.display_order,
                'field_options': json.loads(field.field_options) if field.field_options else None
            }
            fields_data.append(field_data)
        
        return jsonify(fields_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@custom_fields_bp.route('/api/events/<int:event_id>/custom-fields', methods=['POST'])
@jwt_required()
def create_custom_field(event_id):
    """Create a custom field for an event"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        
        # Validate field type
        valid_types = ['text', 'select', 'checkbox', 'textarea', 'number', 'email', 'phone']
        if data.get('field_type') not in valid_types:
            return jsonify({'error': 'Invalid field type'}), 400
        
        # Create custom field
        field = EventCustomField(
            event_id=event_id,
            field_name=data['field_name'],
            field_type=data['field_type'],
            field_description=data.get('field_description', ''),
            required=data.get('required', False),
            display_order=data.get('display_order', 0),
            field_options=json.dumps(data.get('field_options')) if data.get('field_options') else None
        )
        
        db.session.add(field)
        db.session.commit()
        
        return jsonify({
            'id': field.id,
            'field_name': field.field_name,
            'field_type': field.field_type,
            'field_description': field.field_description,
            'required': field.required,
            'display_order': field.display_order,
            'field_options': json.loads(field.field_options) if field.field_options else None
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@custom_fields_bp.route('/api/events/<int:event_id>/custom-fields/<int:field_id>', methods=['PUT'])
@jwt_required()
def update_custom_field(event_id, field_id):
    """Update a custom field"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        field = EventCustomField.query.get_or_404(field_id)
        if field.event_id != event_id:
            return jsonify({'error': 'Field does not belong to this event'}), 400
        
        data = request.get_json()
        
        # Update field properties
        if 'field_name' in data:
            field.field_name = data['field_name']
        if 'field_description' in data:
            field.field_description = data['field_description']
        if 'required' in data:
            field.required = data['required']
        if 'display_order' in data:
            field.display_order = data['display_order']
        if 'field_options' in data:
            field.field_options = json.dumps(data['field_options']) if data['field_options'] else None
        
        db.session.commit()
        
        return jsonify({
            'id': field.id,
            'field_name': field.field_name,
            'field_type': field.field_type,
            'field_description': field.field_description,
            'required': field.required,
            'display_order': field.display_order,
            'field_options': json.loads(field.field_options) if field.field_options else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@custom_fields_bp.route('/api/events/<int:event_id>/custom-fields/<int:field_id>', methods=['DELETE'])
@jwt_required()
def delete_custom_field(event_id, field_id):
    """Delete a custom field"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        field = EventCustomField.query.get_or_404(field_id)
        if field.event_id != event_id:
            return jsonify({'error': 'Field does not belong to this event'}), 400
        
        db.session.delete(field)
        db.session.commit()
        
        return jsonify({'message': 'Field deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Field Responses Management
@custom_fields_bp.route('/api/events/<int:event_id>/field-responses', methods=['GET'])
@jwt_required()
def get_field_responses(event_id):
    """Get user's responses to custom fields"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        responses = EventFieldResponse.query.filter_by(event_id=event_id, user_id=user.id).all()
        
        responses_data = {}
        for response in responses:
            responses_data[response.field_id] = response.response_value
        
        return jsonify(responses_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@custom_fields_bp.route('/api/events/<int:event_id>/field-responses', methods=['POST'])
@jwt_required()
def submit_field_responses(event_id):
    """Submit responses to custom fields"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        data = request.get_json()
        responses = data.get('responses', {})
        
        # Process each response
        for field_id, response_value in responses.items():
            field_id = int(field_id)
            
            # Check if response already exists
            existing_response = EventFieldResponse.query.filter_by(
                event_id=event_id,
                user_id=user.id,
                field_id=field_id
            ).first()
            
            if existing_response:
                # Update existing response
                existing_response.response_value = response_value
                existing_response.updated_at = datetime.utcnow()
            else:
                # Create new response
                new_response = EventFieldResponse(
                    event_id=event_id,
                    user_id=user.id,
                    field_id=field_id,
                    response_value=response_value
                )
                db.session.add(new_response)
        
        db.session.commit()
        
        return jsonify({'message': 'Responses submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@custom_fields_bp.route('/api/events/<int:event_id>/field-responses/summary', methods=['GET'])
@jwt_required()
def get_field_responses_summary(event_id):
    """Get summary of all responses to custom fields (Admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or user.role != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all fields for this event
        fields = EventCustomField.query.filter_by(event_id=event_id).all()
        
        summary = {}
        for field in fields:
            responses = EventFieldResponse.query.filter_by(field_id=field.id).all()
            
            field_summary = {
                'field_name': field.field_name,
                'field_type': field.field_type,
                'total_responses': len(responses),
                'responses': []
            }
            
            for response in responses:
                field_summary['responses'].append({
                    'user_id': response.user_id,
                    'username': response.user.username,
                    'name': response.user.name,
                    'response_value': response.response_value,
                    'submitted_at': response.updated_at.isoformat()
                })
            
            summary[field.id] = field_summary
        
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
