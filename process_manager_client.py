from xmlrpc.client import ServerProxy
from time import sleep


s = ServerProxy('http://localhost:8000/process-manager')


processes = s.list_processes()
s.start_process(processes[0])
sleep(1)
print(s.get_metrics(processes[0]))
