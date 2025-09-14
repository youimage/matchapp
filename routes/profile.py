"""
Profile management routes for viewing and editing user profiles.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User, Profile
from forms import ProfileForm

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def view_profile():
    """View current user's profile."""
    if not current_user.profile:
        # Create empty profile if it doesn't exist
        profile = Profile(user_id=current_user.id, name='')
        db.session.add(profile)
        db.session.commit()
    
    return render_template('profile.html', profile=current_user.profile)


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit current user's profile."""
    if not current_user.profile:
        # Create empty profile if it doesn't exist
        profile = Profile(user_id=current_user.id, name='')
        db.session.add(profile)
        db.session.commit()
    
    form = ProfileForm(obj=current_user.profile)
    
    if form.validate_on_submit():
        try:
            # Update profile fields
            current_user.profile.name = form.name.data
            current_user.profile.age = form.age.data
            current_user.profile.gender = form.gender.data
            current_user.profile.bio = form.bio.data
            current_user.profile.location = form.location.data
            
            # Handle tags
            if form.tags.data:
                # Convert comma-separated string to clean tags
                tags_list = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
                current_user.profile.set_tags_from_list(tags_list)
            else:
                current_user.profile.tags = ''
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
    
    return render_template('edit_profile.html', form=form, profile=current_user.profile)


@profile_bp.route('/profile/<int:user_id>')
@login_required
def view_other_profile(user_id):
    """View another user's profile."""
    if user_id == current_user.id:
        return redirect(url_for('profile.view_profile'))
    
    user = User.query.get_or_404(user_id)
    if not user.profile:
        flash('User profile not found.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if current user has already liked this user
    has_liked = current_user.has_liked(user_id)
    
    # Check if they have a match
    match = current_user.get_match_with_user(user_id)
    
    return render_template('view_profile.html', 
                         profile=user.profile, 
                         user=user,
                         has_liked=has_liked, 
                         has_match=match is not None)


# API endpoint for profile data (for future extensions)
@profile_bp.route('/api/profile/<int:user_id>')
@login_required
def get_profile_api(user_id):
    """API endpoint to get user profile data."""
    user = User.query.get_or_404(user_id)
    if not user.profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    profile_data = {
        'id': user.id,
        'name': user.profile.name,
        'age': user.profile.age,
        'gender': user.profile.gender,
        'bio': user.profile.bio,
        'tags': user.profile.get_tags_list(),
        'location': user.profile.location
    }
    
    return jsonify(profile_data)