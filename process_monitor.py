import psutil
from subprocess import Popen
from threading import Thread
from queue import Queue

from typing import List

class ProcessMonitor:
    def __init__(self, name: str, args: List[str], cwd: str='.'):
        self._name = name
        self._args = args 
        self._cwd = cwd
        
        self._proc = Popen(args, cwd=cwd)
        self._info = psutil.Process(self._proc.pid)

        self._host_queue = None #type: Queue

        self._thread = Thread(target=self._monitor_process)
        self._thread.start()

    def _monitor_process(self):
        print('watching process')
        return_value = self._proc.wait()
        self._fire_event(self, return_value)

    def kill(self):
        self._proc.kill()

    def register_host(self, host: Queue):
        self._host_queue = host

    def _fire_event(self, process_monitor: 'ProcessMonitor', return_code: int):
        if self._host_queue is not None:
            self._host_queue.put({  'process_monitor': process_monitor,
                                    'return_code': return_code })

    @property
    def name(self):
        return self._name

    @property 
    def args(self):
        return self._args.copy()

    @property 
    def pid(self):
        return self._proc.pid

    @property
    def current_working_directory(self):
        return self._cwd

    @property
    def cpu(self):
        if not self.running:
            return 0

        return self._info.cpu_percent(interval=None)

    @property
    def memory(self):
        if not self.running:
            return 0,
        
        usage = self._info.memory_info().rss
        if usage < 1e3:
            return usage,
        elif usage < 1e6:
            return round(usage / 1e3, 2), 'k'
        elif usage < 1e9:
            return round(usage / 1e6, 2), 'M'
        else:
            return round(usage / 1e9, 2), 'G'

    @property
    def running(self):
        return self._proc.poll() is None


if __name__ == '__main__':
    pm = ProcessMonitor('hans', ['python3', 'test_process.py'])

    from time import sleep 

    queue = Queue()

    pm.register_host(queue)

    running = True
    while running:
        while not queue.empty():
            item = queue.get()
            print(item)
            running = False
        print(pm.memory, pm.cpu)
        sleep(0.5)
