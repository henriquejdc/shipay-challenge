from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Optional

from application.settings import Settings


@dataclass(frozen=True)
class PasswordResult:
    hashed_password: str
    auto_generated: bool


class PasswordService:
    @staticmethod
    def _generate_password() -> str:
        return secrets.token_urlsafe(Settings.GENERATED_PASSWORD_LENGTH)

    @classmethod
    def build_password(cls, candidate: Optional[str]) -> PasswordResult:
        raw_password = candidate if candidate else cls._generate_password()
        salt = secrets.token_bytes(Settings.PASSWORD_SALT_BYTES)
        digest = hashlib.pbkdf2_hmac("sha256", raw_password.encode("utf-8"), salt, Settings.PASSWORD_ITERATIONS)
        stored = f"pbkdf2_sha256${salt.hex()}${digest.hex()}"
        return PasswordResult(hashed_password=stored, auto_generated=not bool(candidate))

