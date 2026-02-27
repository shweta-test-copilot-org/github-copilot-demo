"""
==============================================================================
LEGACY AUTHENTICATION PROVIDER
==============================================================================

!!! IMPORTANT: LEGACY CODE - DO NOT MODIFY WITHOUT SECURITY TEAM APPROVAL !!!

This module provides session-based authentication for the Contoso Orders API.
It was implemented in 2019 and is still in production use.

HISTORY:
- 2019-Q2: Initial implementation (ticket SEC-1234)
- 2021-Q1: Added session caching (ticket SEC-2456)
- 2023-Q3: Security audit passed (report #SA-2023-089)

CONTACTS:
- Security Team: security@contoso.com
- On-call: #security-oncall Slack channel

DO NOT:
- Implement your own authentication
- Modify session handling logic
- Change the Session class structure
- Add new authentication methods without approval

All API endpoints MUST use get_current_session() for authentication.
==============================================================================
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import logging

# NOTE: This legacy module uses stdlib logging, not structlog
logger = logging.getLogger(__name__)


# =============================================================================
# SESSION CONFIGURATION
# DO NOT MODIFY THESE VALUES - They are security-critical
# =============================================================================

SESSION_TIMEOUT_MINUTES = 30
SESSION_TOKEN_LENGTH = 64
MAX_SESSIONS_PER_USER = 5


# =============================================================================
# SESSION DATA STRUCTURES
# =============================================================================

@dataclass
class Session:
    """
    User session object.
    
    WARNING: Do not add fields without Security Team review.
    The session structure is validated by security middleware.
    """
    session_id: str
    user_id: str
    user_email: str
    is_admin: bool
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return not self.is_expired


# =============================================================================
# SESSION STORE
# In production, this is backed by Redis. Here we use in-memory for demo.
# =============================================================================

_SESSION_STORE: dict[str, Session] = {}

# Pre-populate with test sessions for development
_SESSION_STORE["dev_session_001"] = Session(
    session_id="dev_session_001",
    user_id="cust_001",
    user_email="orders@acme.com",
    is_admin=False,
    created_at=datetime.utcnow(),
    expires_at=datetime.utcnow() + timedelta(hours=24),
)

_SESSION_STORE["admin_session_001"] = Session(
    session_id="admin_session_001",
    user_id="admin_001",
    user_email="admin@contoso.com",
    is_admin=True,
    created_at=datetime.utcnow(),
    expires_at=datetime.utcnow() + timedelta(hours=24),
)


# =============================================================================
# SESSION MANAGEMENT FUNCTIONS
# =============================================================================

def create_session(
    user_id: str,
    user_email: str,
    is_admin: bool = False,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Session:
    """
    Create a new session for a user.
    
    SECURITY NOTE: This should only be called after successful authentication
    through the corporate SSO system.
    """
    session_id = _generate_session_token()
    now = datetime.utcnow()
    
    session = Session(
        session_id=session_id,
        user_id=user_id,
        user_email=user_email,
        is_admin=is_admin,
        created_at=now,
        expires_at=now + timedelta(minutes=SESSION_TIMEOUT_MINUTES),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Enforce max sessions per user
    _cleanup_user_sessions(user_id)
    
    _SESSION_STORE[session_id] = session
    logger.info(f"Session created for user {user_id}")
    
    return session


def get_session(session_id: str) -> Optional[Session]:
    """
    Retrieve a session by ID.
    
    Returns None if session doesn't exist or is expired.
    """
    session = _SESSION_STORE.get(session_id)
    
    if session is None:
        return None
    
    if session.is_expired:
        # Clean up expired session
        invalidate_session(session_id)
        return None
    
    return session


def invalidate_session(session_id: str) -> bool:
    """
    Invalidate (logout) a session.
    
    Returns True if session was invalidated, False if not found.
    """
    if session_id in _SESSION_STORE:
        del _SESSION_STORE[session_id]
        logger.info(f"Session invalidated: {session_id[:8]}...")
        return True
    return False


def refresh_session(session_id: str) -> Optional[Session]:
    """
    Extend a session's expiration time.
    
    Called on each authenticated request to keep active sessions alive.
    """
    session = get_session(session_id)
    
    if session is None:
        return None
    
    session.expires_at = datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    _SESSION_STORE[session_id] = session
    
    return session


# =============================================================================
# FASTAPI DEPENDENCY
# All authenticated endpoints MUST use this dependency
# =============================================================================

from fastapi import Header, HTTPException, Depends


async def get_current_session(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    authorization: Optional[str] = Header(None),
) -> Session:
    """
    FastAPI dependency to get the current session.
    
    Usage in endpoints:
        @router.get("/protected")
        async def protected_endpoint(session: Session = Depends(get_current_session)):
            ...
    
    IMPORTANT: All authenticated endpoints MUST use this dependency.
    Do NOT implement custom authentication logic.
    """
    session_id = None
    
    # Try X-Session-ID header first (preferred for API clients)
    if x_session_id:
        session_id = x_session_id
    # Fall back to Authorization header (Bearer token format)
    elif authorization and authorization.startswith("Bearer "):
        session_id = authorization[7:]  # Remove "Bearer " prefix
    
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Missing session ID. Include X-Session-ID header or Authorization: Bearer <session_id>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    session = get_session(session_id)
    
    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Refresh session on each request
    refresh_session(session_id)
    
    return session


def require_admin(session: Session = Depends(get_current_session)) -> Session:
    """
    FastAPI dependency that requires admin privileges.
    
    Usage:
        @router.delete("/admin-only")
        async def admin_endpoint(session: Session = Depends(require_admin)):
            ...
    """
    if not session.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required",
        )
    return session


# =============================================================================
# INTERNAL HELPER FUNCTIONS
# =============================================================================

def _generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    # Using secrets module for security (not random)
    token = secrets.token_hex(SESSION_TOKEN_LENGTH // 2)
    return token


def _cleanup_user_sessions(user_id: str) -> None:
    """
    Clean up old sessions for a user.
    
    Enforces MAX_SESSIONS_PER_USER limit.
    """
    user_sessions = [
        (sid, s) for sid, s in _SESSION_STORE.items() 
        if s.user_id == user_id
    ]
    
    # Sort by creation time (oldest first)
    user_sessions.sort(key=lambda x: x[1].created_at)
    
    # Remove oldest sessions if over limit
    while len(user_sessions) >= MAX_SESSIONS_PER_USER:
        old_session_id, _ = user_sessions.pop(0)
        invalidate_session(old_session_id)
        logger.info(f"Removed old session for user {user_id}")


def _hash_session_id(session_id: str) -> str:
    """
    Hash a session ID for logging purposes.
    
    SECURITY: Never log full session IDs.
    """
    return hashlib.sha256(session_id.encode()).hexdigest()[:16]


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# These exist for backward compatibility with older services
# DO NOT USE in new code
# =============================================================================

def validate_session_token(token: str) -> bool:
    """
    DEPRECATED: Use get_session() instead.
    
    This function exists for backward compatibility with the legacy
    batch processing system (BatchProcessor v1.x).
    
    Scheduled for removal: 2026-Q2
    """
    logger.warning("DEPRECATED: validate_session_token() called")
    session = get_session(token)
    return session is not None


def get_user_from_session(token: str) -> Optional[dict]:
    """
    DEPRECATED: Use get_session() instead.
    
    Returns user info dict for backward compatibility.
    New code should use the Session object directly.
    
    Scheduled for removal: 2026-Q2
    """
    logger.warning("DEPRECATED: get_user_from_session() called")
    session = get_session(token)
    if session is None:
        return None
    return {
        "user_id": session.user_id,
        "email": session.user_email,
        "is_admin": session.is_admin,
    }
