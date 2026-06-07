import re
from .password_utils import hash_password
from src.database.connection import supabase


class RegistrationError(Exception):
    pass


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    if len(username) < 3 or len(username) > 20:
        return False
    return username.isalnum() or '_' in username


def validate_password(password):
    return len(password) >= 8


def register_user(email, username, password):
    if not email or not username or not password:
        raise RegistrationError("All fields are required")
    
    if not validate_email(email):
        raise RegistrationError("Invalid email format")
    
    if not validate_username(username):
        raise RegistrationError("Username must be 3-20 characters (alphanumeric or underscore)")
    
    if not validate_password(password):
        raise RegistrationError("Password must be at least 6 characters")
    
    password_hash = hash_password(password)
    
    try:
        # Insert user into database
        response = supabase.table('users').insert({
            'email': email,
            'username': username,
            'password_hash': password_hash,
            'role': 'captain'  # All registered users are team captains
        }).execute()
        
        if response.data:
            user = response.data[0]
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        else:
            raise RegistrationError("Failed to create user")
            
    except Exception as e:
        error_msg = str(e)
        
        # Check for duplicate email or username
        if 'duplicate key' in error_msg.lower() or 'unique constraint' in error_msg.lower():
            if 'email' in error_msg.lower():
                raise RegistrationError("Email already exists")
            elif 'username' in error_msg.lower():
                raise RegistrationError("Username already exists")
            else:
                raise RegistrationError("User already exists")
        
        raise RegistrationError(f"Registration failed: {error_msg}")
