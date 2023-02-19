from handlers.apply import ApplyHandle,CheckReapply
from handlers.auth import RegisterHandler, LoginHandler, CreateUserHandler, PasswordChangeHandler,UserManagerHandler,AdminManagerHandler,Check2FA,AdminDelUserHandler
from handlers.review import ReviewPageHandle, ReviewResultHandle
from handlers.passed import PassedPageHandle, PassedResultHandle
from handlers.banned import BannedPageHandle
from handlers.refused import RefusedPageHandle
from tornado.web import StaticFileHandler

import settings

URL_ROOT = r""
API_ROOT = URL_ROOT + r"/api"


url_patterns = (
    (API_ROOT + r"/auth/register", RegisterHandler),
    (URL_ROOT + r"/checkreapply", CheckReapply),
    (URL_ROOT + r"/new_user", CreateUserHandler),
    (URL_ROOT + r"/change_pw", PasswordChangeHandler),
    (URL_ROOT + r"/manager", UserManagerHandler),
    (URL_ROOT + r"/adminmanager", AdminManagerHandler),
    (URL_ROOT + r"/adminmanager/del_user",AdminDelUserHandler),
    (URL_ROOT + r"/check2fa", Check2FA),
    (URL_ROOT + r"/login", LoginHandler),
    (URL_ROOT + r"/review", ReviewPageHandle),
    (URL_ROOT + r"/review", ReviewPageHandle),
    (URL_ROOT + r"/review/set_result", ReviewResultHandle),
    (URL_ROOT + r"/passed", PassedPageHandle),
    (URL_ROOT + r"/passed/set_result", PassedResultHandle),
    # (URL_ROOT + r"/review/render/(\d+)", ReviewPieceHandle),
    (URL_ROOT + r"/refused", RefusedPageHandle),
    (URL_ROOT + r"/banned", BannedPageHandle),
    (URL_ROOT + r"/", ApplyHandle),
    (URL_ROOT + r"/static/(.*)", StaticFileHandler, {'path': settings.tornado_settings['static_path']})
)
