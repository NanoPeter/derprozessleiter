import psutil
from subprocess import Popen, TimeoutExpired, PIPE
from threading import Thread, Event
from queue import Queue

from datetime import datetime

from typing import List

class ProcessMonitor:
    def __init__(self, host_queue: Queue, name: str, args: List[str], cwd: str='.'):
        self._name = name
        self._args = args 
        self._cwd = cwd

        self._number_of_starts = 0

        self._should_stop = Event()
        
        self._start(args, cwd)

        self._host_queue = host_queue

    def _monitor_process(self):
        while not self._should_stop.is_set():
            return_value = self._proc.poll()
            if return_value is None:
                try:
                    #stdout, stderr = self._proc.communicate(timeout=1)
                    print('DEBUG', self._name, self._proc.stdout.readline())
                    print('ERROR', self._name, self._proc.stderr.readline())
                except TimeoutExpired:
                    pass
            else:
                self._fire_event(self, return_value)
                self._should_stop.set()


    def kill(self):
        self._proc.kill()
        self._proc.wait()
        self._should_stop.set()

    def terminate(self):
        self._proc.terminate()
        self._should_stop.set()

    def wait(self, timeout:int):
        try:
            self._proc.wait(timeout=timeout)
        except TimeoutExpired:
            return False 
        
        return True

    def _fire_event(self, process_monitor: 'ProcessMonitor', return_code: int):
        self._host_queue.put({  'process_monitor': process_monitor,
                                'return_code': return_code })

    def _start(self, args: List[str], cwd: str):
        self._proc = Popen(args, cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self._info = psutil.Process(self._proc.pid)

        self._should_stop.clear()

        self._thread = Thread(target=self._monitor_process)
        self._thread.start()

        self._number_of_starts += 1
        self._start_timestamp = datetime.now()

    def restart_gracefully(self):
        if self.running:
            self.terminate()
            try:
                self._proc.wait(timeout=10)
            except TimeoutExpired:
                self.kill()
            
        self.start()

    def restart(self, wait = 0):
        if self.running:
            self.kill()
        self.start()

    def start(self):
        if not self.running:
            self._start(self._args, self._cwd)

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

    @property
    def number_of_starts(self):
        return self._number_of_starts

    @property
    def last_start_timestamp(self):
        return self._start_timestamp

    @property
    def uptime(self):
        return datetime.now() - self._start_timestamp

    def to_dict(self):
        return dict(name=self.name,
                    cpu=self.cpu,
                    memory=self.memory,
                    running=self.running,
                    cwd=self.current_working_directory,
                    args=self.args,
                    pid=self.pid,
                    started=self._start_timestamp.isoformat(),
                    uptime=str(self.uptime).split('.')[0],
                    number_of_starts=self.number_of_starts)

