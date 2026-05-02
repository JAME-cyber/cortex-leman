"""
Cortex Leman v5 — Tests Auth JWT + RBAC + API Keys

Teste:
- Login/logout avec les 7 comptes démo
- JWT token creation & verification
- RBAC permissions matrix
- API Key CRUD
- Fernet encryption
- RBAC route protection
"""
import os
import sys
import uuid
import pytest
from datetime import datetime, timezone

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Forcer SQLite en mémoire pour les tests
os.environ["DATABASE_URL"] = "sqlite:///file::memory:?cache=shared&uri=true"
os.environ["SECRET_KEY"] = "test-secret-key-for-auth-tests"
os.environ["JOURNAL_PATH"] = "/tmp/cortex-test-journal-auth"


# ============================================================
# Tests JWT Token
# ============================================================

class TestJWTToken:
    """Tests de création et vérification des tokens JWT"""

    def test_create_access_token(self):
        from core.security.auth import create_access_token, UserInfo

        user = UserInfo(
            id=str(uuid.uuid4()),
            email="test@cortex-leman.com",
            full_name="Test User",
            role="admin",
            allowed_verticals=["comptable"],
        )
        token = create_access_token(user)
        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_valid_token(self):
        from core.security.auth import create_access_token, verify_token, UserInfo

        user = UserInfo(
            id=str(uuid.uuid4()),
            email="test@cortex-leman.com",
            full_name="Test User",
            role="admin",
            allowed_verticals=["comptable"],
        )
        token = create_access_token(user)
        payload = verify_token(token, token_type="access")

        assert payload.sub == user.id
        assert payload.email == user.email
        assert payload.role == "admin"
        assert payload.type == "access"

    def test_verify_expired_token(self):
        from core.security.auth import create_access_token, verify_token, UserInfo
        from unittest.mock import patch
        from datetime import timedelta

        user = UserInfo(
            id=str(uuid.uuid4()),
            email="test@cortex-leman.com",
            full_name="Test User",
            role="admin",
        )

        # Créer un token déjà expiré
        with patch("core.security.auth.ACCESS_TOKEN_EXPIRE_MINUTES", -1):
            token = create_access_token(user)

        with pytest.raises(ValueError, match="Token invalide"):
            verify_token(token)

    def test_verify_wrong_type(self):
        from core.security.auth import create_access_token, verify_token, UserInfo

        user = UserInfo(
            id=str(uuid.uuid4()),
            email="test@cortex-leman.com",
            full_name="Test",
            role="viewer",
        )
        token = create_access_token(user)

        with pytest.raises(ValueError, match="Token type invalide"):
            verify_token(token, token_type="refresh")

    def test_refresh_token(self):
        from core.security.auth import create_refresh_token, verify_token, UserInfo

        user = UserInfo(
            id=str(uuid.uuid4()),
            email="test@cortex-leman.com",
            full_name="Test",
            role="admin",
        )
        token = create_refresh_token(user)
        payload = verify_token(token, token_type="refresh")
        assert payload.type == "refresh"
        assert payload.email == user.email


# ============================================================
# Tests Password Hashing
# ============================================================

class TestPasswordHash:
    """Tests de hash bcrypt"""

    def test_hash_and_verify(self):
        from core.security.auth import hash_password, verify_password

        hashed = hash_password("MySecret123!")
        assert hashed != "MySecret123!"
        assert verify_password("MySecret123!", hashed) is True

    def test_wrong_password(self):
        from core.security.auth import hash_password, verify_password

        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes(self):
        from core.security.auth import hash_password

        h1 = hash_password("same")
        h2 = hash_password("same")
        # bcrypt génère des salts différents
        assert h1 != h2


# ============================================================
# Tests API Key
# ============================================================

class TestApiKey:
    """Tests de gestion des clés API"""

    def test_generate_api_key(self):
        from core.security.auth import generate_api_key

        raw, hashed = generate_api_key()
        assert raw.startswith("cl_")
        assert len(raw) > 30
        assert len(hashed) == 64  # SHA-256 hex

    def test_verify_api_key(self):
        from core.security.auth import generate_api_key, verify_api_key

        raw, expected_hash = generate_api_key()
        computed_hash = verify_api_key(raw)
        assert computed_hash == expected_hash

    def test_different_keys_different_hashes(self):
        from core.security.auth import generate_api_key

        _, h1 = generate_api_key()
        _, h2 = generate_api_key()
        assert h1 != h2


# ============================================================
# Tests RBAC
# ============================================================

