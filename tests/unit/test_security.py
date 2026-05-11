import pytest
from datetime import timedelta
from jose import JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    def test_hash_differs_from_plaintext(self):
        plain = "mysecretpassword"
        assert hash_password(plain) != plain

    def test_verify_correct_password(self):
        plain = "correcthorsebatterystaple"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_bcrypt_produces_different_hashes_for_same_password(self):
        p = "samepassword"
        h1 = hash_password(p)
        h2 = hash_password(p)
        assert h1 != h2

    def test_both_hashes_still_verify(self):
        p = "samepassword"
        h1 = hash_password(p)
        h2 = hash_password(p)
        assert verify_password(p, h1) is True
        assert verify_password(p, h2) is True

    def test_empty_password_hashes_and_verifies(self):
        plain = ""
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True
        assert verify_password("notempty", hashed) is False


class TestJwtTokens:
    def test_create_returns_string(self):
        token = create_access_token("42")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_roundtrip_preserves_sub(self):
        token = create_access_token("123")
        payload = decode_access_token(token)
        assert payload["sub"] == "123"

    def test_exp_claim_present(self):
        token = create_access_token("7")
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_custom_expiry_accepted(self):
        token = create_access_token("99", expires_delta=timedelta(hours=1))
        payload = decode_access_token(token)
        assert payload["sub"] == "99"

    def test_invalid_token_raises_jwt_error(self):
        with pytest.raises(JWTError):
            decode_access_token("not.a.valid.token")

    def test_tampered_signature_raises_jwt_error(self):
        token = create_access_token("1")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(JWTError):
            decode_access_token(tampered)

    def test_empty_string_raises_jwt_error(self):
        with pytest.raises(JWTError):
            decode_access_token("")

    def test_different_subjects_produce_different_tokens(self):
        t1 = create_access_token("1")
        t2 = create_access_token("2")
        assert t1 != t2
