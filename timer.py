import time
from curses import wrapper
import curses
from curses.textpad import Textbox, rectangle
import json
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP) #E-Stop Button (Pull to Gnd)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Start Button
class leaderboard:

    def __init__(self, datafile='playerData.txt'):
        self.datafile = datafile
        self.data = []
        with open(self.datafile, 'r') as db:
            try:
                self.data = json.load(db)
            except:
                self.data = []
    def add(self,playerData):
        playerData['timestamp'] = time.time()
        self.data.insert(0, playerData)
        self.writeback()
        return (sorted(self.data, key=lambda x: x['userTime']).index(playerData) + 1)

    def writeback(self):
        with open(self.datafile, 'w') as db:
            db.write(json.dumps(self.data))

    def top10(self):
        return sorted(self.data, key=lambda x: x['userTime'])
    
    def last10(self):
        return self.data[-10:]
    
    def delete(self, index):
        try:
            with open('deletedPlayer.txt', 'w') as d:
                d.write(str(self.data.pop(index)) +"/n")
        except:
            print('not possible')
        self.writeback()

SPACE_KEY = ord(" ")
S_KEY = ord("s")
L_KEY = ord("l")
A_KEY = ord("a")
N_KEY = ord("n")
Y_KEY = ord("y")
R_KEY = ord("r")
D_KEY = ord("d")
Q_KEY = ord("q")
P_KEY = ord("p")

timerfont = "ascii"

