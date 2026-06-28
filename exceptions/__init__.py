"""Application level exceptions"""


class AppException(Exception):
    """Base for all application-level errors."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundException(AppException):
    """Requested resource does not exist."""


class ConflictException(AppException):
    """Operation conflicts with existing state (e.g. duplicate email)."""


class BadRequestException(AppException):
    """Client input is invalid in a way Pydantic validation didn't catch."""


class UnauthorizedException(AppException):
    """Invalid email or password"""


class ForbiddenException(AppException):
    """Not authorised to do this action"""
