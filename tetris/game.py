print("Loading...")
from random import randint
from time import sleep, process_time
from turtle import clearscreen
from pynput.keyboard import Listener
import threading
from os import system, name


WIDTH, HEIGHT = 14, 30

TICKSPEED = 6

clearScreen = lambda : system('cls' if name == 'nt' else 'clear')
centerTo = lambda line, width : "{0:^{1}}".format(line, width)



class Dot:
    def __init__(self, colour, coord):
        self.colour = colour
        self.coord = coord
    
    def printSelf(self):
        return f"\031[1;{self.colour}m[]"
    
class Shape:
    def __init__(self, payload, corner_coord, shapeWidth):
        self.colour, shape = payload["colour"], payload["shape"]
        self.shapeWidth = shapeWidth
        self.alive = True
        self.shape = []
        self.corner_coord = corner_coord
        for y, row in enumerate(shape):
            self.shape.append([])
            for x, point in enumerate(row):
                if point == 1:
                    self.shape[y].append(Dot(self.colour, (corner_coord[0] + x, corner_coord[1] + y)))
                else:
                    self.shape[y].append(None)
    
    def rotate(self, collisionBoard):
        backupShape = self.shape
        
        self.shape = list(zip(*self.shape))[::-1]
        
        if self.corner_coord[0] + len(self.shape[0]) > WIDTH:
            self.shape = backupShape
        else:
            cantRotate = False
            for y, row in enumerate(self.shape):
                for x, point  in enumerate(row):
                    if point != None:
                        if collisionBoard[self.corner_coord[1] + y] [self.corner_coord[0] + x] != 0:
                            cantRotate = True
                            break
            if cantRotate:
                self.shape = backupShape
                
        
        for y, row in enumerate(self.shape):
            for x, point in enumerate(row):
                if point != None:
                    self.shape[y][x].coord = (self.corner_coord[0] + x, self.corner_coord[1] + y)
        
        self.shapeWidth = len(self.shape[0])
        leaveLoop = False
        for collumn in range(self.shapeWidth):
            for y in self.shape:
                if y[collumn] != None:
                    self.shapeWidth -= collumn
                    leaveLoop = True
                    break
            if leaveLoop:
                break
        
                
        
    def move(self, keys, collisionBoard):
        if keys["left"].pressed and self.corner_coord[0] > 0:
            canShift = True
            
            for y in range(len(self.shape)):
                for x, point in enumerate(self.shape[y]):
                    if point != None:
                        if collisionBoard[point.coord[1]][point.coord[0] - 1] != 0:
                            canShift = False
            
            if canShift:
                self.corner_coord = (self.corner_coord[0] - 1, self.corner_coord[1])
                for y in range(len(self.shape)):
                    for x, point in enumerate(self.shape[y]):
                        if point != None:
                            point.coord = (point.coord[0] - 1, point.coord[1])
                        
        if keys["right"].pressed and self.corner_coord[0] + self.shapeWidth < WIDTH:
            canShift = True
            
            for y in range(len(self.shape)):
                for x, point in enumerate(self.shape[y]):
                    if point != None:
                        if collisionBoard[point.coord[1]][point.coord[0] + 1] != 0:
                            canShift = False
            
            if canShift:
                self.corner_coord = (self.corner_coord[0] + 1, self.corner_coord[1])
                for y in range(len(self.shape)):
                    for x, point in enumerate(self.shape[y]):
                        if point != None:
                            point.coord = (point.coord[0] + 1, point.coord[1])
                        
        if keys["down"].pressed:
            self.drop(collisionBoard)
            
        if keys["space"].pressed:
            self.rotate(collisionBoard)
        
    def drop(self, collisionBoard):
        canDrop = True
        for y in range(len(self.shape)):
            for x, point in enumerate(self.shape[y]):
                if point != None:
                    if point.coord[1] + 1 >= HEIGHT  or  collisionBoard[point.coord[1] + 1][point.coord[0]] != 0:
                        canDrop = False
                        break
        
        if canDrop:
            self.corner_coord = (self.corner_coord[0], self.corner_coord[1] + 1)
            for y in range(len(self.shape)):
                for x, point in enumerate(self.shape[y]):
                    if point != None:
                        point.coord = (point.coord[0], point.coord[1] + 1)
                        
        else:
            self.alive = False
        
    def solidify(self, collisionBoard):
        for y in range(len(self.shape)):
            for x, point in enumerate(self.shape[y]):
                if point != None:
                    collisionBoard[point.coord[1]][point.coord[0]] = point.colour
        return collisionBoard
        
    def inShape(self, checkX, checkY):
        for y in range(len(self.shape)):
            for x, point in enumerate(self.shape[y]):
                if point != None:
                    if (checkX, checkY) == point.coord:
                        return True
        return False
        
                
                
