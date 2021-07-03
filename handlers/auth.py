import hashlib
import logging
import pyotp
import tortoise.exceptions

from handlers.base import BaseHandler
from handlers.utils import require_login, require_admin
from orm import User
from settings import secret_tokens
from handlers.utils import set_session, APINotFoundError, APIError


logger = logging.getLogger('whitelist.' + __name__)
pepper = secret_tokens['password_pepper']


class RegisterHandler(BaseHandler):
    async def post(self):
        # only allow localhost
        if self.request.remote_ip not in ["127.0.0.1", "::1"]:
            self.write_error(403)
            return

        username = self.get_json_argument('username')
        password = self.get_json_argument('password')

        logger.debug(f"User register: {username}")
        sha = hashlib.sha512(f"{username}{password}{pepper}".encode())

        user = await User.create(name=username, password=sha.hexdigest())

        set_session(self, user)
        self.write(dict(message="Success", seed=user.seed_2fa))


class CreateUserHandler(BaseHandler):
    @require_admin
    async def get(self):
        await self.render("new_user.html")

    @require_admin
    async def post(self):
        # self.write(dict(message="Success", seed="12345555"))
        # return

        username = self.get_json_argument('username')
        password = self.get_json_argument('password')

        logger.debug(f"User register: {username}")
        sha = hashlib.sha512(f"{username}{password}{pepper}".encode())

        user = await User.create(name=username, password=sha.hexdigest(), is_admin=is_local)

        self.write(dict(message="Success", seed=user.seed_2fa))


class PasswordChangeHandler(BaseHandler):
    @require_login
    async def get(self):
        await self.render("change_pw.html")

    @require_login
    async def post(self):
        user = self.get_current_user()

        old_password = self.get_json_argument('old_password')
        new_password = self.get_json_argument('new_password')
        otp = self.get_json_argument('otp')

        old_sha = hashlib.sha512(f"{user.name}{old_password}{pepper}".encode())
        if user.password != old_sha.hexdigest():
            raise APIError("auth:password", 200, "Password is incorrect")

        totp = pyotp.TOTP(user.seed_2fa)
        if not totp.verify(otp, valid_window=1):
            raise APIError("auth:otp", 200, "Two factor code incorrect")

        new_sha = hashlib.sha512(f"{user.name}{new_password}{pepper}".encode())
        user.password = new_sha
        user.save(force_update=True)

        set_session(self, user)
        self.write(dict(message="Success"))


class LoginHandler(BaseHandler):
    async def get(self):
        await self.render("login.html", handler=self)

    async def post(self):
        name = self.get_json_argument('username')
        password = self.get_json_argument('password')
        otp = self.get_json_argument('otp')

        try:
            user = await User.get(name=name)
        except tortoise.exceptions.DoesNotExist:
            raise APIError("auth:username", 200, f"No such username: {name}")

        sha = hashlib.sha512(f"{name}{password}{pepper}".encode())
        if user.password != sha.hexdigest():
            raise APIError("auth:password", 200,
                           "Username or password is incorrect")

        totp = pyotp.TOTP(user.seed_2fa)
        if not totp.verify(otp, valid_window=1):
            raise APIError("auth:otp", 200, "Two factor code incorrect")

        set_session(self, user)
        self.write(dict(message="Success"))
