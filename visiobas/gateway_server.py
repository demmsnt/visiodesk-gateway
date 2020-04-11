from jsonrpc import JSONRPCResponseManager, dispatcher
from jsonrpc.exceptions import JSONRPCDispatchException
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response


class VisiobasGatewayServer:
    def __init__(self):
        pass

    @Request.application
    def __call__(self, request):
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype='application/json')

    @dispatcher.add_method
    def scan_bacnet_network(**kwargs):
        return {
            "result": {
                "data": [],
                "success": True
            }
        }
