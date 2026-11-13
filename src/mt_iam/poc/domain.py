"""Synthetic local behavioral models for POCs only; not production authentication.

No real credentials, passwords, JWT tokens, sensitive staff records or OAuth protocol
implementation is used here. Models are useful to falsify domain-state hypotheses.
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import Lock

class InvalidTransition(ValueError):
    pass

class AccountState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"
    DEPROVISIONED = "deprovisioned"

_ALLOWED = {
    AccountState.PENDING: {AccountState.ACTIVE, AccountState.DISABLED},
    AccountState.ACTIVE: {AccountState.SUSPENDED, AccountState.DISABLED, AccountState.DEPROVISIONED},
    AccountState.SUSPENDED: {AccountState.ACTIVE, AccountState.DISABLED, AccountState.DEPROVISIONED},
    AccountState.DISABLED: {AccountState.ACTIVE, AccountState.DEPROVISIONED},
    AccountState.DEPROVISIONED: set(),
}

@dataclass
class Account:
    subject: str
    org: str
    state: AccountState = AccountState.PENDING
    history: list[str] = field(default_factory=list)

    def transition(self, destination: AccountState, *, actor: str, reason: str) -> None:
        if not actor or not reason or destination not in _ALLOWED[self.state]:
            raise InvalidTransition("Transition requires valid state, actor and reason")
        self.history.append(f"{self.state.value}->{destination.value}:{actor}:{reason}")
        self.state = destination

@dataclass
class Session:
    subject: str
    expires_at: datetime
    revoked: bool = False

    def valid(self, now: datetime) -> bool:
        return not self.revoked and now < self.expires_at

    def revoke(self) -> None:
        self.revoked = True

class ScopedDirectory:
    def __init__(self) -> None:
        self._people: dict[str, Account] = {}

    def enroll(self, account: Account) -> None:
        if account.subject in self._people:
            raise ValueError("duplicate identity")
        self._people[account.subject] = account

    def get(self, subject: str, org_scope: str) -> Account | None:
        person = self._people.get(subject)
        return person if person and person.org == org_scope else None

@dataclass(frozen=True)
class Client:
    client_id: str
    redirect_uris: tuple[str, ...]
    approved: bool = False

    def allows_redirect(self, uri: str) -> bool:
        return self.approved and uri in self.redirect_uris

class LocalApplication:
    def __init__(self, members: set[str]) -> None:
        self.members = members

    def admit(self, verified_subject: str) -> bool:
        return verified_subject in self.members

class BoundedExecutor:
    """Synchronous simulation of admission. Production needs async/load tests."""
    def __init__(self, limit: int) -> None:
        if limit < 1:
            raise ValueError("limit must be positive")
        self._capacity = limit
        self._active = 0
        self._lock = Lock()

    def run(self, fn: Callable[[], object]) -> object:
        with self._lock:
            if self._active >= self._capacity:
                raise RuntimeError("backpressure")
            self._active += 1
        try:
            return fn()
        finally:
            with self._lock:
                self._active -= 1

    @property
    def active(self) -> int:
        with self._lock:
            return self._active


def sample_session(subject: str = "synthetic") -> Session:
    return Session(subject=subject, expires_at=datetime.now(timezone.utc) + timedelta(minutes=5))
