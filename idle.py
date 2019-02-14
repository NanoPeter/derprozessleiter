from time import sleep

sleep(4)

with open('file.txt', 'a') as fil:
    fil.write('data\n')