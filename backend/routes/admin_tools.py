from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import User, Event, Organization, db

admin_tools_bp = Blueprint('admin_tools', __name__)

@admin_tools_bp.route('/tools', methods=['GET'])
def get_admin_tools():
    return jsonify({"msg": "Admin tools endpoint"})

# User Management

@admin_tools_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.json
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created", "id": new_user.id})

@admin_tools_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.json
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({"msg": "User updated"})

@admin_tools_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "User deleted"})

@admin_tools_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    users = User.query.paginate(page=page, per_page=per_page)
    user_list = [{"id": user.id, "name": user.name, "email": user.email} for user in users.items]
    return jsonify(user_list)

# Event Management

@admin_tools_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    data = request.json
    new_event = Event(name=data['name'], date=data['date'])
    db.session.add(new_event)
    db.session.commit()
    return jsonify({"msg": "Event created", "id": new_event.id})

@admin_tools_bp.route('/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    data = request.json
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"msg": "Event not found"}), 404
    event.name = data.get('name', event.name)
    event.date = data.get('date', event.date)
    db.session.commit()
    return jsonify({"msg": "Event updated"})

@admin_tools_bp.route('/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"msg": "Event not found"}), 404
    db.session.delete(event)
    db.session.commit()
    return jsonify({"msg": "Event deleted"})

@admin_tools_bp.route('/events', methods=['GET'])
@jwt_required()
def get_events():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    events = Event.query.paginate(page=page, per_page=per_page)
    event_list = [{"id": event.id, "name": event.name, "date": event.date} for event in events.items]
    return jsonify(event_list)

# Organization Management

@admin_tools_bp.route('/organizations', methods=['POST'])
@jwt_required()
def create_organization():
    data = request.json
    new_organization = Organization(name=data['name'])
    db.session.add(new_organization)
    db.session.commit()
    return jsonify({"msg": "Organization created", "id": new_organization.id})

@admin_tools_bp.route('/organizations/<int:org_id>', methods=['PUT'])
@jwt_required()
def update_organization(org_id):
    data = request.json
    organization = Organization.query.get(org_id)
    if not organization:
        return jsonify({"msg": "Organization not found"}), 404
    organization.name = data.get('name', organization.name)
    db.session.commit()
    return jsonify({"msg": "Organization updated"})

@admin_tools_bp.route('/organizations/<int:org_id>', methods=['DELETE'])
@jwt_required()
def delete_organization(org_id):
    organization = Organization.query.get(org_id)
    if not organization:
        return jsonify({"msg": "Organization not found"}), 404
    db.session.delete(organization)
    db.session.commit()
    return jsonify({"msg": "Organization deleted"})

@admin_tools_bp.route('/organizations', methods=['GET'])
@jwt_required()
def get_organizations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    organizations = Organization.query.paginate(page=page, per_page=per_page)
    organization_list = [{"id": org.id, "name": org.name} for org in organizations.items]
    return jsonify(organization_list)
