import functools
import hashlib
import secrets
import time
import tortoise.exceptions
from tornado.web import RequestHandler
from typing import Optional, Union, Dict

import handlers.base
from orm import User
from settings import secret_tokens, session_max_age
from handlers.utils import APILoginNeeded, APIPermissionError


class SessionStorage:
    class Item:
        expires: int
        value: any

        def __init__(self, expires: int, value):
            self.expires = expires
            self.value = value

    def __init__(self):
        self.storage: Dict[str, SessionStorage.Item] = {}
        self.last_maintain = 0

    def _periodic_maintain(self):
        if time.time() > self.last_maintain + 2 * session_max_age:
            self.storage = {k: v for (k, v) in self.storage.items()
                            if time.time() < v.expires}
            self.last_maintain = time.time()

    def set(self, key: str, value, age: int = session_max_age):
        self._periodic_maintain()
        self.storage[key] = SessionStorage.Item(int(time.time() + age), value)

    def get(self, key: str) -> Optional[any]:
        self._periodic_maintain()
        item = self.storage.get(key)
        if item is None:
            return None
        if time.time() > item.expires:
            del self.storage[key]
            return None
        return item.value

    def delete(self, key: str):
        self._periodic_maintain()
        try:
            del self.storage[key]
        except KeyError:
            pass


session_storage = SessionStorage()


def set_session(handler: RequestHandler, user: User,
                expires: int = session_max_age):
    token = secrets.token_hex(32)
    session_storage.set(token, user, expires)
    handler.set_cookie("auth", token)


def get_session_user(handler: RequestHandler) -> Optional[User]:
    token = handler.get_cookie("auth")
    if token is None:
        return None
    user = session_storage.get(token)
    return user


def require_login(func):
    @functools.wraps(func)
    async def login_checker(self: handlers.base.BaseHandler, *args, **kwargs):
        user = get_session_user(self)
        if user is None:
            if "text/html" in self.request.headers.get('Accept', ""):
                self.redirect("/login")
            else:
                raise APILoginNeeded("You must login to view this page")
        else:
            await func(self, *args, **kwargs)

    return login_checker


def require_admin(func):
    @functools.wraps(func)
    async def checker(self, *args, **kwargs):
        user = get_session_user(self)
        is_admin = user is not None and bool(user.is_admin)

        if not is_admin:
            if "text/html" in self.request.headers.get('Accept', ""):
                self.write_error(403, reason='Access denied')
            else:
                raise APIPermissionError("You must be admin to view this page")
        else:
            await func(self, *args, **kwargs)

    return checker
