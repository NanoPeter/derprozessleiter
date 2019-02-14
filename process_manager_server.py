from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from process_monitor import ProcessMonitor

import json
from queue import Queue

from threading import Thread


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/process-manager', )

class ProcessManager(Thread):
    def __init__(self, path_to_config_file: str):
        super().__init__()
        with open(path_to_config_file, 'r', encoding='utf-8') as fil:
            self._configuration = json.load(fil)

        self._queue = Queue()
    
        self._process_monitors = dict()

        for process_name, parameters in self._configuration.items():
            pm = self._start_process_from_config(process_name, parameters)
            self._process_monitors[process_name] = pm

    def _start_process_from_config(self, process_name: str, parameters):
        return ProcessMonitor(  self._queue,
                                process_name,
                                parameters['command'],
                                parameters['cwd'])

    def list_processes(self):
        return list(self._process_monitors.keys())

    def get_metrics(self, process_name: str):

        if process_name in self._process_monitors:
            pm = self._process_monitors[process_name]
            return pm.to_dict()

        return {}

    def start_process(self, process_name: str):
        if process_name in self._process_monitors:
            pm = self._process_monitors[process_name]
            pm.start()

        return 0

    def kill(self, process_name: str):
        if process_name in self._process_monitors:
            pm = self._process_monitors[process_name]
            pm.kill()

    def run(self):
        while True:
            process_exit_message = self._queue.get() 
            self._handle_process_exit(process_exit_message)

    def _handle_process_exit(self, message):
        pm = message['process_monitor']
        return_code = message['return_code']

        if return_code == 0:
            self._handle_process_on_exit(pm)
        else:
            self._handle_process_on_error(pm)

    def _handle_process_on_exit(self, pm: ProcessMonitor):
        config = self._configuration[pm.name]

        if 'on_exit' in config:
            if config['on_exit'] == 'restart':
                pm.restart()

    def _handle_process_on_error(self, pm: ProcessMonitor):
        config = self._configuration[pm.name]

        if 'on_error' in config:
            if config['on_error'] == 'restart':
                pm.restart()   


if __name__ == '__main__':
    manager = ProcessManager('processes.json')
    manager.start()

    with SimpleXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler) as server:
        server.register_function(manager.list_processes)
        server.register_function(manager.get_metrics)
        server.register_function(manager.start_process)

        server.serve_forever()