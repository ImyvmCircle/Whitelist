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

        user = await User.create(name=username, password=sha.hexdigest(), is_admin=True)

        set_session(self, user)
        self.write(dict(message="Success", seed=user.seed_2fa))


class CreateUserHandler(BaseHandler):
    @require_admin
    async def post(self):
        # self.write(dict(message="Success", seed="12345555"))
        # return

        username = self.get_json_argument('username')
        password = self.get_json_argument('password')

        logger.debug(f"User register: {username}")
        sha = hashlib.sha512(f"{username}{password}{pepper}".encode())

        user = await User.create(name=username, password=sha.hexdigest(), is_admin=False)

        self.write(dict(message="Success", seed=user.seed_2fa))


class PasswordChangeHandler(BaseHandler):
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
        if new_sha == old_sha:
            raise APIError("auth:password", 200, "Please do not enter the same password")
        user.password = new_sha.hexdigest()
        await user.save(force_update=True)

        set_session(self, user)
        self.write(dict(message="Success"))


class LoginHandler(BaseHandler):
    async def get(self):
        await self.render("login.html", handler=self)

    async def post(self):
        name = self.get_json_argument('username')
        password = self.get_json_argument('password')
        otp = self.get_json_argument('otp')
        ipaddress = self.request.remote_ip

        try:
            user = await User.get(name=name)
            enableotp = user.enableotp  #This is on by default
            if ipaddress != user.ip:
                enableotp = "on"
        except tortoise.exceptions.DoesNotExist:
            raise APIError("auth:username", 200, f"No such username: {name}")

        sha = hashlib.sha512(f"{name}{password}{pepper}".encode())
        if user.password != sha.hexdigest():
            raise APIError("auth:password", 200,
                           "Username or password is incorrect")

        totp = pyotp.TOTP(user.seed_2fa)
        if (not totp.verify(otp, valid_window=1)) and (enableotp != "hidden"):
            raise APIError("auth:otp", 200, "Two factor code incorrect")
        if user.ip != ipaddress:
            user.ip = ipaddress
            await user.save(force_update=True)

        set_session(self, user)
        self.write(dict(message="Success"))


class UserManagerHandler(BaseHandler):
    async def get(self):
        user = self.get_current_user()
        enableotp = user.enableotp 
        print(enableotp)
        if enableotp == "hidden":
            flag="False"
            selected="mdc-switch mdc-switch--unselected"
        else:
            flag="True"
            selected="mdc-switch mdc-switch--selected"
        print(flag+selected)
        await self.render("user_manager.html", handler=self,flag=flag,selected=selected)
    async def post(self):
        user = self.get_current_user()
        enableotp = self.get_json_argument('enableotp')
        if enableotp == "true":
            new_enableotp = "hidden"
        else:
            new_enableotp = "on"
        if user.enableotp != new_enableotp:
            user.enableotp = new_enableotp
            await user.save(force_update=True)

        self.write(dict(message="Success"))


class AdminManagerHandler(BaseHandler):
    @require_admin
    async def get(self):
        users = await User.all()
        await self.render("adminmanager.html", users=users, handler=self)

    @require_admin
    async def post(self):
        self.write(dict(message="Success", seed="12345555"))
        return

class AdminDelUserHandler(BaseHandler):
    @require_admin
    async def post(self):
        id = int(self.get_argument("id"))
        username = await User.get(id=id)
        await username.delete()

class Check2FA(BaseHandler):
    async def post(self):
        name =self.get_json_argument('username')
        ipaddress = self.request.remote_ip
        print(ipaddress)
        try:
            user = await User.get(name=name)
        except:
            self.write(dict(message=True))
        enableotp_settings = user.enableotp
        if enableotp_settings == "on" or ipaddress != user.ip:
            self.write(dict(message=False))
        else:
            self.write(dict(message=True))

