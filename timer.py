import time
import art
from curses import wrapper

def main(stdscr):
    stdscr.clear()


    import os


    art.tprint("Test", font="rnd-large")
    startTime = time.time()
    while startTime < (startTime + 10):
        #print(term.home + term.clear + term.move_y(term.height //2))
        art.tprint(str(time.time()) ,font="clr8x8")
        time.sleep(0.01)


wrapper(main)    