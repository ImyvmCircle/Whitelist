import json
import tornado.httpclient

http_client = tornado.httpclient.AsyncHTTPClient()


async def post(url, body):
    r = await http_client.fetch(tornado.httpclient.HTTPRequest(url, "POST", body=body))
    return json.loads(r.body)


async def get(url):
    r = await http_client.fetch(tornado.httpclient.HTTPRequest(url))
    return json.loads(r.body)
