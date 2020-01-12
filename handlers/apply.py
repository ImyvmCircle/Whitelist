import datetime
import json
import logging
import re
import tornado.httpclient
import tortoise

from handlers.base import BaseHandler
from handlers.utils.recaptcha import verify_recaptcha_with_dynamic_score
from orm.models import Player
from settings import smtp_settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import handlers.mail as mail


logger = logging.getLogger('whitelist.' + __name__)

err_1048_re = re.compile(r"Column '([a-zA-Z_]+)' cannot be null")


def parse_year_month(date):
    y, m = date.split('-')
    return int(y) * 12 + (int(m) - 1)


class ApplyHandle(BaseHandler):
    http_client = tornado.httpclient.AsyncHTTPClient()

    async def get(self):
        meta_data = [
            {
                "key": "minecraft_id",
                "name": "您的正版 Minecraft ID",
                "type": "text",
                "required": True,
                "message": "请输入您的 Minecraft ID"
            },
            {
                "key": "email",
                "name": "邮箱地址",
                "description": "申请结果将发送到您的电子邮箱",
                "type": "text",
                "validate": r"^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$",
                "required": True,
                "message": "请输入您的邮箱"
            },
            {
                "key": "nickname",
                "name": "昵称",
                "description": "希望大家如何称呼您",
                "type": "text"
            },
            {
                "key": "introduction",
                "name": "一句话介绍你自己",
                "description": "如您通过审核此项将显示给其他玩家",
                "type": "text"
            },
            {
                "key": "gender",
                "name": "性别",
                "options": [
                    "男",
                    "女",
                    "保密"
                ],
                "type": "radio",
                "required": True
            },
            {
                "key": "motto",
                "name": "座右铭",
                "description": "如您通过审核此项将显示给其他玩家",
                "type": "text"
            },
            {
                "key": "age",
                "name": "年龄",
                "type": "text",
                "validate": "^\d{1,3}$",
                "required": True
            },
            {
                "key": "things_todo",
                "name": "来竹萌希望体验的内容或想做的事情？",
                "options": [
                    "原汁原味的生存功能",
                    "更丰富的有现实代入感的生存",
                    "成为一名竹萌生存建筑师",
                    "建立自己的村庄",
                    "玩转红石机械",
                    "聊天吹水，交交朋友",
                    "创造世界开开脑洞",
                    "竹萌独创的各种小游戏",
                    "空岛生存",
                    "录制视频或直播"
                ],
                "has_other": True,
                "type": "multiselect",
                "required": True
            },
            {
                "key": "minecraft_join_time",
                "name": "接触 Minecraft 的时间",
                "type": "text",
                "validate": r"^20\d{2}-(0|1)?\d$",
                "placeholder": "YYYY-MM",
                "required": True
            },
            {
                "key": "good_at",
                "name": "擅长的事情？",
                "options": [
                    "生存",
                    "建筑",
                    "红石",
                    "聊天",
                    "唱歌",
                    "学习",
                    "英文",
                    "编辑视频",
                    "组织活动",
                    "规划管理"
                ],
                "has_other": True,
                "type": "multiselect",
                "required": True
            },
            {
                "key": "resident",
                "name": "是否愿意常驻竹萌？",
                "type": "radio",
                "options": ["是", "否"],
                "required": True
            },
            {
                "key": "want_donate",
                "name": "是否有能力或愿意捐赠服务器？",
                "type": "radio",
                "options": ["是", "否"],
                "required": True
            },
            {
                "key": "apply_more",
                "name": "是否同时在申请其他服务器白名单？",
                "type": "radio",
                "options": ["是", "否"],
                "required": True
            },
            {
                "key": "is_bad",
                "name": "是否有被封禁的经历？",
                "description": "该题不影响白名单审核",
                "type": "radio",
                "options": ["是", "否"],
                "required": True
            },
            {
                "key": "manage_exp",
                "name": "是否有其他服务器管理经验？",
                "type": "radio",
                "options": ["是", "否"],
                "required": True
            },
            {
                "key": "referrer_person",
                "name": "推荐人",
                "type": "text"
            },
            {
                "key": "referrer_web",
                "name": "你从哪里得知竹萌服务器的？",
                "options": [
                    "Bilibili",
                    "MCBBS",
                    "Youtube",
                    "搜索引擎"
                ],
                "type": "radio",
                "required": True,
                "has_other": True
            },
            {
                "key": "praise_post",
                "name": "是否顶帖",
                "description": "喜欢的话请帮助点赞顶帖哦 >>> <a href=\"http://www.mcbbs.net/thread-730815-1-1.html\">http://www.mcbbs.net/thread-730815-1-1.html</a> <<<",
                "type": "radio",
                "options": ["是", "否"],
                "required": True
            },
            {
                "key": "send_copy",
                "name": "是否发送该申请表的副本给你的邮箱？",
                "type": "radio",
                "options": ["是", "否"],
                "required": True
            }
        ]

        return await self.render("apply.html", meta=meta_data, handler=self)

    async def post(self):
        token = self.get_argument('token')
        if not (await verify_recaptcha_with_dynamic_score(token, "apply", self.request.remote_ip)):
            self.write("Invalid request")

        raw_data = json.loads(self.get_argument('data'))
        data = {}

        for field in raw_data:
            if isinstance(field['value'], list):
                field['value'] = ':;:'.join(field['value'])
            assert isinstance(field['value'], str)
            assert isinstance(field['name'], str)
            data[field['name']] = field['value']
            if field['name'] in ["resident", "want_donate", "apply_more", "is_bad", "manage_exp", "praise_post"]:
                # logger.debug(f"{field['name']} ")
                assert field['value'] in ["是", "否"]
                data[field['name']] = field['value'] == "是"

        try:
            send_copy = data['send_copy']
            data['minecraft_join_time'] = parse_year_month(data['minecraft_join_time'])
            data['birth_year'] = datetime.datetime.now().year - int(data['age'])
            del data['send_copy']
            del data['age']
        except KeyError as e:
            self.write(f"错误: {str(e)} is missing")
            return

        try:
            player = await Player.create(**data)
        except tortoise.exceptions.IntegrityError as e:
            if e.args[0].args[0] == 1048:
                # some column cannot be null
                column = err_1048_re.match(e.args[0].args[1]).groups()[0]
                self.write(f"错误: {column} is missing")
            elif e.args[0].args[0] == 1062:
                # Duplicate entry
                self.write(f"请不要提交两次哟")
            else:
                raise
            return
        self.write("Success")
        if send_copy == "是":
            mailserver = mail.mailSender(smtp_settings['mail_host'], smtp_settings['mail_user'], smtp_settings['mail_pass'])
            title = "IMYVM 竹萌 白名单申请回执"
            msg = MIMEMultipart()
            file1 = MIMEText(json.dumps(data, ensure_ascii=False), 'base64', 'utf-8')
            file1["Content-Type"] = 'application/octet-stream'
            file1["Content-Disposition"] = 'attachment; filename="apply.json"'
            msg.attach(file1)
            mailserver.sendmail(player.email, msg, title, player.minecraft_id)