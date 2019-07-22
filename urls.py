from handlers.apply import ApplyHandle
from handlers.auth import RegisterHandler, LoginHandler
from handlers.review import ReviewPageHandle, ReviewResultHandle
from tornado.web import StaticFileHandler

import settings

URL_ROOT = r""
API_ROOT = URL_ROOT + r"/api"


url_patterns = (
    (API_ROOT + r"/auth/register", RegisterHandler),
    (URL_ROOT + r"/login", LoginHandler),
    (URL_ROOT + r"/review", ReviewPageHandle),
    (URL_ROOT + r"/review/set_result", ReviewResultHandle),
    # (URL_ROOT + r"/review/render/(\d+)", ReviewPieceHandle),
    (URL_ROOT + r"/apply", ApplyHandle),
    (URL_ROOT + r"/static/(.*)", StaticFileHandler, {'path': settings.tornado_settings['static_path']})
)
