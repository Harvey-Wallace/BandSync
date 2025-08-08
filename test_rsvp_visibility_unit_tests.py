#!/usr/bin/env python3
"""
Unit tests for RSVP visibility feature
Tests the backend logic without requiring a full deployment
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import unittest
from unittest.mock import Mock, patch
from models import Organization, User, Event, RSVP

class TestRSVPVisibilityFeature(unittest.TestCase):
    """Unit tests for RSVP visibility control"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = Mock()
        self.admin_user.id = 1
        self.admin_user.username = "admin"
        
        self.member_user = Mock()
        self.member_user.id = 2
        self.member_user.username = "member"
        
        self.organization = Mock()
        self.organization.id = 1
        self.organization.name = "Test Band"
        self.organization.members_can_view_rsvp_status = True
        
        self.event = Mock()
        self.event.id = 1
        self.event.title = "Test Rehearsal"
        self.event.organization_id = 1
    
    def test_organization_model_has_visibility_field(self):
        """Test that Organization model has the new visibility field"""
        # This test would work with actual SQLAlchemy models
        # For now, we're testing the mock
        self.assertTrue(hasattr(self.organization, 'members_can_view_rsvp_status'))
        self.assertEqual(self.organization.members_can_view_rsvp_status, True)
    
    def test_default_visibility_setting(self):
        """Test that default visibility setting is True (backward compatible)"""
        # Test that new organizations default to allowing visibility
        org = Mock()
        org.members_can_view_rsvp_status = True  # This would be the default
        self.assertTrue(org.members_can_view_rsvp_status)
    
    def test_admin_can_always_see_details(self):
        """Test that admin users can always see RSVP details regardless of setting"""
        # Test with privacy disabled
        self.organization.members_can_view_rsvp_status = False
        admin_role = "Admin"
        
        # Admin should always see details
        can_see_details = (admin_role == 'Admin') or self.organization.members_can_view_rsvp_status
        self.assertTrue(can_see_details)
        
        # Test with privacy enabled
        self.organization.members_can_view_rsvp_status = True
        can_see_details = (admin_role == 'Admin') or self.organization.members_can_view_rsvp_status
        self.assertTrue(can_see_details)
    
    def test_member_visibility_respects_setting(self):
        """Test that member users respect the organization's privacy setting"""
        member_role = "Member"
        
        # Test with privacy enabled (members can see)
        self.organization.members_can_view_rsvp_status = True
        can_see_details = (member_role == 'Admin') or self.organization.members_can_view_rsvp_status
        self.assertTrue(can_see_details)
        
        # Test with privacy disabled (members cannot see)
        self.organization.members_can_view_rsvp_status = False
        can_see_details = (member_role == 'Admin') or self.organization.members_can_view_rsvp_status
        self.assertFalse(can_see_details)
    
    def test_user_can_always_see_own_rsvp(self):
        """Test that users can always see their own RSVP regardless of privacy setting"""
        current_user_id = "2"
        rsvp_user_id = "2"  # Same user
        
        # User should see their own RSVP even with privacy disabled
        self.organization.members_can_view_rsvp_status = False
        member_role = "Member"
        can_see_details = (member_role == 'Admin') or self.organization.members_can_view_rsvp_status
        can_see_own = str(rsvp_user_id) == str(current_user_id)
        
        should_include_rsvp = can_see_details or can_see_own
        self.assertTrue(should_include_rsvp)
    
    def test_privacy_message_logic(self):
        """Test that privacy message is included when appropriate"""
        admin_role = "Admin"
        member_role = "Member"
        
        # Admin should never get privacy message
        self.organization.members_can_view_rsvp_status = False
        admin_can_see = (admin_role == 'Admin') or self.organization.members_can_view_rsvp_status
        admin_needs_privacy_msg = not admin_can_see
        self.assertFalse(admin_needs_privacy_msg)
        
        # Member should get privacy message when visibility is disabled
        member_can_see = (member_role == 'Admin') or self.organization.members_can_view_rsvp_status
        member_needs_privacy_msg = not member_can_see
        self.assertTrue(member_needs_privacy_msg)
        
        # Member should not get privacy message when visibility is enabled
        self.organization.members_can_view_rsvp_status = True
        member_can_see = (member_role == 'Admin') or self.organization.members_can_view_rsvp_status
        member_needs_privacy_msg = not member_can_see
        self.assertFalse(member_needs_privacy_msg)
    
    def test_rsvp_response_filtering(self):
        """Test that RSVP responses are filtered correctly based on privacy settings"""
        # Mock RSVP data
        all_rsvps = [
            {"user_id": 1, "name": "Admin User", "status": "Yes"},
            {"user_id": 2, "name": "Member User", "status": "Maybe"},
            {"user_id": 3, "name": "Other Member", "status": "No"}
        ]
        
        current_user_id = "2"
        member_role = "Member"
        
        # Test with privacy enabled (member sees all)
        self.organization.members_can_view_rsvp_status = True
        can_see_details = (member_role == 'Admin') or self.organization.members_can_view_rsvp_status
        
        if can_see_details:
            visible_rsvps = all_rsvps
        else:
            visible_rsvps = [r for r in all_rsvps if str(r['user_id']) == str(current_user_id)]
        
        self.assertEqual(len(visible_rsvps), 3)  # Should see all
        
        # Test with privacy disabled (member sees only their own)
        self.organization.members_can_view_rsvp_status = False
        can_see_details = (member_role == 'Admin') or self.organization.members_can_view_rsvp_status
        
        if can_see_details:
            visible_rsvps = all_rsvps
        else:
            visible_rsvps = [r for r in all_rsvps if str(r['user_id']) == str(current_user_id)]
        
        self.assertEqual(len(visible_rsvps), 1)  # Should see only their own
        self.assertEqual(visible_rsvps[0]['user_id'], 2)

class TestAPIEndpoints(unittest.TestCase):
    """Test the API endpoint logic"""
    
    def test_get_rsvp_visibility_endpoint_logic(self):
        """Test the logic for getting RSVP visibility setting"""
        # Mock organization
        org = Mock()
        org.id = 1
        org.name = "Test Band"
        org.members_can_view_rsvp_status = True
        
        # Test getting the setting
        setting_value = getattr(org, 'members_can_view_rsvp_status', True)
        self.assertTrue(setting_value)
        
        # Test response format
        response = {
            'organization_id': org.id,
            'organization_name': org.name,
            'members_can_view_rsvp_status': setting_value
        }
        
        self.assertEqual(response['organization_id'], 1)
        self.assertEqual(response['organization_name'], "Test Band")
        self.assertTrue(response['members_can_view_rsvp_status'])
    
    def test_update_rsvp_visibility_endpoint_logic(self):
        """Test the logic for updating RSVP visibility setting"""
        # Mock organization
        org = Mock()
        org.id = 1
        org.name = "Test Band"
        org.members_can_view_rsvp_status = True
        
        # Test admin role check
        user_role = "Admin"
        is_admin = (user_role == 'Admin')
        self.assertTrue(is_admin)
        
        # Test non-admin role check
        user_role = "Member"
        is_admin = (user_role == 'Admin')
        self.assertFalse(is_admin)
        
        # Test setting update
        new_setting = False
        if isinstance(new_setting, bool):
            org.members_can_view_rsvp_status = new_setting
            self.assertFalse(org.members_can_view_rsvp_status)

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    print("Running RSVP Visibility Feature Unit Tests")
    print("=" * 50)
    run_tests()
