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


class ReviewPageHandle(BaseHandler):
    # @require_login
    async def get(self):
        players = await Player.filter(passed=0)
        await self.render("review.html", players=players, handler=self)


class ReviewResultHandle(BaseHandler):
    @require_login
    async def post(self):
        id = int(self.get_argument("id"))
        result = int(self.get_argument("result"))
        assert result in [1, 2]

        player = await Player.get(id=id)
        player.passed = result
        await player.save()
        if result==1:
            cmd = "screen -S BC -p 0 -X stuff \"buc whitelist add "+ player.minecraft_id+"\\r\""
            os.system(cmd)
            mailserver = mail.mailSender(smtp_settings['mail_host'], smtp_settings['mail_user'], smtp_settings['mail_pass'])
            title = "IMYVM 竹萌 白名单申请成功通知"
            message = pass_reply.replace('minecraft_id', player.minecraft_id)
            msg = MIMEText(message, 'plain', 'utf-8')
            mailserver.sendmail(player.email, msg, title, player.minecraft_id)
        elif result==2:
            cmd = "screen -S BC -p 0 -X stuff \"buc whitelist remove "+ player.minecraft_id+"\\r\""
            os.system(cmd)

'''
class ReviewPieceHandle(BaseHandler):
    async def get(self, uid):
        player = await Player.get(id=int(uid))

        await self.render("review_piece.html", player=player, handler=self)
'''
