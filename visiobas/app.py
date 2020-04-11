from jsonrpc import JSONRPCResponseManager, dispatcher
from jsonrpc.exceptions import JSONRPCDispatchException
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from visiobas.gateway_server import VisiobasGatewayServer

if __name__ == '__main__':
    server = VisiobasGatewayServer()
    run_simple('localhost', 10000, server)