### KEYS ###

class PressKey:
    def __init__(self, kind):
        if kind == "up":
            self.keys = ["\'w\'", "\'W\'", "Key.up"]
        elif kind == "down":
            self.keys = ["\'s\'", "\'S\'", "Key.down"]
        elif kind == "right":
            self.keys = ["\'d\'", "\'D\'", "Key.right"]
        elif kind == "left":
            self.keys = ["\'a\'", "\'A\'", "Key.left"]
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
    "left":     PressKey("left"),
    "right":    PressKey("right"),
    "space":    PressKey("space"),
    "esc":      PressKey("esc")
}


def on_key_press(key):
    if str(key) in keys["up"].keys:
        keys["up"].pressed = True
    elif str(key) in keys["right"].keys:
        keys["right"].pressed = True
    elif str(key) in keys["down"].keys:
        keys["down"].pressed = True
    elif str(key) in keys["left"].keys:
        keys["left"].pressed = True
    elif str(key) in keys["space"].keys:
        keys["space"].pressed = True
    elif str(key) in keys["esc"].keys:
        keys["esc"].pressed = True
        
def on_key_release(key): 
    if str(key) in keys["down"].keys:
        keys["down"].pressed = False


def keyInputs():
    # Collect events until released
    with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

keyboardT = threading.Thread(target=keyInputs, args=(), daemon = True)
keyboardT.start()                


def blankBoard():
    board = []
    for y in range(HEIGHT):
        newrow = []
        for x in range(WIDTH):
            newrow.append(0)
        board.append(newrow)
    return board
         
                
def printBoard(collisionBoard, currentShape, score, isTetris):
    frame = "\033[1;39m+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
    
    for y, row in enumerate(collisionBoard):
        frame += "|"
        for x, point in enumerate(row):
            if collisionBoard[y][x] != 0:
                frame += "\033[1;{}m[]".format(point)
            elif currentShape.inShape(x,y):
                frame += "\033[1;{}m[]".format(currentShape.colour)
            else:
                frame += "  "
        frame += "\033[1;39m|\n"
    
    frame += "\033[1;39m+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
    
    frame += centerTo(f"Score: {score}", WIDTH*2+2)
    
    clearScreen()
    print(frame)
    

