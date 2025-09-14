"""
Database models for the generic matching app.
Defines User, Profile, Like, Match, and Message models with SQLAlchemy ORM.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and core user data."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_active(self):
        """Flask-Login requires is_active property."""
        return self.active
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    likes_given = db.relationship('Like', foreign_keys='Like.user_id', backref='user', cascade='all, delete-orphan')
    matches_as_user1 = db.relationship('Match', foreign_keys='Match.user1_id', backref='user1', cascade='all, delete-orphan')
    matches_as_user2 = db.relationship('Match', foreign_keys='Match.user2_id', backref='user2', cascade='all, delete-orphan')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_matches(self):
        """Get all matches for this user."""
        matches1 = Match.query.filter_by(user1_id=self.id).all()
        matches2 = Match.query.filter_by(user2_id=self.id).all()
        return matches1 + matches2
    
    def get_match_with_user(self, other_user_id):
        """Check if this user has a match with another user."""
        match = Match.query.filter(
            ((Match.user1_id == self.id) & (Match.user2_id == other_user_id)) |
            ((Match.user1_id == other_user_id) & (Match.user2_id == self.id))
        ).first()
        return match
    
    def has_liked(self, other_user_id):
        """Check if this user has already liked another user."""
        like = Like.query.filter_by(user_id=self.id, liked_user_id=other_user_id).first()
        return like is not None
    
    def __repr__(self):
        return f'<User {self.email}>'


class Profile(db.Model):
    """User profile model with detailed information for matching."""
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    location = db.Column(db.String(100), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_from_list(self, tags_list):
        """Set tags from a list of strings."""
        if tags_list:
            self.tags = ', '.join([tag.strip() for tag in tags_list if tag.strip()])
        else:
            self.tags = ''
    
    def __repr__(self):
        return f'<Profile {self.name}>'


class Like(db.Model):
    """Like model to track user likes (one-way)."""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    liked_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a user can't like the same person twice
    __table_args__ = (db.UniqueConstraint('user_id', 'liked_user_id', name='unique_like'),)
    
    @staticmethod
    def create_like_and_check_match(user_id, liked_user_id):
        """Create a like and check if it results in a match."""
        # Don't allow self-likes
        if user_id == liked_user_id:
            return None, False
        
        # Check if like already exists
        existing_like = Like.query.filter_by(user_id=user_id, liked_user_id=liked_user_id).first()
        if existing_like:
            return existing_like, False
        
        # Create the like
        new_like = Like(user_id=user_id, liked_user_id=liked_user_id)
        db.session.add(new_like)
        
        # Check if the other user has already liked back
        reverse_like = Like.query.filter_by(user_id=liked_user_id, liked_user_id=user_id).first()
        
        match_created = False
        if reverse_like:
            # Create a match
            existing_match = Match.query.filter(
                ((Match.user1_id == user_id) & (Match.user2_id == liked_user_id)) |
                ((Match.user1_id == liked_user_id) & (Match.user2_id == user_id))
            ).first()
            
            if not existing_match:
                new_match = Match(
                    user1_id=min(user_id, liked_user_id),
                    user2_id=max(user_id, liked_user_id)
                )
                db.session.add(new_match)
                match_created = True
        
        db.session.commit()
        return new_like, match_created
    
    def __repr__(self):
        return f'<Like user:{self.user_id} -> {self.liked_user_id}>'


class Match(db.Model):
    """Match model for mutual likes between users."""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='match', cascade='all, delete-orphan')
    
    # Ensure unique matches (user1_id should always be less than user2_id)
    __table_args__ = (db.UniqueConstraint('user1_id', 'user2_id', name='unique_match'),)
    
    def get_other_user(self, current_user_id):
        """Get the other user in this match."""
        if self.user1_id == current_user_id:
            return User.query.get(self.user2_id)
        elif self.user2_id == current_user_id:
            return User.query.get(self.user1_id)
        return None
    
    def get_messages(self, limit=50):
        """Get messages for this match, ordered by creation time."""
        return Message.query.filter_by(match_id=self.id).order_by(Message.created_at.asc()).limit(limit).all()
    
    def __repr__(self):
        return f'<Match {self.user1_id} <-> {self.user2_id}>'


class Message(db.Model):
    """Message model for chat between matched users."""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f'<Message from:{self.sender_id} in match:{self.match_id}>'