"""
Chat routes for messaging between matched users.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User, Match, Message
from forms import MessageForm
from sqlalchemy import and_

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat/<int:match_id>')
@login_required
def chat(match_id):
    """Chat page for a specific match."""
    match = Match.query.get_or_404(match_id)
    
    # Verify current user is part of this match
    if current_user.id not in [match.user1_id, match.user2_id]:
        flash('You do not have access to this chat.', 'danger')
        return redirect(url_for('match.view_matches'))
    
    # Get the other user
    other_user = match.get_other_user(current_user.id)
    if not other_user:
        flash('Chat partner not found.', 'danger')
        return redirect(url_for('match.view_matches'))
    
    # Get messages
    messages = match.get_messages()
    
    # Mark messages from other user as read
    unread_messages = Message.query.filter(
        and_(
            Message.match_id == match_id,
            Message.sender_id != current_user.id,
            Message.is_read == False
        )
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    if unread_messages:
        db.session.commit()
    
    form = MessageForm()
    
    return render_template('chat.html', 
                         match=match,
                         other_user=other_user,
                         other_profile=other_user.profile,
                         messages=messages,
                         form=form)


@chat_bp.route('/chat/<int:match_id>/send', methods=['POST'])
@login_required
def send_message(match_id):
    """Send a message in a chat."""
    match = Match.query.get_or_404(match_id)
    
    # Verify current user is part of this match
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Access denied'}), 403
    
    form = MessageForm()
    if form.validate_on_submit():
        try:
            message = Message(
                match_id=match_id,
                sender_id=current_user.id,
                content=form.content.data.strip() if form.content.data else ''
            )
            
            db.session.add(message)
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'sender_id': message.sender_id,
                        'created_at': message.created_at.isoformat()
                    }
                })
            else:
                flash('Message sent!', 'success')
                return redirect(url_for('chat.chat', match_id=match_id))
                
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': 'Failed to send message'}), 500
            else:
                flash('Failed to send message. Please try again.', 'danger')
    
    if request.is_json:
        return jsonify({'error': 'Invalid message data'}), 400
    else:
        return redirect(url_for('chat.chat', match_id=match_id))


@chat_bp.route('/chat/<int:match_id>/messages')
@login_required
def get_messages(match_id):
    """Get messages for a chat (API endpoint)."""
    match = Match.query.get_or_404(match_id)
    
    # Verify current user is part of this match
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Access denied'}), 403
    
    messages = match.get_messages()
    messages_data = []
    
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender_id,
            'sender_name': message.sender.profile.name if message.sender.profile else message.sender.email,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        })
    
    return jsonify(messages_data)


@chat_bp.route('/chat/<int:match_id>/mark-read', methods=['POST'])
@login_required
def mark_messages_read(match_id):
    """Mark all messages in a chat as read."""
    match = Match.query.get_or_404(match_id)
    
    # Verify current user is part of this match
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Mark all unread messages from the other user as read
        unread_messages = Message.query.filter(
            and_(
                Message.match_id == match_id,
                Message.sender_id != current_user.id,
                Message.is_read == False
            )
        ).all()
        
        for message in unread_messages:
            message.is_read = True
        
        db.session.commit()
        
        return jsonify({'success': True, 'marked_count': len(unread_messages)})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to mark messages as read'}), 500


# For future real-time chat extensions
@chat_bp.route('/api/chat/<int:match_id>/info')
@login_required
def get_chat_info(match_id):
    """Get chat information (for real-time features)."""
    match = Match.query.get_or_404(match_id)
    
    # Verify current user is part of this match
    if current_user.id not in [match.user1_id, match.user2_id]:
        return jsonify({'error': 'Access denied'}), 403
    
    other_user = match.get_other_user(current_user.id)
    unread_count = Message.query.filter(
        and_(
            Message.match_id == match_id,
            Message.sender_id != current_user.id,
            Message.is_read == False
        )
    ).count()
    
    return jsonify({
        'match_id': match.id,
        'other_user': {
            'id': other_user.id,
            'name': other_user.profile.name if other_user.profile else other_user.email,
        },
        'unread_count': unread_count,
        'created_at': match.created_at.isoformat()
    })