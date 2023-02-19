import logging
import json
import os
import re

from handlers.base import BaseHandler
from handlers.utils import require_login
from orm.models import Player
from settings import tornado_settings, smtp_settings, pass_reply, admin_email
from email.mime.text import MIMEText

import handlers.mail as mail


logger = logging.getLogger('whitelist.' + __name__)


class ReviewPageHandle(BaseHandler):
    @require_login
    async def get(self):
        players = await Player.filter(passed=0)
        await self.render("review.html", players=players, handler=self)


class ReviewResultHandle(BaseHandler):
    @require_login
    async def post(self):
        id = int(self.get_argument("id"))
        result = int(self.get_argument("result"))
        reason = str(self.get_argument("reason"))
        assert result in [1, 2]
        user = self.get_current_user()
        username = user.name
        player = await Player.get(id=id)
        if result==1:
            cmd = "screen -S Velocity -p 0 -X stuff \"buc whitelist add "+ player.minecraft_id+"\\r\""
            os.system(cmd)
            try:
                output = str(os.popen("cat ~/screenlog.0|tail -n 3",'r').readlines())
            except:
                self.write(dict(message="open log error!"))
            if re.search('Added\s[a-zA-Z0-9_-]+\s\(.*\)\sto\swhitelist',output)!=None:
                player.passed = result
                player.operator = username
                await player.save()
                mailserver = mail.mailSender(smtp_settings['mail_host'], smtp_settings['mail_user'], smtp_settings['mail_pass'])
                title = "IMYVM 竹萌 白名单申请成功通知"
                message = pass_reply.replace('minecraft_id', player.minecraft_id)
                # msg = MIMEText(message, 'plain', 'utf-8')
                msg = MIMEText(message, 'html')
                mailserver.sendmail(player.email, msg, title, player.minecraft_id)
                message = player.minecraft_id+"的白名单申请已成功，现发此函以通知"+"<br>"+"操作人为："+player.operator
                msg = MIMEText(message, "html")
                mailserver.sendmail(admin_email['address'], msg, player.minecraft_id+"白名单申请失败通知", admin_email['name'])
            else:
                self.write(dict(message="operate failed"))
        elif result==2:
            cmd = "screen -S Velocity -p 0 -X stuff \"buc whitelist remove "+ player.minecraft_id+"\\r\""
            os.system(cmd)
            mailserver = mail.mailSender(smtp_settings['mail_host'], smtp_settings['mail_user'], smtp_settings['mail_pass'])
            title = "IMYVM 竹萌 白名单申请失败通知"
            message = "很遗憾的通知您，您的白名单申请已被拒绝，以下是拒绝原因，请查看后重新申请"+"<br>"+"拒绝原因："+ reason
            # msg = MIMEText(message, 'plain', 'utf-8')
            msg = MIMEText(message, 'html')
            mailserver.sendmail(player.email, msg, title, player.minecraft_id)
            message = player.minecraft_id+"的白名单申请已被拒绝，现发此函以通知"+"<br>"+"操作人为："+player.operator+"<br>"+"原因为"+reason
            msg = MIMEText(message, "html")
            mailserver.sendmail(admin_email['address'], msg, player.minecraft_id+"白名单申请失败通知", admin_email['name'])

'''
class ReviewPieceHandle(BaseHandler):
    async def get(self, uid):
        player = await Player.get(id=int(uid))

        await self.render("review_piece.html", player=player, handler=self)
'''
