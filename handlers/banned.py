import logging
import json
import os

from handlers.base import BaseHandler
from handlers.utils import require_login
from orm.models import Player
from settings import tornado_settings, smtp_settings, pass_reply
from email.mime.text import MIMEText

import handlers.mail as mail


logger = logging.getLogger('whitelist.' + __name__)


class BannedPageHandle(BaseHandler):
    @require_login
    async def get(self):
        players = await Player.filter(passed=3)
        await self.render("banned.html", players=players, handler=self)
