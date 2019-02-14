from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from process_monitor import ProcessMonitor

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/process-manager', )

class ProcessManager:
    

def list_processes():
    return ['process1', 'process2', 'process3']


def start_process(name):

    
if __name__ == '__main__':
    with SimpleXMLRPCServer(('0.0.0.0', 8000), requestHandler=RequestHandler) as server:
        server.register_function(list_processes)

        server.serve_forever()