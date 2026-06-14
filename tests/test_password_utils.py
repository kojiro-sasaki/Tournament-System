import pytest
from auth_backend.password_utils import hash_password, verify_password

def test_password_hashing_and_verification():
    password = "supersecretpassword"
    
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert hashed != password
    
    assert verify_password(password, hashed) is True
    
    assert verify_password("wrongpassword", hashed) is False

def test_hash_uniqueness():
    password = "testpassword"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    assert hash1 != hash2
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True