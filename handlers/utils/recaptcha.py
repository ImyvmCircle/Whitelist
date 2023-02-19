from handlers.utils import request
import logging
import urllib.parse
from collections import defaultdict

from settings import secret_tokens


logger = logging.getLogger('whitelist.' + __name__)
last_clean_time = 0
ip_request_count = defaultdict(int)


async def verify_recaptcha(token: str, type: str, ip: str):
    verify_result = await request.post(
        "https://www.recaptcha.net/recaptcha/api/siteverify",
        urllib.parse.urlencode({
            'secret': secret_tokens['recaptcha_key'],
            'response': token,
            'remoteip': ip
        }))

    logger.debug(f"reCaptcha verify result: {verify_result}")

    return verify_result['success']
