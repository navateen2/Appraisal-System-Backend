import contextvars

_current_user_context: contextvars.ContextVar[int | None] = contextvars.ContextVar("current_user_id", default=None)


def set_current_user_id(user_id: int | None) -> contextvars.Token:
    return _current_user_context.set(user_id)


def get_current_user_id() -> int | None:
    return _current_user_context.get()


def reset_current_user_id(token: contextvars.Token) -> None:
    _current_user_context.reset(token)
