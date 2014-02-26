from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
from TwidderServer import app

http_server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
http_server.serve_forever()