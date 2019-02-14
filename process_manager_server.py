from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from subprocess

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2', )


def list_processes():
    return ['process1', 'process2', 'process3']


def start_process(name):
    

with SimpleXMLRPCServer(('0.0.0.0', 8000), requestHandler=RequestHandler) as server:
    server.register_function(list_processes)

    server.serve_forever()