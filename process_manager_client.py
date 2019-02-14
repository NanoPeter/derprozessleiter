from xmlrpc.client import ServerProxy

s = ServerProxy('http://localhost:8000/process-manager')


print(s.list_processes())

s.shutdown()
