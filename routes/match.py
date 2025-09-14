"""
Matching routes for liking users, viewing matches, and match discovery.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User, Profile, Like, Match, Message
from sqlalchemy import and_, or_, func

match_bp = Blueprint('match', __name__)


@match_bp.route('/discover')
@login_required
def discover():
    """Discover page showing potential matches."""
    # Get users that current user hasn't liked and aren't themselves
    liked_user_ids = db.session.query(Like.liked_user_id).filter_by(user_id=current_user.id).subquery()
    
    potential_matches = db.session.query(User).join(Profile).filter(
        and_(
            User.id != current_user.id,  # Not themselves
            User.id.notin_(liked_user_ids),  # Haven't liked already
            User.active == True,  # User is active
            Profile.name != ''  # Has a name in profile
        )
    ).limit(20).all()
    
    return render_template('discover.html', users=potential_matches)


@match_bp.route('/like/<int:user_id>', methods=['POST'])
@login_required
def like_user(user_id):
    """Like a user endpoint."""
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot like yourself'}), 400
    
    target_user = User.query.get_or_404(user_id)
    
    # Create like and check for match
    like, match_created = Like.create_like_and_check_match(current_user.id, user_id)
    
    if like is None:
        return jsonify({'error': 'Invalid like operation'}), 400
    
    response_data = {
        'liked': True,
        'match_created': match_created
    }
    
    if match_created:
        response_data['message'] = f"It's a match with {target_user.profile.name}!"
    
    return jsonify(response_data)


@match_bp.route('/matches')
@login_required
def view_matches():
    """View all matches for current user."""
    matches = current_user.get_matches()
    
    # Get match details with other user info
    match_details = []
    for match in matches:
        other_user = match.get_other_user(current_user.id)
        if other_user and other_user.profile:
            # Get latest message for preview
            latest_messages = match.get_messages(limit=1)
            latest_message = latest_messages[0] if latest_messages else None
            
            match_details.append({
                'match': match,
                'other_user': other_user,
                'other_profile': other_user.profile,
                'latest_message': latest_message,
                'unread_count': Message.query.filter(
                    and_(
                        Message.match_id == match.id,
                        Message.sender_id != current_user.id,
                        Message.is_read == False
                    )
                ).count()
            })
    
    # Sort by most recent activity
    match_details.sort(key=lambda x: x['match'].created_at, reverse=True)
    
    return render_template('matches.html', matches=match_details)


@match_bp.route('/unlike/<int:user_id>', methods=['POST'])
@login_required
def unlike_user(user_id):
    """Unlike a user (remove like)."""
    like = Like.query.filter_by(user_id=current_user.id, liked_user_id=user_id).first()
    
    if not like:
        return jsonify({'error': 'Like not found'}), 404
    
    try:
        # Remove the like
        db.session.delete(like)
        
        # Check if there was a match and remove it
        match = Match.query.filter(
            or_(
                and_(Match.user1_id == current_user.id, Match.user2_id == user_id),
                and_(Match.user1_id == user_id, Match.user2_id == current_user.id)
            )
        ).first()
        
        if match:
            # Check if the other user still likes current user
            reverse_like = Like.query.filter_by(user_id=user_id, liked_user_id=current_user.id).first()
            if not reverse_like:
                # No mutual like anymore, remove the match
                db.session.delete(match)
        
        db.session.commit()
        return jsonify({'success': True, 'unliked': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to unlike user'}), 500


# API endpoints for future extensions
@match_bp.route('/api/potential-matches')
@login_required
def get_potential_matches():
    """API endpoint to get potential matches."""
    liked_user_ids = db.session.query(Like.liked_user_id).filter_by(user_id=current_user.id).subquery()
    
    potential_matches = db.session.query(User).join(Profile).filter(
        and_(
            User.id != current_user.id,
            User.id.notin_(liked_user_ids),
            User.active == True,
            Profile.name != ''
        )
    ).limit(10).all()
    
    matches_data = []
    for user in potential_matches:
        matches_data.append({
            'id': user.id,
            'name': user.profile.name,
            'age': user.profile.age,
            'bio': user.profile.bio,
            'tags': user.profile.get_tags_list(),
            'location': user.profile.location
        })
    
    return jsonify(matches_data)


@match_bp.route('/api/matches')
@login_required
def get_matches_api():
    """API endpoint to get user's matches."""
    matches = current_user.get_matches()
    matches_data = []
    
    for match in matches:
        other_user = match.get_other_user(current_user.id)
        if other_user and other_user.profile:
            matches_data.append({
                'match_id': match.id,
                'other_user': {
                    'id': other_user.id,
                    'name': other_user.profile.name,
                    'age': other_user.profile.age,
                    'bio': other_user.profile.bio
                },
                'created_at': match.created_at.isoformat()
            })
    
    return jsonify(matches_data)