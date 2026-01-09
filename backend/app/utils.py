from functools import wraps
from flask import request, jsonify, session
from app.models import User
import json
from app import redis_client
from datetime import timedelta

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401

            user = User.query.get(session['user_id'])
            if not user or user.role not in roles:
                return jsonify({'error': 'Access denied'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def cache_get(key):
    """Get value from Redis cache"""
    try:
        if redis_client:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
    except Exception as e:
        print(f"Cache get error: {e}")
    return None

def cache_set(key, value, expiry=300):
    """Set value in Redis cache with expiry (default 5 minutes)"""
    try:
        if redis_client:
            redis_client.setex(key, expiry, json.dumps(value))
            return True
    except Exception as e:
        print(f"Cache set error: {e}")
    return False

def cache_delete(key):
    """Delete key from Redis cache"""
    try:
        if redis_client:
            redis_client.delete(key)
            return True
    except Exception as e:
        print(f"Cache delete error: {e}")
    return False

def cache_clear_pattern(pattern):
    """Clear all keys matching pattern"""
    try:
        if redis_client:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
    except Exception as e:
        print(f"Cache clear error: {e}")
    return False