class TestRBAC:
    """Tests de la matrice de permissions RBAC"""

    def test_admin_full_access(self):
        from core.security.auth import has_permission

        assert has_permission("admin", "users", "create") is True
        assert has_permission("admin", "users", "delete") is True
        assert has_permission("admin", "intentions", "freeze") is True
        assert has_permission("admin", "settings", "update") is True

    def test_expert_limited_access(self):
        from core.security.auth import has_permission

        assert has_permission("expert", "users", "read") is True
        assert has_permission("expert", "intentions", "create") is True
        assert has_permission("expert", "users", "delete") is False
        assert has_permission("expert", "settings", "update") is False

    def test_operator_read_only(self):
        from core.security.auth import has_permission

        assert has_permission("operator", "intentions", "create") is True
        assert has_permission("operator", "intentions", "read") is True
        assert has_permission("operator", "users", "read") is False
        assert has_permission("operator", "settings", "read") is False

    def test_viewer_minimal_access(self):
        from core.security.auth import has_permission

        assert has_permission("viewer", "intentions", "read") is True
        assert has_permission("viewer", "journal", "read") is True
        assert has_permission("viewer", "intentions", "create") is False
        assert has_permission("viewer", "users", "read") is False

    def test_require_permission_raises(self):
        from core.security.auth import require_permission

        with pytest.raises(PermissionError):
            require_permission("viewer", "users", "create")

    def test_require_permission_passes(self):
        from core.security.auth import require_permission

        # Ne doit pas lever d'exception
        require_permission("admin", "users", "create")

    def test_invalid_role(self):
        from core.security.auth import has_permission

        assert has_permission("unknown", "users", "read") is False

    def test_invalid_resource(self):
        from core.security.auth import has_permission

        assert has_permission("admin", "nonexistent", "read") is False


# ============================================================
# Tests Fernet Encryption
# ============================================================

class TestEncryption:
    """Tests du chiffrement Fernet"""

    def test_encrypt_decrypt_string(self):
        from core.security.encryption import FernetEncryption

        enc = FernetEncryption("test-secret-key")
        plaintext = "Données sensibles RGPD"
        ciphertext = enc.encrypt(plaintext)

        assert ciphertext != plaintext
        assert enc.decrypt(ciphertext) == plaintext

    def test_encrypt_decrypt_empty(self):
        from core.security.encryption import FernetEncryption

        enc = FernetEncryption("test-secret-key")
        assert enc.encrypt("") == ""
        assert enc.decrypt("") == ""

    def test_encrypt_decrypt_dict(self):
        from core.security.encryption import FernetEncryption

        enc = FernetEncryption("test-secret-key")
        data = {
            "name": "Pierre Martin",
            "iban": "CH93 0076 2011 6238 5295 8",
            "email": "pierre@avocat.ch",
            "public_field": "visible",
        }

        encrypted = enc.encrypt_dict(data, ["iban", "email"])
        assert encrypted["iban"] != data["iban"]
        assert encrypted["email"] != data["email"]
        assert encrypted["name"] == data["name"]
        assert encrypted["public_field"] == "visible"
        assert encrypted["iban_encrypted"] is True

        decrypted = enc.decrypt_dict(encrypted)
        assert decrypted["iban"] == data["iban"]
        assert decrypted["email"] == data["email"]
        assert "iban_encrypted" not in decrypted

    def test_different_keys_different_ciphertext(self):
        from core.security.encryption import FernetEncryption

        enc1 = FernetEncryption("key-1")
        enc2 = FernetEncryption("key-2")

        c1 = enc1.encrypt("same data")
        c2 = enc2.encrypt("same data")

        assert c1 != c2
        assert enc1.decrypt(c1) == "same data"
        assert enc2.decrypt(c2) == "same data"

    def test_wrong_key_fails(self):
        from core.security.encryption import FernetEncryption
        from cryptography.fernet import InvalidToken

        enc1 = FernetEncryption("key-1")
        enc2 = FernetEncryption("key-2")

        ciphertext = enc1.encrypt("secret")

        with pytest.raises((ValueError, InvalidToken)):
            enc2.decrypt(ciphertext)

    def test_generate_key(self):
        from core.security.encryption import FernetEncryption

        key = FernetEncryption.generate_key()
        assert isinstance(key, str)
        assert len(key) > 20

    def test_singleton_init(self):
        from core.security.encryption import init_encryption, get_encryption

        init_encryption("test-key-for-init")
        enc = get_encryption()
        assert enc is not None

        encrypted = enc.encrypt("test singleton")
        assert enc.decrypt(encrypted) == "test singleton"


# ============================================================
# Tests User CRUD + Seed
# ============================================================

