import time
from tortoise import Model, fields
import pyotp


class Player(Model):
    id = fields.IntField(pk=True)
    minecraft_id = fields.CharField(max_length=32, unique=True, index=True)  # Minecraft ID
    email = fields.CharField(max_length=128, unique=True)  # Email
    apply_time = fields.IntField(default=lambda: int(time.time()))  # 申请时间
    join_time = fields.IntField(default=0)  # 加入（竹萌）时间
    nickname = fields.CharField(max_length=64, null=True)  # 称呼
    introduction = fields.TextField(null=True)  # 介绍
    gender = fields.CharField(max_length=16)  # 性别
    motto = fields.CharField(max_length=128, null=True)  # 座右铭
    birth_year = fields.IntField()  # 出生年份（推算年龄用）
    things_todo = fields.TextField()  # "来竹萌希望体验的内容或想做的事情？"
    minecraft_join_time = fields.IntField()  # 接触 Minecraft 的时间
    good_at = fields.TextField()  # 擅长
    resident = fields.BooleanField()  # 是否常驻
    want_donate = fields.BooleanField()  # 是否愿意捐赠
    apply_more = fields.BooleanField()  # 是否在同时申请多个
    is_bad = fields.BooleanField()  # 是否曾经被 ban
    manage_exp = fields.BooleanField()  # 是否有管理经验
    referrer_person = fields.CharField(max_length=32, null=True)  # 推荐人
    referrer_web = fields.CharField(max_length=32)  # "你从哪里得知竹萌服务器的？"
    # praise_post = fields.BooleanField()  # 是否顶帖
    passed = fields.IntField(default=0, index=True)  # 审核状态：0 待审核，1 通过，2 未通过


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64, unique=True, index=True)
    password = fields.CharField(max_length=128)
    seed_2fa = fields.CharField(max_length=20, default=pyotp.random_base32)
