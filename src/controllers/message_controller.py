"""Messaging routes."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.data_access.message_dal import MessageDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.user_dal import UserDAL
from src.utils.validators import Validator

message_bp = Blueprint('message', __name__, url_prefix='/messages')


def _resolve_other_user(thread):
    if current_user.user_id not in {thread.owner_id, thread.participant_id}:
        return None
    other_id = thread.participant_id if thread.owner_id == current_user.user_id else thread.owner_id
    return UserDAL.get_user_by_id(other_id)


@message_bp.route('/')
@login_required
def inbox():
    threads = MessageDAL.list_threads_for_user(current_user.user_id)
    thread_cards = []
    for thread in threads:
        resource = ResourceDAL.get_resource_by_id(thread.resource_id) if thread.resource_id else None
        other_user = _resolve_other_user(thread)
        thread_cards.append({'thread': thread, 'resource': resource, 'other_user': other_user})
    return render_template('messages/inbox.html', thread_cards=thread_cards)


@message_bp.route('/start/<int:owner_id>', methods=['GET', 'POST'])
@login_required
def start(owner_id: int):
    if owner_id == current_user.user_id:
        flash('You cannot message yourself.', 'warning')
        return redirect(url_for('message.inbox'))
    resource_id = request.args.get('resource_id', type=int)
    resource = ResourceDAL.get_resource_by_id(resource_id) if resource_id else None
    owner = UserDAL.get_user_by_id(owner_id)
    if not owner:
        flash('Recipient not found.', 'danger')
        return redirect(url_for('message.inbox'))

    if request.method == 'POST':
        body = request.form.get('body', '').strip()
        valid, message = Validator.validate_string(body, 3, 2000, 'Message')
        if not valid:
            flash(message, 'danger')
            return render_template('messages/compose.html', resource=resource)

        thread = MessageDAL.find_or_create_thread(owner_id=owner_id, participant_id=current_user.user_id, resource_id=resource_id)
        MessageDAL.post_message(thread.thread_id, current_user.user_id, body)
        flash('Message sent.', 'success')
        return redirect(url_for('message.thread', thread_id=thread.thread_id))

    return render_template('messages/compose.html', resource=resource)


@message_bp.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def thread(thread_id: int):
    thread = MessageDAL.get_thread_by_id(thread_id)
    if not thread:
        flash('Thread not found.', 'danger')
        return redirect(url_for('message.inbox'))
    other_user = _resolve_other_user(thread)
    if not other_user:
        flash('You do not have access to that thread.', 'danger')
        return redirect(url_for('message.inbox'))

    resource = ResourceDAL.get_resource_by_id(thread.resource_id) if thread.resource_id else None

    if request.method == 'POST':
        body = request.form.get('body', '').strip()
        valid, message = Validator.validate_string(body, 1, 2000, 'Message')
        if not valid:
            flash(message, 'danger')
        else:
            MessageDAL.post_message(thread.thread_id, current_user.user_id, body)
            flash('Sent.', 'success')
        return redirect(url_for('message.thread', thread_id=thread.thread_id))

    messages = MessageDAL.get_messages_for_thread(thread.thread_id, limit=200)
    return render_template('messages/thread.html', thread=thread, messages=messages, other_user=other_user, resource=resource)