class TestUserCRUD:
    """Tests CRUD utilisateurs avec DB SQLite in-memory"""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Crée une DB SQLite en mémoire pour chaque test"""
        from core.db.models import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        self.db = SessionLocal()
        yield
        self.db.close()

    def test_create_user(self):
        from core.security.auth import create_user, UserCreate

        user = create_user(self.db, UserCreate(
            email="new@test.com",
            password="secret123",
            full_name="New User",
            role="expert",
            primary_vertical="comptable",
        ))

        assert user.email == "new@test.com"
        assert user.role.value == "expert"
        assert user.full_name == "New User"

    def test_create_duplicate_email_fails(self):
        from core.security.auth import create_user, UserCreate

        create_user(self.db, UserCreate(
            email="dup@test.com", password="pass", full_name="User 1", role="viewer"
        ))
        with pytest.raises(ValueError, match="Email déjà utilisé"):
            create_user(self.db, UserCreate(
                email="dup@test.com", password="pass2", full_name="User 2", role="viewer"
            ))

    def test_authenticate_success(self):
        from core.security.auth import create_user, authenticate_user, UserCreate

        create_user(self.db, UserCreate(
            email="auth@test.com", password="correct_pass", full_name="Auth User", role="operator"
        ))
        user = authenticate_user(self.db, "auth@test.com", "correct_pass")
        assert user is not None
        assert user.email == "auth@test.com"

    def test_authenticate_wrong_password(self):
        from core.security.auth import create_user, authenticate_user, UserCreate

        create_user(self.db, UserCreate(
            email="auth2@test.com", password="correct", full_name="Auth2", role="operator"
        ))
        user = authenticate_user(self.db, "auth2@test.com", "wrong")
        assert user is None

    def test_authenticate_nonexistent_user(self):
        from core.security.auth import authenticate_user

        user = authenticate_user(self.db, "nobody@test.com", "pass")
        assert user is None

    def test_seed_users(self):
        from core.security.auth import seed_users

        seed_users(self.db)
        from core.db.models import UserModel
        count = self.db.query(UserModel).count()
        assert count == 7  # 7 comptes démo

    def test_seed_idempotent(self):
        from core.security.auth import seed_users

        seed_users(self.db)
        seed_users(self.db)  # Ne doit pas crasher ni dupliquer
        from core.db.models import UserModel
        count = self.db.query(UserModel).count()
        assert count == 7

    def test_user_to_info(self):
        from core.security.auth import create_user, user_to_info, UserCreate

        user = create_user(self.db, UserCreate(
            email="info@test.com", password="pass", full_name="Info User",
            role="expert", primary_vertical="avocat",
            allowed_verticals=["avocat"],
        ))
        info = user_to_info(user)

        assert info.email == "info@test.com"
        assert info.role == "expert"
        assert info.primary_vertical == "avocat"
        assert "avocat" in info.allowed_verticals

    def test_login_count_increments(self):
        from core.security.auth import create_user, authenticate_user, UserCreate

        create_user(self.db, UserCreate(
            email="count@test.com", password="pass", full_name="Count User", role="viewer"
        ))

        # Login 3 fois
        for _ in range(3):
            authenticate_user(self.db, "count@test.com", "pass")

        user = authenticate_user(self.db, "count@test.com", "pass")
        assert user.login_count == 4  # 3 + le dernier


# ============================================================
# Tests Audit Logger
# ============================================================

class TestAuditLog:
    """Tests du logger d'audit"""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        from core.db.models import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        self.db = SessionLocal()
        yield
        self.db.close()

    def test_log_audit(self):
        from core.security.audit import log_audit
        from core.db.models import AuditLogModel

        log_audit(
            self.db,
            action="login_success",
            user_email="test@cortex-leman.com",
            ip_address="192.168.1.1",
            details={"method": "jwt"},
        )

        entries = self.db.query(AuditLogModel).all()
        assert len(entries) == 1
        assert entries[0].action == "login_success"
        assert entries[0].user_email == "test@cortex-leman.com"

    def test_log_audit_with_user_id(self):
        from core.security.audit import log_audit
        from core.db.models import AuditLogModel

        uid = str(uuid.uuid4())
        log_audit(
            self.db,
            action="api_key_created",
            user_id=uid,
            user_email="test@cortex-leman.com",
            resource_type="api_key",
            resource_id="key-123",
        )

        entry = self.db.query(AuditLogModel).first()
        assert str(entry.user_id) == uid
        assert entry.resource_type == "api_key"

    def test_log_audit_failure(self):
        from core.security.audit import log_audit
        from core.db.models import AuditLogModel

        log_audit(
            self.db,
            action="login_failed",
            user_email="hacker@evil.com",
            success=False,
            error_message="Identifiants invalides",
        )

        entry = self.db.query(AuditLogModel).first()
        assert entry.success is False
        assert entry.error_message == "Identifiants invalides"


# ============================================================
# Tests AuthContext
# ============================================================

class TestAuthContext:
    """Tests du contexte d'authentification"""

    def test_auth_context_creation(self):
        from api.dependencies import AuthContext

        ctx = AuthContext(
            user_id="test-id",
            email="test@cortex-leman.com",
            role="admin",
            verticals=["comptable", "avocat"],
        )
        assert ctx.user_id == "test-id"
        assert ctx.role == "admin"

    def test_auth_context_permission_check(self):
        from api.dependencies import AuthContext

        admin = AuthContext(user_id="1", email="a@b.com", role="admin")
        viewer = AuthContext(user_id="2", email="c@d.com", role="viewer")

        assert admin.has_permission("users", "create") is True
        assert viewer.has_permission("users", "create") is False

    def test_auth_context_require_permission_raises(self):
        from api.dependencies import AuthContext
        from fastapi import HTTPException

        viewer = AuthContext(user_id="1", email="v@b.com", role="viewer")
        with pytest.raises(HTTPException) as exc:
            viewer.require_permission("users", "create")
        assert exc.value.status_code == 403
