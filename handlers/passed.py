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


class PassedPageHandle(BaseHandler):
    @require_login
    async def get(self):
        players = await Player.filter(passed=1)
        await self.render("passed.html", players=players, handler=self)


class PassedResultHandle(BaseHandler):
    @require_login
    async def post(self):
        id = int(self.get_argument("id"))
        result = int(self.get_argument("result"))
        reason = str(self.get_argument("reason"))
        assert result in [3]

        player = await Player.get(id=id)
        player.passed = result
        await player.save()
        if reason:
            cmd = "screen -S BC -p 0 -X stuff \"buc ban "+ player.minecraft_id+" "+reason+"\\r\""
        else:
            cmd = "screen -S BC -p 0 -X stuff \"buc ban "+ player.minecraft_id+"\\r\""
        os.system(cmd)