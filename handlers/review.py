import logging
import json

from handlers.base import BaseHandler
from handlers.utils import require_login
from orm.models import Player
from settings import tornado_settings


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


'''
class ReviewPieceHandle(BaseHandler):
    async def get(self, uid):
        player = await Player.get(id=int(uid))

        await self.render("review_piece.html", player=player, handler=self)
'''
