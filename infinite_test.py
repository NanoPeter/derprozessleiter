from time import sleep
import signal

class ProcessTerminator:
    kill_now = False 
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signal_number, frame):
        self.kill_now = True

if __name__ == '__main__':
    terminator = ProcessTerminator()

    while not terminator.kill_now:
        sleep(1)
        print('I am doing something')

print('end program')