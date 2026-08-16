from application.services.password_service import PasswordService


def test_password_service_generates_password_when_missing():
    result = PasswordService.build_password(None)

    assert result.auto_generated is True
    assert result.hashed_password.startswith("pbkdf2_sha256$")


def test_password_service_hashes_provided_password():
    result = PasswordService.build_password("StrongPass123!")

    assert result.auto_generated is False
    assert result.hashed_password.startswith("pbkdf2_sha256$")