def printDeathMenu(showMenu, score, highscore):
    
    deathScreens = [["GAMEOVER",
                    " /__  ___/                                 ",
                    "   / /   ___    __  ___  __     ( )  ___   ",
                    "  / /  //___) )  / /   //  ) ) / / ((   ) )",
                    " / /  //        / /   //      / /   \ \    ",
                    "/ /  ((____    / /   //      / / //   ) )  ",
                    "",
                    "Press SPACE to play again"],
                    
                    ["GAMEOVER",
                    " _______   _        _     ",
                    "|__   __| | |      (_)    ",
                    "   | | ___| |_ _ __ _ ___ ",
                    "   | |/ _ \ __| '__| / __|",
                    "   | |  __/ |_| |  | \__ \\",
                    "   |_|\___|\__|_|  |_|___/",
                    "",
                    "Press SPACE to play again"]
                    
                    ]
    deathScreen =  deathScreens[1]
    
    frame = "\033[1;39m+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
                
    for y in range((HEIGHT - len(deathScreen)) // 2):
        frame += "|" + centerTo("",WIDTH*2) + "|\n"
    
    for line in deathScreen:
        if showMenu:
            frame += "|" + centerTo(line,WIDTH*2) + "|\n"
        else:
            frame += "|" + centerTo("",WIDTH*2) + "|\n"
        
    for y in range((HEIGHT - len(deathScreen)) // 2):
        frame += "|" + centerTo("",WIDTH*2) + "|\n"
        
    frame += "+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
    
    frame += centerTo(f"Score: {score}", WIDTH*2+2) + "\n"
    frame += centerTo(f"Highscore: {highscore}", WIDTH*2+2)
    
    #clearscreen()
    print(frame)
        
        

blocksMeta = [
    {"colour": 36,
    "shape":
        [[1,1,1,1]]},
    
    {"colour": 37,
     "shape":
        [[1,0],
         [1,0],
         [1,1]]},
    
    {"colour": 34,
     "shape":
        [[0,1,0],
         [1,1,1]]},
    
    {"colour": 33,
     "shape":
        [[1,1],
         [1,1]]},
    
    {"colour": 35,
     "shape":
        [[0,1],
         [0,1],
         [1,1]]},
    
    {"colour": 32,
     "shape":
        [[1,1,0],
         [0,1,1]]},
    
    {"colour": 31,
     "shape":
        [[0,1,1],
         [1,1,0]]}
]

highscore = 0

playing = True
while playing:
        
    collisionBoard = blankBoard()
    startBlock = True
    score = 0
    isMove = True

    while True:
        tick_start = process_time()
        
        if startBlock or (not currentShape.alive):
            createType = blocksMeta[randint(0, len(blocksMeta) - 1)]
            currentShape = Shape(createType, ( randint(0 , WIDTH - len(createType["shape"][0])) , 0 ),  len(createType["shape"][0]))
            startBlock = False
            
        
        currentShape.move(keys, collisionBoard)
        if currentShape.alive and isMove:
            currentShape.drop(collisionBoard)
        
        if not currentShape.alive:
            collisionBoard = currentShape.solidify(collisionBoard)
            score += 1
            
        totalRows = 0
        for y, row in enumerate(collisionBoard):
            if not 0 in row:
                totalRows += 1
                collisionBoard.pop(y)
                collisionBoard = collisionBoard[::-1]
                collisionBoard.append([0 for x in range(WIDTH)])
                collisionBoard = collisionBoard[::-1]
                score += 10
        isTetris = False
        if totalRows >= 4:
            score += 50
            isTetris = True
                
        if (collisionBoard[0] != [0 for i in range(WIDTH)] or 
            collisionBoard[1] != [0 for i in range(WIDTH)]):
            sleep(1.25)
            break
        
        for key in keys:    
            if key != "down":
                keys[key].pressed = False
            
        printBoard(collisionBoard, currentShape, score, isTetris)
        
        if isMove:
            isMove = False
        else:
            isMove = True
        
        
        sleep(max(1/TICKSPEED - (process_time() - tick_start), 0.1))
        
    score -= 1
    
    highscore = max(score, highscore)
    
    for key in keys:
        keys[key].pressed = False

    showMenu = True
    while True:
        tickstart = process_time()
        
        printDeathMenu(showMenu, score, highscore)
        
        if keys["space"].pressed:
            for key in keys:
                keys[key].pressed = False
            break
        
        if keys["esc"].pressed:
            playing = False
            break
        
        if showMenu:
            showMenu = False
        else:
            showMenu = True
        
        sleep(max(1 - (process_time() - tick_start), 0.1))