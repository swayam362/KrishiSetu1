import uuid
import datetime
from flask import Blueprint, jsonify, request
from backend.database import get_db, make_id_query
from backend.utils.security import sanitize_string
from backend.utils.middleware import token_required

message_bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@message_bp.route('/send', methods=['POST'])
@token_required
def send_message(current_user):
    """
    Send a private message to another user.
    `sender_id` is strictly derived from verified JWT token.
    """
    data = request.get_json(silent=True) or {}
    recipient_id = sanitize_string(str(data.get('recipient_id', '')))
    content = sanitize_string(str(data.get('content') or data.get('message') or ''), max_length=2000)
    related_product_id = sanitize_string(str(data.get('product_id', '')))
    related_order_id = sanitize_string(str(data.get('order_id', '')))

    if not recipient_id:
        return jsonify({"success": False, "error": "Recipient ID is required."}), 400

    if not content:
        return jsonify({"success": False, "error": "Message content cannot be empty."}), 400

    sender_id = str(current_user["id"])
    if sender_id == recipient_id:
        return jsonify({"success": False, "error": "Cannot send message to yourself."}), 400

    # Verify recipient exists
    users_col = get_db().get_collection("users")
    recipient = users_col.find_one(make_id_query(recipient_id))
    if not recipient:
        return jsonify({"success": False, "error": "Recipient user account not found."}), 404

    msg_id = f"MSG-{uuid.uuid4().hex[:10]}"
    now_iso = datetime.datetime.utcnow().isoformat()

    msg_doc = {
        "_id": msg_id,
        "id": msg_id,
        "sender_id": sender_id,
        "sender_name": current_user.get("full_name") or current_user.get("business_name", "User"),
        "sender_role": current_user.get("role", "farmer"),
        "recipient_id": recipient_id,
        "recipient_name": recipient.get("full_name") or recipient.get("business_name", "User"),
        "content": content,
        "product_id": related_product_id,
        "order_id": related_order_id,
        "is_read": False,
        "created_at": now_iso
    }

    messages_col = get_db().get_collection("messages")
    messages_col.insert_one(msg_doc)

    return jsonify({
        "success": True,
        "message": "Message sent successfully.",
        "data": msg_doc
    }), 201


@message_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """Retrieve all unique conversation contacts and last message for current user."""
    user_id = str(current_user["id"])
    messages_col = get_db().get_collection("messages")

    # Fetch messages where current user is either sender or recipient
    user_messages = messages_col.find({
        "$or": [{"sender_id": user_id}, {"recipient_id": user_id}]
    })

    conversations = {}
    for m in user_messages:
        m_dict = dict(m)
        m_dict["id"] = str(m_dict.get("_id") or m_dict.get("id"))
        m_dict.pop("_id", None)

        other_id = m_dict["recipient_id"] if m_dict["sender_id"] == user_id else m_dict["sender_id"]
        other_name = m_dict["recipient_name"] if m_dict["sender_id"] == user_id else m_dict["sender_name"]

        if other_id not in conversations or m_dict.get("created_at", "") > conversations[other_id]["last_message_at"]:
            conversations[other_id] = {
                "other_user_id": other_id,
                "other_user_name": other_name,
                "last_message": m_dict["content"],
                "last_message_at": m_dict["created_at"],
                "is_unread": not m_dict["is_read"] and m_dict["recipient_id"] == user_id
            }

    conv_list = list(conversations.values())
    conv_list.sort(key=lambda x: x["last_message_at"], reverse=True)

    return jsonify({
        "success": True,
        "count": len(conv_list),
        "conversations": conv_list
    }), 200


@message_bp.route('/thread/<other_user_id>', methods=['GET'])
@token_required
def get_thread(current_user, other_user_id):
    """
    Retrieve full chronological message thread between current user and other_user_id.
    Guarantees privacy: third parties cannot eavesdrop on conversations.
    """
    user_id = str(current_user["id"])
    messages_col = get_db().get_collection("messages")

    # Query strictly bidirectional messages between user_id and other_user_id
    thread_messages = messages_col.find({
        "$or": [
            {"sender_id": user_id, "recipient_id": other_user_id},
            {"sender_id": other_user_id, "recipient_id": user_id}
        ]
    })

    results = []
    for m in thread_messages:
        m_dict = dict(m)
        m_dict["id"] = str(m_dict.get("_id") or m_dict.get("id"))
        m_dict.pop("_id", None)
        results.append(m_dict)

    # Sort chronological
    results.sort(key=lambda x: x.get("created_at", ""))

    return jsonify({
        "success": True,
        "count": len(results),
        "messages": results
    }), 200
