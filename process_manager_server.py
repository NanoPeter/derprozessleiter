from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from process_monitor import ProcessMonitor

import json
from queue import Queue, Empty

from typing import List

from threading import Thread, Event

from time import sleep

import signal

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/process-manager', )

class ProcessManager(Thread):
    def __init__(self, path_to_config_file: str):
        super().__init__()

        self._configuration_file_path = path_to_config_file

        with open(path_to_config_file, 'r', encoding='utf-8') as fil:
            self._configuration = json.load(fil)

        self._queue = Queue()
        self._should_stop = Event()
    
        self._process_monitors = dict()

        for process_name, parameters in self._configuration.items():
            pm = self._start_process_from_config(process_name, parameters)
            self._process_monitors[process_name] = pm

    def _start_process_from_config(self, process_name: str, parameters):
        return ProcessMonitor(  self._queue,
                                process_name,
                                parameters['command'],
                                parameters['cwd'])

    def save_current_configuration(self):
        with open(self._configuration_file_path, 'w', encoding='utf-8') as fil:
            json.dump(self._configuration, fil)

    def delete_process(self, process_name: str):
        if process_name in self._process_monitors:
            pm = self._process_monitors[process_name]
            pm.kill()
            del self._configuration[process_name]

    def add_new_process(self, process_name: str, parameters) -> bool:
        #TODO: check if parameters contains valid keys

        if process_name in self._process_monitors:
            return False

        self._configuration[process_name]

    def list_processes(self) -> List[str]:
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
        return True

    def terminate(self, process_name: str):
        if process_name in self._process_monitors:
            pm = self._process_monitors[process_name]
            pm.terminate()

        return True

    def restart_process(self, process_name: str):
        if process_name in self._process_monitors:
            pm = self._process_monitors[process_name]
            pm.restart_gracefully()
        return True

    def shutdown(self):
        self._should_stop.set()
        sleep(1)
        for name, process in self._process_monitors.items():
            print('Terminate', name)
            process.terminate()

            if not process.wait(10):
                print(name, 'does not terminate, trying to kill it')
                process.kill()

    def run(self):
        while not self._should_stop.is_set():
            try:
                process_exit_message = self._queue.get(timeout=1) 
                self._handle_process_exit(process_exit_message)
            except Empty:
                pass

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

        def shutdown(signal_number, frame):
            manager.shutdown()
            shutdown_thread = Thread(target=server.server_close)
            print('shutting down server')
            shutdown_thread.start()
            shutdown_thread.join()
            print('server has been shut down.')
            exit(0)


        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        server.register_function(manager.list_processes)
        server.register_function(manager.get_metrics)
        server.register_function(manager.start_process)
        server.register_function(manager.kill)
        server.register_function(manager.terminate)
        server.register_function(manager.restart_process)

        server.serve_forever()