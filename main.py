from random import randint
from pynput.keyboard import Listener
import threading
from time import process_time, sleep
from os import system, name

# Import games #
import snake
import tetris
import pong
import breakout

SCREEN_WIDTH = 70
SCREEN_HEIGHT = 35


clearScreen = lambda : system('cls' if name == 'nt' else 'clear')
centerTo = lambda line, width : "{0:^{1}}".format(line, width)


class Flash:
    def __init__(self):
        self.x = randint(0,SCREEN_WIDTH-1)
        self.y = randint(0,SCREEN_HEIGHT-1)
        self.coord = (self.x, self.y)
        self.total_life = 9
        self.life = self.total_life




### KEYS ###

class PressKey:
    def __init__(self, kind):
        if kind == "up":
            self.keys = ["Key.up","\'w\'", "\'W\'"]
        elif kind == "down":
            self.keys = ["Key.down","\'s\'", "\'S\'"]
        elif kind == "right":
            self.keys = ["Key.right","\'d\'", "\'D\'"]
        elif kind == "left":
            self.keys = ["Key.left","\'a\'", "\'A\'"]
        elif kind == "space":
            self.keys = ["Key.space"]
        elif kind == "esc":
            self.keys = ["Key.esc"]
        else:
            raise Exception("Tried to create a key with an invalid type")
        
        self.pressed = False
        

keys = {
    "up":       PressKey("up"),
    "down":     PressKey("down"),
    "space":    PressKey("space"),
    "esc":      PressKey("esc")
}


def on_key_press(key):
    for keytype in keys:
        if str(key) in keys[keytype].keys:
            keys[keytype].pressed = True
    
        
def on_key_release(key):
    for keytype in keys:
        if str(key) in keys[keytype].keys and not (keytype == "space" or keytype == "esc"):
            keys[keytype].pressed = False


def keyInputs():
    # Collect events until released
    with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

keyboardT = threading.Thread(target=keyInputs, args=(), daemon = True)
keyboardT.start()                




def printOnWindow(lines, width):
    frame = ""
    for i in range(max(0, (SCREEN_HEIGHT-len(lines)) // 2 )):
        frame += "\n"
    for line in lines:
        for i in range((SCREEN_WIDTH-width)//2):
            frame += "  "
        frame += line
        frame += "\n"
        
    clearScreen()
    print(frame)
    
    
    
    
def printMenu(keypos, games, flashes):
    
    menuIcon = [
        "   ______                    _             __   ___                        __   ",
        "  /_  __/__  _________ ___  (_)___  ____ _/ /  /   |  ______________ _____/ /__ ",
        "   / / / _ \/ ___/ __ `__ \/ / __ \/ __ `/ /  / /| | / ___/ ___/ __ `/ __  / _ \\",
        "  / / /  __/ /  / / / / / / / / / / /_/ / /  / ___ |/ /  / /__/ /_/ / /_/ /  __/",
        " /_/  \___/_/  /_/ /_/ /_/_/_/ /_/\__,_/_/  /_/  |_/_/   \___/\__,_/\__,_/\___/ "
    ]
    
    def checkSpace(flashes, x, y):
        isFlash = False
        for flash in flashes:
            if (x, y) == flash.coord:
                isFlash = True
                if flash.life > flash.total_life / 3 * 2:
                    char = "<>"
                elif flash.life > flash.total_life / 3:
                    char = "><"
                else:
                    char = "]["
        if not isFlash:
            char = "  "
        return char
    
    def centerWithFlashes(toCenter, flashes, width, y):
        line = ""
        for x in range(int((width - (len(toCenter)/2))/2)):
            line += checkSpace(flashes, x, y)
        line += toCenter
        for x in range(int((width - (len(toCenter)/2))/2)):
            line += checkSpace(flashes, x + int((width - (len(toCenter)/2))/2) + len(line) -1, y)
        return line
        
    
    frame = "+"
    for x in range(SCREEN_WIDTH):
        frame += "--"
    frame += "+\n"
    
    totalY = 0
    
    for y in range((SCREEN_HEIGHT-len(menuIcon))//2 - 3):
        totalY += 1
        frame += "|"
        for x in range(SCREEN_WIDTH):
            frame += checkSpace(flashes, x, y)
        frame += "|\n"
    
    for line in menuIcon:
        totalY += 1
        frame += "|" + centerWithFlashes(line, flashes, SCREEN_WIDTH, totalY) + "|\n"
        
    
    for pos, game in enumerate(games):
        totalY += 1
        frame += "|" + centerWithFlashes("", flashes, SCREEN_WIDTH, totalY) + "|\n|"
        totalY += 1
        if keypos == pos:
            frame += centerWithFlashes(f" > {game}  ", flashes, SCREEN_WIDTH, totalY)
        else:
            frame += centerWithFlashes(f"   {game}  ", flashes, SCREEN_WIDTH, totalY)
        frame += "|\n"
        
        
    
    for y in range((SCREEN_HEIGHT-len(menuIcon))//2 + 3 - (len(games) * 2)):
        totalY += 1
        frame += "|"
        for x in range(SCREEN_WIDTH):
            frame += checkSpace(flashes, x, totalY)
        frame += "|\n"
        
        
    frame += "+"
    for x in range(SCREEN_WIDTH):
        frame += "--"
    frame += "+"
    
    clearScreen()
    print(frame)

            
    


keypos = 0
games = [" Snake ", " Tetris", "  Pong ", "  Breakout "]

flashes = []

while True:
    tick_start = process_time()
    
    if keys["up"].pressed:
        keypos -= 1
        keys["up"].pressed = False
    if keys["down"].pressed:
        keypos += 1
        keys["down"].pressed = False
    
    if keypos >= len(games):
        keypos = 0
    elif keypos < 0:
        keypos = len(games) - 1
        
        
    # Update flashes
    for i in range(0):
        flashes.append(Flash())
        
    next_flashes = flashes
    for i, flash in enumerate(flashes):
        flash.life -= 1
        if flash.life < 0:
            next_flashes[i] = None
    flashes = []
    for flash in next_flashes:
        if flash != None:
            flashes.append(flash)
            
    if keys["space"].pressed:
        keys["space"].pressed = False
        if keypos == 0:
            snake.run()
        elif keypos == 1:
            tetris.run()
        elif keypos == 2:
            pong.run()
        elif keypos == 3:
            breakout.run()
        tick_start = process_time()
        keys["esc"].pressed = False
        print("stopping")
        
            
            
        
        
    printMenu(keypos, games, flashes)
    
    
    sleep(0.1 - (process_time() - tick_start))