def timeconvert(currentTime):
    mins = int(currentTime // 60)
    secs = int(currentTime // 1)
    msecs = int(((currentTime - secs - mins)*10000) // 1)
    secs -= (mins * 60)
    return str(mins) + ":" + str(secs) + "." + str(msecs)

def timer(startTime, win):
    win.nodelay(1)
    while True:
        currentTime = time.time() - startTime
        win.addstr(1, 1, timeconvert(currentTime), curses.A_BOLD)
        win.refresh()
        stopKey = win.getch()
        if stopKey == SPACE_KEY or GPIO.input(21) == False:
            return startTime, time.time() - startTime

def main(stdscr):
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    while True:
        stdscr.clear()
        stdscr.bkgd(" ", curses.color_pair(2))
        stdscr.addstr(1,1, "MAKEGosport", curses.A_BOLD)
        stdscr.addstr(1,curses.COLS - len("Toolwall Challenge") - 2, "Toolwall Challenge", curses.A_BOLD)
        stdscr.addstr(curses.LINES - 2 ,2, "New Player (n)", curses.A_BLINK)
        stdscr.addstr(curses.LINES - 2 , curses.COLS - len("Admin Controls (a)") - 2 , "Admin Controls (a)", curses.A_DIM)
        rectangle(stdscr, 0, 0, curses.LINES - 1, curses.COLS - 2)
        stdscr.refresh()
        displayboard()


        menuKey = stdscr.getch()
        if menuKey == A_KEY:
            menuKey = stdscr.getch()
            if menuKey == P_KEY:
                stdscr.keypad(False)
                adminpanel()
                stdscr.keypad(True)
        elif menuKey == N_KEY:
            newPlayer()
        elif menuKey == 27:
            break
        else:
            curses.beep()
    
def stopWatch():
    sw_window = curses.newwin(5, 40, curses.LINES // 2 ,curses.COLS // 2 - 20)
    sw_window.bkgd(" ", curses.color_pair(3))
    sw_window.clear()
    sw_window.addstr(1,1, "0:0.0000", curses.A_BLINK)
    rectangle(sw_window, 0, 0, 2, 19)
    sw_window.addstr(3,1, "Submit(s), Reset(r), Abort(a)")
    firstRun = True
    sw_window.nodelay(1)
    while GPIO.input(20) == True:
        keyIn = sw_window.getch()
        if keyIn == SPACE_KEY:
            break
    keyIn = SPACE_KEY
    totalTime = None
    while True:
        if keyIn == SPACE_KEY:
            while GPIO.input(21) == False:
                sw_window.addstr(4,1, "Reset the E-Stop Button")
                sw_window.refresh()
            sw_window.move(4,1)
            sw_window.deleteln()
            if firstRun:
                startTime = time.time()
                firstRun = False           
            startTime, totalTime = timer(startTime, sw_window)
            while GPIO.input(21) == False:
                sw_window.addstr(4,1, "Reset the E-Stop Button")
                sw_window.refresh()
            sw_window.nodelay(0)
            keyIn = sw_window.getch()
        elif keyIn == R_KEY:
            sw_window.clear()
            sw_window.addstr(1,1, "0:0.0000")
            sw_window.addstr(3,1, "Submit(s), Reset(r), Abort(a)")
            sw_window.refresh()
            firstRun = True
            keyIn = sw_window.getch()
        elif keyIn == A_KEY:
            return None
        elif keyIn == S_KEY:
            
            return totalTime
        else:
            curses.beep()
    return totalTime
    


def newPlayer():
    playerwindow = curses.newwin(0,0)
    playerwindow.addstr(0,0, "Enter your name:")
    editwin = curses.newwin(1, 50, 2, 1)
    emailwin = curses.newwin(1,50, 6, 1)
    rectangle(playerwindow, 1,0, 3, 52)
    rectangle(playerwindow, 5,0,7,52)
    playerwindow.addstr(4,0, "Enter your email address:")
    playerwindow.refresh()
    box = Textbox(editwin)
    box.edit(enter_is_terminate)
    userName = box.gather()
    box = Textbox(emailwin)
    box.edit(enter_is_terminate)
    userEmail = box.gather()
    playerwindow.addstr(8,1, "Details are correct? (y/n)")
    confirmKey = playerwindow.getch()
    if confirmKey != Y_KEY:
        return False
    del editwin
    del playerwindow
    userTime = stopWatch()
    if userTime is not None:
        entry = {
            'userName' : userName,
            'userEmail': userEmail,
            'userTime' : userTime,
            'valid' : True
        }
        playerpos = timerboard.add(entry)
        confirmwindow = curses.newwin(curses.LINES, curses.COLS, 0, 0)
        #confirmwindow.bkgd(" ", curses.color_pair(6))
        confirmwindow.addstr(curses.LINES // 2, curses.COLS //2 - 8, "Your Position: " + str(playerpos), curses.color_pair(6))
        confirmwindow.addstr((curses.LINES // 2) + 1, curses.COLS //2 - 7, "Press any Key", curses.color_pair(6))
        confirmwindow.chgat((curses.LINES //2),0, curses.color_pair(6))
        confirmwindow.chgat((curses.LINES //2) + 1, 0, curses.color_pair(6))
        confirmwindow.getch()
        del confirmwindow
        
def displayboard():
    leaderwindow = curses.newwin(curses.LINES - 8, (curses.COLS - 8)//2, 4, 4)
    leaderwindow.bkgd(" ", curses.color_pair(1))
    displaylines = curses.LINES - 8
    displaycols = curses.COLS - 8
    maxname = displaycols // 2 - 3 - 20
    leaderwindow.addstr(0, 0, "{:^{displaycols}}".format("Top Players", displaycols=displaycols//2))
    leaderwindow.addstr(1,0, "+" + "-"* 3 + "+" + "-" * (maxname + 2) + "+" + "-" * 10 + "+")
    lbData = timerboard.top10()
    
    for i, player in enumerate(lbData):
        linestring = "| " + str(i+1) + " | " + "{:<{displaycols}}" + " | " + timeconvert(float(player['userTime'])) + " |"
        if (i*2+3) >= displaylines:
            break
        if i == 0:
            leaderwindow.addstr(i*2+2,0, linestring.format(player['userName'], displaycols=maxname), curses.A_BLINK)
        else:
            leaderwindow.addstr(i*2+2,0, linestring.format(player['userName'], displaycols=maxname))
        leaderwindow.addstr(i*2+3,0, "+" + "-"* 3 + "+" + "-" * (maxname + 2) + "+" + "-" * 10 + "+")
    
    lastwindow = curses.newwin(curses.LINES - 8, (curses.COLS - 8)//2, 4, displaycols // 2 + 4)
    lastwindow.addstr(0, 0, "{:^{displaycols}}".format("Recent Players", displaycols=displaycols//2))
    lastwindow.addstr(1, 0, "+" + "-"* 3 + "+" + "-" * (maxname + 2) + "+" + "-" * 10 + "+")
    lastwindow.bkgd(" ", curses.color_pair(1))
    lastData = timerboard.last10()
    for i, player in enumerate(lastData):
        if (i*2+3) >= displaylines:
            break
        linestring = "| " + str(i+1) + " | " + "{:<{displaycols}}" + " | " + timeconvert(float(player['userTime'])) + " |"
        lastwindow.addstr(i*2+2,0, linestring.format(player['userName'], displaycols=maxname))
        lastwindow.addstr(i*2+3,0, "+" + "-"* 3 + "+" + "-" * (maxname + 2) + "+" + "-" * 10 + "+")
    leaderwindow.refresh()
    lastwindow.refresh()
    

def enter_is_terminate(x):
    if x == 10 or x == 9:
        x = 7
    return x

def adminpanel():
    adminwin = curses.newwin(curses.LINES, curses.COLS, 0, 0)
    adminwin.bkgd(" ", curses.color_pair(4))
    adminwin.keypad(True)
    adminwin.refresh()
    maxline = curses.COLS
    maxnumber = curses.LINES
    curr_y = 0
    curr_x = 0
    while True:
        adminwin.bkgd(" ", curses.color_pair(4))
        for i, player in enumerate(timerboard.data):
            adminwin.addstr(i,0, (str(i) + " | " + str(player['userName']) + " | " + str(player['userEmail']) + " | " + timeconvert(player['userTime']))[:(maxline-2)], curses.A_NORMAL)
            adminwin.chgat(i,0, curses.color_pair(4))
            if i > (maxnumber - 3):
                break
        adminwin.addstr(maxnumber - 1,0, "Select with arrow keys, (d) to delete an entry, (q) to exit this screen")
        adminwin.move(curr_y,curr_x)
        curr_y, curr_x = adminwin.getyx()
        adminwin.chgat(curr_y, curr_x, curses.A_REVERSE)
        adminKey = adminwin.getch()
        if adminKey == curses.KEY_DOWN:
            curr_y += 1
            curr_y = min(curr_y, maxnumber - 1)
        elif adminKey == curses.KEY_UP:
            curr_y -= 1
            curr_y = max(0, curr_y)
        elif adminKey == Q_KEY or adminKey == 27:
            del adminwin
            break
        elif adminKey == D_KEY:

            adminwin.addstr(curr_y, 0, "Confirm delete this entry (y/n)")
            adminKey = adminwin.getch()
            if adminKey == Y_KEY:
                timerboard.delete(curr_y)
                adminwin.erase()

timerboard = leaderboard('playerData.txt')
wrapper(main)    