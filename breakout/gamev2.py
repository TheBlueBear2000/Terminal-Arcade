print("Loading...")

### LIBRARIES ###
# You may need to install pynput, everything else should be part of default libs (I think)
from random import randint
from pynput.keyboard import Listener
import threading
from math import sin
from time import process_time, sleep
from os import system, name

### CONSTANTS ###
WIDTH, HEIGHT = 50, 30
BASE_FPS = 50
PADDLE_WIDTH = 7
VALID_ANGLES = [292.5, 315, 337.5, 0, 22.5, 45, 67.5]  # All valid starter angles.  They point in three angles both left and right to add variety and make gameplay interesting

### LAMBDA STATEMENTS ###
clearScreen = lambda : system('cls' if name == 'nt' else 'clear')  # Clears the screen
centerTo = lambda line, width : "{0:^{1}}".format(line, width)  # Centers a string to a given value
getVector = lambda speed, angle : (speed * sin(angle)  ,  abs(speed * sin(90 - angle)) * -1 )  # Calculates a vector from a speed and an angle  (the Y value will always be negative, meaning the ball will always go up after its given a new vector)


### CLASSES ###

class Ball:
    def __init__(self, angle, y, x):
        self.speed = 0.5
        self.collided = False
        self.score = 0
        self.x = x
        self.y = y
        self.coord = (self.x, self.y)
        self.vector = getVector(self.speed, angle)  # Vector system allows for dynamic directions using angles and speeds
        self.hits = 0
        
        self.hitOrange = False  # For speed control
        self.hitRed = False     # For speed control
        
        
    def flipx(self): # Inverts the direction of the x part of the balls vector
        self.vector = (self.vector[0] * -1, self.vector[1])
    
    def flipy(self): # Inverts the direction of the x part of the balls vector
        self.vector = (self.vector[0], self.vector[1] * -1)
    
    def paddleflip(self, paddlevalue): # Creates a new random vector for the ball (for bouncing on paddle)
        self.vector = getVector(self.speed, paddlevalue)
            
    def changespeed(self, value, multiplier = True): # Multiplies the direction of the vector as well as the ball speed
        if multiplier:
            self.vector = (self.vector[0] * value, self.vector[1] * value)
            self.speed *= value
        else:
            self.vector = (self.vector[0] + value, self.vector[1] + value)
            self.speed *= value
        
    
    def hitbrick(self, bricks, x, y):
        self.score += bricks[y][x].value  # Each brick has a different value depending on its row
        self.hits += 1
        
        if self.hits == 4 or self.hits == 12:  # Ball speed will increase by 20% after 4 hits, after 12 hits, when the ball first hits red and when the ball first hits orange
            self.changespeed(1.2)
        
        if (not self.hitOrange) and bricks[y][x].value == 5:
            self.changespeed(1.2)
            self.hitOrange = True
        elif (not self.hitRed) and bricks[y][x].value == 7:
            self.changespeed(1.2)
            self.hitRed = True
        
        bricks[y][x] = None
        
        return bricks
        
    def move(self, paddle, bricks):
        
        
        # Paddle collision #
        
        for i, part in enumerate(paddle.body):
            if (int(self.x + 1) == part[0] and int(self.y) == part[1]) or (int(self.x - 1) == part[0] and int(self.y) == part[1]) or (int(self.x) == part[0] and int(self.y + 1) == part[1]) or (int(self.x) == part[0] and int(self.y - 1) == part[1]):
                self.paddleflip(part[2], ((len(paddle.body)//2) - i) // abs((len(paddle.body)//2) - i))
                self.y -= 2
                self.collided = True
        
        #if (int(self.x + 1), int(self.y)) in paddle.body  or  (int(self.x - 1), int(self.y)) in paddle.body  or  (int(self.x), int(self.y + 1)) in paddle.body  or  (int(self.x), int(self.y - 1)) in paddle.body:
        #    self.paddleflip()
        #    self.y -= 2
        #    self.collided = True
                
        # Roof collision #
        if self.y - 1 < 0:
            self.flipy()
            if not paddle.ishalved:
                paddle.halfsize()
        # Wall collision #
        if self.x <= 0 or self.x >= WIDTH-1:
            self.flipx()
            self.x += self.vector[0]
            
        # Brick collision #
        for y, row in enumerate(bricks):
            for x, brick in enumerate(row):
                if brick != None:
                    if (int(self.x + 1), int(self.y)) in brick.parts or (int(self.x - 1), int(self.y)) in brick.parts:
                        self.flipx()
                        bricks = self.hitbrick(bricks, x, y)
                    if (int(self.x), int(self.y + 1)) in brick.parts or (int(self.x), int(self.y - 1)) in brick.parts:
                        self.flipy()
                        bricks = self.hitbrick(bricks, x, y)
                        
        # Add the vector
        self.x += self.vector[0]
        self.y += self.vector[1]
        
            
        self.coord = (self.x, self.y)
        return bricks
        
class Paddle:
    def __init__(self, y):
        self.y = y
        self.x = WIDTH//2
        self.coord = (self.x, y)
        self.body = []
        for x in range(PADDLE_WIDTH): # Creates paddle segments
            self.body.append(((WIDTH-PADDLE_WIDTH)//2 + x, self.y,  VALID_ANGLES[int(len(VALID_ANGLES) * (x/PADDLE_WIDTH))]))
        self.ishalved = False

    def shift(self, left):
        for move in range(2): # Paddle technically moves 2 blocks every tick, but they must be checked seperatly for wall collision
            firstblock = self.body[0]
            lastblock = self.body[len(self.body)-1]
            for i in range(len(self.body)):
                if left and firstblock[0] > 0:
                    self.body[i] = (self.body[i][0] - 1, self.body[i][1], self.body[i][2])
                    
                elif (not left) and lastblock[0] < WIDTH - 1:
                    self.body[i] = (self.body[i][0] + 1, self.body[i][1], self.body[i][2])
    
    def halfsize(self): # Halves the length of the paddle for when the ball hits the roof (only happens once)
        length = len(self.body)
        self.body = self.body[length//4 : length - (length//4)]
        self.ishalved = True
                    

class Block: # The actual bricks being eliminated
    def __init__(self, leftCoord, value):
        self.parts = []
        for x in range(2):
            self.parts.append((leftCoord[0] + x, leftCoord[1]))
        self.value = value
        


### KEYS ###

class PressKey:
    def __init__(self, kind):
        # Different valid keys for controls
        if kind == "up":
            self.keys = ["\'w\'", "\'W\'","Key.up"] # Unused
        elif kind == "down":
            self.keys = ["\'s\'", "\'S\'","Key.down"] # Unused
        elif kind == "right":
            self.keys = ["\'d\'", "\'D\'","Key.right"]
        elif kind == "left":
            self.keys = ["\'a\'", "\'A\'","Key.left"]
            
            
        elif kind == "space":
            self.keys = ["Key.space"]
        elif kind == "esc":
            self.keys = ["Key.esc"]
        else:
            raise Exception("Tried to create a key with an invalid type") # To catch programming errors
        
        self.pressed = False

keys = { # With a keys dict, they can be viewed much more easily
    "up":       PressKey("up"),
    "down":     PressKey("down"),
    "left":     PressKey("left"),
    "right":    PressKey("right"),
    "space":    PressKey("space"),
    "esc":      PressKey("esc")
}

# You dont wanna know what the next the functions do
def on_key_press(key):
    for keytype in keys:
        if str(key) in keys[keytype].keys:
            keys[keytype].pressed = True
        
def on_key_release(key):
    for keytype in keys:
        if str(key) in keys[keytype].keys and not (keytype == "space" or keytype == "esc"): # "space" and "esc" are tap keys, the automatically unpress themselves when they are hit, while the others can be held down
            keys[keytype].pressed = False

# Esspecially this one, I stole it from SO
def keyInputs():
    with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

# Keyboard input process is threaded
keyboardT = threading.Thread(target=keyInputs, args=(), daemon = True)
keyboardT.start()


### FUNCTIONS ###

def printBoard(paddle, ball, bricks, score, turns, paused = False):
    
    # Ascii art in the form of a 2d array for all digits 0-9 (in their correct index, meaning it is easy to access)
    digits = [ [" _ ", # 0
                "/ \\",
                "\_/"],
               ["   ", # 1
                "/| ",
                " | "],
               ["__ ", # 2
                " _)",
                "/__"],
               ["__ ", # 3
                "__)",
                "__)"],
               ["   ", # 4
                "|_|",
                "  |"],
               [" __", # 5
                "|_ ",
                "__)"],
               [" _ ", # 6
                "|_ ",
                "|_)"],
               [" __", # 7
                "  /",
                " / "],
               [" _ ", # 8
                "(_)",
                "(_)"],
               [" _ ", # 9
                "(_|",
                " _|"]
               ]
    
    # Score and balls display
    frame = "+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
    
    frame += "|"
    
    scoreword = str(score)
    while len(scoreword) < 3:
        scoreword = "0" + scoreword
        
    for i in range(3):
        frame += "  "
        for x in range(3):
            frame += digits[int(list(scoreword)[x])][i]
        for x in range(WIDTH * 2 - 18 - (turns * 2)):
            frame += " "
        for x in range(turns):
            if i == 1:
                frame += "()"
            else:
                frame += "  "
        frame += "  " + digits[turns][i] + "  "
        frame += "|\n|"
    
    for i in range(WIDTH):
        frame += "  "
    frame += "|\n"
            
    # Gamescreen display
    frame += "+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"

    # Locates the character at that location
    def makeChar(paddle, ball, bricks, x , y):
        char = ""
        paddlebodycoords = []
        for part in paddle.body:
            paddlebodycoords.append((part[0], part[1]))
        if x == int(ball.coord[0]) and y == int(ball.coord[1]):
            char += f"\033[1;39m(){colour}"
        elif y > 3 and y <= 11:
            if bricks[y-4][x//2] != None:
                if x%2 == 0:
                    char += "[_"
                else:
                    char += "_]"
            else:
                char += "  "
        elif (x, y) in paddlebodycoords:
            char += "[]"
        else:
            char += "  "
        return char
    
    for y in range(HEIGHT):
        frame += "|"
        # Gives different colours to different rows
        if y > 11:
            colour = "\033[1;39m"
        elif y > 9:
            colour = "\033[1;33m"
        elif y > 7:
            colour = "\033[1;32m"
        elif y > 5:
            colour = "\033[1;33m"
        elif y > 3:
            colour = "\033[1;31m"
        else:
            colour = "\033[1;39m"
        frame += colour
        if paused and y == HEIGHT//2:
            pauseMsg = "Paused"
            for x in range((WIDTH-len(pauseMsg))//2+2):
                frame += makeChar(paddle, ball, bricks, x , y)
            frame += pauseMsg
            for x in range((WIDTH-len(pauseMsg))//2+1):
                frame += makeChar(paddle, ball, bricks, x + ((WIDTH*2 + (len(pauseMsg)))//4 + 1) , y)
        else:
            for x in range(WIDTH):
                frame += makeChar(paddle, ball, bricks, x , y)
            
        frame += "\033[1;39m|\n"

    frame += "+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
    
    clearScreen()
    print(frame)

def printMenu(score, win, isFlash):
    
    # This amalgimation can have values adjusted to change size and layout of title screen
    deathIcon = [
        "\033[1;31m______   ______ _______ _______ _     _  _____  _     _ _______",
        "\033[1;32m|_____] |_____/ |______ |_____| |____/  |     | |     |    |   ",
        "\033[1;33m|_____] |    \_ |______ |     | |    \_ |_____| |_____|    |   "
    ]
    
    frame = "+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
    
    for y in range(((HEIGHT + 6)-len(deathIcon))//2-2):
        frame += "|" + centerTo("",WIDTH*2) + "|\n"
        
    if win:
        frame += "|" + centerTo("YOU WIN!",WIDTH*2) + "|\n"
    else:
        frame += "|" + centerTo("Thank you for playing...",WIDTH*2) + "|\n"
    frame += "|" + centerTo("",WIDTH*2) + "|\n"
    for y in range(len(deathIcon)):
        if isFlash:
            frame += "|" + centerTo(deathIcon[y],WIDTH*2+7) + "\033[1;39m|\n"
        else:
            frame += "|" + centerTo("",WIDTH*2) + "|\n"
    frame += "|" + centerTo("",WIDTH*2) + "|\n"
    frame += "|" + centerTo(f"Score: {score}",WIDTH*2) + "|\n"
    frame += "|" + centerTo("",WIDTH*2) + "|\n"
    frame += "|" + centerTo("Press SPACE to play again",WIDTH*2) + "|\n"
        
    for y in range(((HEIGHT + 6)-len(deathIcon))//2-4):
        frame += "|" + centerTo("",WIDTH*2) + "|\n"
        
    frame += "+"
    for x in range(WIDTH):
        frame += "--"
    frame += "+\n"
    
    clearScreen()
    print(frame)
    

### GAMELOOP ###

gameloop = True
while gameloop:
    
    # Game initialisation
    bricks = []
    value = 9
    # Create bricks
    for y in range(8):
        # Calculates brick values
        if y % 2 == 0:
            value -= 2
        bricks.append([])
        for x in range(WIDTH//2):
            bricks[y].append(Block((x*2, y + 3), value))
            
    fps = BASE_FPS
    paddle = Paddle(HEIGHT - 3) # CREATES PADDLE
    newBall = False
    ball = Ball(VALID_ANGLES[randint(0,5)], paddle.y - 2, paddle.body[len(paddle.body)//2][0]) # CREATES BALL
    ballPauseTimer = 0
    started = False
    
    turns = 3
    
    while True:
        tick_start = process_time()
        
        # Creates a new ball if newBall bool is True
        if newBall:
            ball.x = paddle.body[len(paddle.body)//2][0]
            ball.y = paddle.y - 2
            ball.coord = (ball.x, ball.y)
            ball.vector = getVector(ball.speed, VALID_ANGLES[randint(0,5)])
            ballPauseTimer = 10
            newBall = False
        
        # Paddle movement
        if keys["left"].pressed:
            paddle.shift(True)
            started = True
        if keys["right"].pressed:
            paddle.shift(False)
            started = True

        if started:
            # Game tick if the player has started the game (hit a key and moved the paddle)
            if ballPauseTimer <= 0:
                bricks = ball.move(paddle, bricks)
                moveBall = False
            else:
                ballPauseTimer -= 1
                ball.x = paddle.body[len(paddle.body)//2][0]
                ball.coord = (ball.x, ball.y)
        
        # Ball floor handling
        if ball.y >= HEIGHT and turns < 1: # End game if out of turns
            win = False
            break
        elif ball.y >= HEIGHT: # Make new ball if not out of turns
            turns -= 1
            newBall = True
            
        # Checks for victory
        win = True
        for row in bricks:
            for brick in row:
                if brick != None:
                    win = False
                    break
            if win == False:
                break
        if win:
            break
        
        # Scans "esc" key to leave game
        if keys["esc"].pressed:
            keys["esc"].pressed = False
            win = False
            break
            
        # Pause
        if keys["space"].pressed:
            keys["space"].pressed = False
            printBoard(paddle, ball, bricks, ball.score, turns, True)
            while not keys["space"].pressed:
                sleep(0.1) # 0.1 second delay while pausing to detect new keys, screen not updated (obviously, its not needed)
            keys["space"].pressed = False
            
        printBoard(paddle, ball, bricks, ball.score, turns)
        
        
        sleep(max(1/fps  -  (process_time() - tick_start), 0.05)) # Pauses for the tick time - the time taken so far in this tick to make tickspeed dynamic and consistent

    isFlash = True
    ### MENU LOOP ###
    while True:
        tick_start = process_time()
        
        # "space" key will restart game, "esc" will kill game
        if keys["space"].pressed:
            keys["space"].pressed = False
            break
        if keys["esc"].pressed:
            gameloop = False
            break
        
        printMenu(ball.score, win, isFlash)
        
        # Sorts flashing
        if isFlash:
            isFlash = False
        else:
            isFlash = True
        
        sleep(max(0.5  -  (process_time() - tick_start), 0.05)) # Pauses for the tick time - the time taken so far in this tick to make tickspeed dynamic and consistent
        