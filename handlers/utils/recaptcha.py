from handlers.utils import request
import logging
import math
import time
import urllib.parse
from collections import defaultdict

from settings import secret_tokens, flexible_recaptcha_settings


logger = logging.getLogger('whitelist.' + __name__)
last_clean_time = 0
ip_request_count = defaultdict(int)


async def verify_recaptcha(token: str, action: str, min_score: float):
    verify_result = await request.post(
        "https://www.recaptcha.net/recaptcha/api/siteverify",
        urllib.parse.urlencode({
            'secret': secret_tokens['recaptcha_key'],
            'response': token
        }))

    logger.debug(f"reCaptcha verify result: {verify_result}")

    if not verify_result['success'] or verify_result['action'] != action:
        return False
    return verify_result['score'] >= min_score


async def verify_recaptcha_with_dynamic_score(token: str, action: str, ip: str):
    global last_clean_time

    if time.time() > last_clean_time + flexible_recaptcha_settings['clean_interval']:
        logger.debug(f"Clean IP request counter")
        ip_request_count.clear()
        last_clean_time = time.time()

    ip_request_count[ip] += 1
    score = math.atan(ip_request_count.get(ip) * flexible_recaptcha_settings['arctan_x']) * 2 / math.pi
    logger.debug(f"Verify reCaptcha with score {score}")

    return await verify_recaptcha(token, action, score)
