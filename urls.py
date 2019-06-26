from handlers.auth import RegisterHandler, TokenCheckingHandler, LoginHandler


URL_ROOT = r"/api"


url_patterns = (
    (URL_ROOT + r"/auth/register", RegisterHandler),
    (URL_ROOT + r"/auth/check_token", TokenCheckingHandler),
    (URL_ROOT + r"/auth/login", LoginHandler),
)
