from flask import Blueprint, render_template, request, redirect, url_for
from models import User
from config import Config

# Define the blueprint for all HTML page rendering routes
pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def home():
    """
    Renders the main dashboard (landing page) including the interactive map.
    The Google Maps API key is securely retrieved from the Config class.
    """
    return render_template('index.html', google_maps_api_key=Config.GOOGLE_MAPS_KEY)

@pages_bp.route('/about')
def about():
    """Renders the static 'About Us' information page."""
    return render_template('about.html')

@pages_bp.route('/subscription')
def subscription():
    """Renders the membership or subscription plans page."""
    user_email = request.cookies.get('user_email')
    user = User.query.filter_by(email=user_email).first()
    return render_template('subscription.html', user=user)


@pages_bp.route('/howto')
def howto():
    """Renders the 'How it Works' instruction page for new users."""
    return render_template('howto.html')


@pages_bp.route('/profile')
def profile():
    """
    Renders the authenticated user's profile dashboard.
    It retrieves real-time statistics (rides, distance, CO2) from the database
    based on the identity stored in the 'user_email' cookie.
    """
    user_email = request.cookies.get('user_email')
    user = User.query.filter_by(email=user_email).first()
    return render_template('profile.html', user=user)