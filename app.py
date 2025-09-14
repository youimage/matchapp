"""
Main Flask application for the generic matching app.
Configures the app, database, login manager, and routes.
"""
import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from models import db, User
# Import forms is handled by route blueprints

# Import route blueprints
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.match import match_bp
from routes.chat import chat_bp


def create_app(config=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matching_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(chat_bp)
    
    # Main routes
    @app.route('/')
    def index():
        """Home page route."""
        if current_user.is_authenticated:
            # Check if user has a complete profile
            if not current_user.profile or not current_user.profile.name:
                return redirect(url_for('profile.edit_profile'))
            return render_template('index.html')
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard with quick stats."""
        matches_count = len(current_user.get_matches())
        
        # Count likes given and received
        from models import Like
        likes_given = Like.query.filter_by(user_id=current_user.id).count()
        likes_received = Like.query.filter_by(liked_user_id=current_user.id).count()
        
        stats = {
            'matches_count': matches_count,
            'likes_given': likes_given,
            'likes_received': likes_received
        }
        
        return render_template('dashboard.html', stats=stats)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Template filters for UI enhancements
    @app.template_filter('datetime')
    def datetime_filter(dt):
        """Format datetime for templates."""
        if dt:
            return dt.strftime('%Y-%m-%d %H:%M')
        return ''
    
    @app.template_filter('timeago')
    def timeago_filter(dt):
        """Simple time ago filter."""
        if not dt:
            return ''
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = dt.replace(tzinfo=timezone.utc)
        
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    return app


# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)