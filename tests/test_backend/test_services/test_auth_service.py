import os
import sys
import unittest
from datetime import datetime, timedelta

# Ensure the backend directory is in the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from services.auth_service import AuthService
from models import User
from db import db


class TestAuthService(unittest.TestCase):

    def setUp(self):
        """Sets up a fresh AuthService and an in-memory SQLite database for each test."""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()

        self.auth_service = AuthService()

    def tearDown(self):
        """Drops all tables after each test to ensure a clean state."""
        with self.app.app_context():
            db.drop_all()

    def test_register_new_user_success(self):
        """Tests that a new user can be registered successfully."""
        with self.app.app_context():
            result = self.auth_service.register_user(
                email='test@ucd.ie',
                name='Test User',
                password='password123'
            )
            self.assertTrue(result['success'])
            self.assertEqual(result['user'].email, 'test@ucd.ie')
            self.assertEqual(result['user'].name, 'Test User')

    def test_register_duplicate_email_rejected(self):
        """Tests that registering the same email twice returns a failure."""
        with self.app.app_context():
            self.auth_service.register_user(
                email='duplicate@ucd.ie',
                name='First User',
                password='password123'
            )
            result = self.auth_service.register_user(
                email='duplicate@ucd.ie',
                name='Second User',
                password='differentpassword'
            )
            self.assertFalse(result['success'])
            self.assertIn('message', result)

    def test_authenticate_user_correct_credentials(self):
        """Tests that a registered user can log in with correct credentials."""
        with self.app.app_context():
            self.auth_service.register_user(
                email='login@ucd.ie',
                name='Login User',
                password='securepass'
            )
            result = self.auth_service.authenticate_user(
                email='login@ucd.ie',
                password='securepass'
            )
            self.assertTrue(result['success'])
            self.assertEqual(result['user'].email, 'login@ucd.ie')

    def test_authenticate_user_wrong_password(self):
        """Tests that login fails when the wrong password is provided."""
        with self.app.app_context():
            self.auth_service.register_user(
                email='wrongpass@ucd.ie',
                name='Wrong Pass User',
                password='correctpassword'
            )
            result = self.auth_service.authenticate_user(
                email='wrongpass@ucd.ie',
                password='wrongpassword'
            )
            self.assertFalse(result['success'])
            self.assertIn('message', result)

    def test_authenticate_nonexistent_user(self):
        """Tests that login fails for an email that was never registered."""
        with self.app.app_context():
            result = self.auth_service.authenticate_user(
                email='ghost@ucd.ie',
                password='anypassword'
            )
            self.assertFalse(result['success'])

    def test_new_user_default_stats(self):
        """Tests that a newly registered user has correct default profile statistics."""
        with self.app.app_context():
            result = self.auth_service.register_user(
                email='newuser@ucd.ie',
                name='New User',
                password='password123'
            )
            user = result['user']
            self.assertEqual(user.total_rides, 0)
            self.assertEqual(user.total_distance, 0)
            self.assertEqual(user.co2_saved, 0)
            self.assertEqual(user.current_plan, 'None')
            self.assertEqual(user.fav_station, 'None Yet')

    def test_check_and_clear_expired_plans(self):
        """Tests that expired subscription plans are correctly reset to None."""
        with self.app.app_context():
            # Register a user and manually set an already-expired plan
            self.auth_service.register_user(
                email='expired@ucd.ie',
                name='Expired User',
                password='password123'
            )
            user = User.query.get('expired@ucd.ie')
            user.current_plan = 'Monthly'
            user.plan_start_date = datetime.now() - timedelta(days=60)
            user.plan_end_date = datetime.now() - timedelta(days=30)
            db.session.commit()

            # Run the expiry check
            self.auth_service.check_and_clear_expired_plans()

            # Verify the plan was cleared
            updated_user = User.query.get('expired@ucd.ie')
            self.assertEqual(updated_user.current_plan, 'None')

    def test_active_plan_not_cleared(self):
        """Tests that a currently active plan is NOT reset by the expiry check."""
        with self.app.app_context():
            self.auth_service.register_user(
                email='active@ucd.ie',
                name='Active User',
                password='password123'
            )
            user = User.query.get('active@ucd.ie')
            user.current_plan = 'Annual'
            user.plan_start_date = datetime.now()
            user.plan_end_date = datetime.now() + timedelta(days=365)
            db.session.commit()

            self.auth_service.check_and_clear_expired_plans()

            updated_user = User.query.get('active@ucd.ie')
            self.assertEqual(updated_user.current_plan, 'Annual')


if __name__ == '__main__':
    unittest.main()
