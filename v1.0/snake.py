def run():
    print('Loading...')
    from random import randint as rand
    from pynput.keyboard import Listener
    from time import sleep, process_time
    from os import system, name
    import threading
    from main import printOnWindow

    WIDTH, HEIGHT = 50, 30

    MAX_APPLES = 2
    DEFAULT_SPEED = 10

    fps = DEFAULT_SPEED
    leaveDeathScreen = False
    replay = False
    highscore = 0

    centerTo = lambda line, width : "{0:^{1}}".format(line, width)

    class Snake:
        def __init__(self):
            self.len = 4
            self.body = [(WIDTH/2, HEIGHT/2) for i in range(self.len)]
            self.head = self.body[self.len -1]
            
            self.direction = 0  #   0 = up
                                #   1 = right
                                #   2 = down
                                #   3 = left
            
        def move(self):

            # Create new head:
                
            head = self.body[len(self.body) - 1]
                
            if self.direction == 0:
                self.body.append((head[0]     , head[1] -1))
            elif self.direction == 1:
                self.body.append((head[0] + 1 , head[1]))
            elif self.direction == 2:
                self.body.append((head[0]     , head[1] + 1))
            elif self.direction == 3:
                self.body.append((head[0] - 1 , head[1]))
                
            self.head = self.body[len(self.body) - 1]
                
                
            # Check kill conditions:
            
            # Body hit
            for segment in self.body[1:-1]:
                if segment == self.head:
                    return False
            # Wall hit
            if self.head[0] < 0 or self.head[0] >= WIDTH or self.head[1] < 0 or self.head[1] >= HEIGHT:
                return False
            
                
            return True
                
    class Apple:
        def __init__(self):
            self.x = rand(0,WIDTH-1)
            self.y = rand(0,HEIGHT-1)
            self.pos = (self.x, self.y)
            
            
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
        
        
    ### KEYS ###


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
            
    def on_key_release(key): {}

    def keyInputs():
        # Collect events until released
        with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
            listener.join()

    keyboardT = threading.Thread(target=keyInputs, args=(), daemon = True)
    keyboardT.start()
        
            
    ### FUNCTIONS ###

    def printBoard(snake, apples, pauseScreen = False):

        frame = []
        
        line = "+"
        for i in range(WIDTH):
            line += "--"
        frame.append(line + "+")
        
        for y in range(HEIGHT):
            line = "|"
            for x in range(WIDTH):
                printBlank = True
                if not(pauseScreen and y == HEIGHT //2 and (x == WIDTH//2 -1 or x == WIDTH//2 +1 or x == WIDTH//2 +2)):
                    if pauseScreen and y == HEIGHT //2 and x == WIDTH//2:
                        line += "\033[1;39mPAUSED"
                    for segment in snake.body:
                        if segment == (x, y):
                            printBlank = False
                            line += "\033[1;32m()" # "()" but green
                            break
                    if printBlank:
                        for apple in apples:
                            if apple.pos == (x, y):
                                printBlank = False
                                line += "\033[1;31m()" # "()" but red
                                break
                    if printBlank:
                        line += "  "


            frame.append(line + "\033[1;39m|") # Set text back to white for borders
        
        
        line = "+"
        for i in range(WIDTH):
            line += "--"
        frame.append(line + "+")
        
        frame.append(centerTo("Score: {}".format(snake.len - 4), WIDTH * 2 + 2))
        frame.append("")
        
        printOnWindow(frame, WIDTH)
        
        
    def printDeathScreen(onFlash, highscore, win):
        frame = []
        if WIDTH >= 33 and HEIGHT >= 11:
            deathScreen = [
                    "                     Thanks for playing                           ",    # Some lines are longer to account for the \'s
                    "    ________  ________   ________  ___  __    _______             ",
                    "   |\   ____\|\   ___  \|\   __  \|\  \|\  \ |\  ___ \            ",
                    "   \ \  \___|\ \  \\\\ \  \ \  \|\  \ \  \/  /|\ \   __/|           ",
                    "    \ \_____  \ \  \\\\ \  \ \   __  \ \   ___  \ \  \_|/__         ",
                    "     \|____|\  \ \  \\\\ \  \ \  \ \  \ \  \\\\ \  \ \  \_|\ \        ",  
                    "       ____\_\  \ \__\\\\ \__\ \__\ \__\ \__\\\\ \__\ \_______\       ",
                    "      |\_________\|__| \|__|\|__|\|__|\|__| \|__|\|_______|       ",
                    "       \|_________|                                               "]
        elif WIDTH >= 25 and HEIGHT >= 7:
            deathScreen = [
                "               Thanks for playing                ",
                "    //   ) )                                     ",
                "   ((          __      ___     / ___      ___    ",
                "     \\\\     //   ) ) //   ) ) //\ \     //___) ) ",
                "       ) ) //   / / //   / / //  \ \   //        ",
                "((___ / / //   / / ((___( ( //    \ \ ((____     "]
        elif WIDTH >= 15 and HEIGHT >= 6:
            deathScreen = [
                "      Thanks for playing      ",
                " ____  __ _   __   __ _  ____ ",
                "/ ___)(  ( \ / _\ (  / )(  __)",
                "\___ \/    //    \ )  (  ) _) ",
                "(____/\_)__)\_/\_/(__\_)(____)"
            ]
        else:
            deathScreen = [
                "Thanks for playing",
                "      Snake       "
            ]
        
        line = "+"
        for i in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        for i in range((HEIGHT - len(deathScreen)) // 2 - 2):
            frame.append("|" + centerTo("",WIDTH * 2) + "|")
            
        frame.append("|" + centerTo("You win!  " if win else "You lose...  ", WIDTH*2) + "|")
        frame.append("|" + centerTo("",WIDTH * 2) + "|")
        
        if onFlash:
            for line in deathScreen:
                frame.append("|" + centerTo(line, WIDTH*2) + "|")
        else:
            for line in deathScreen:
                frame.append("|" + centerTo("",WIDTH * 2) + "|")
        
        frame.append("|" + centerTo("Press SPACE to play again", WIDTH*2) + "|")
                
        for i in range((HEIGHT - len(deathScreen)) // 2 - 1):
            frame.append("|" + centerTo("",WIDTH * 2) + "|")

        line = "+"
        for i in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        frame.append(centerTo("Score: {}".format(snake.len - 4), WIDTH*2+2))
        frame.append("")
        frame.append(centerTo(f"Highscore: {highscore}", WIDTH*2+2))
            
        printOnWindow(frame, WIDTH)
            
        

    # Main
    
    replay = True
    while replay:
        
        snake = Snake()
        
        apples = [Apple() for i in range(MAX_APPLES)]
        fps = DEFAULT_SPEED
        
        win = False
        started = False
        
        paused = False
        
        printBoard(snake, apples)
        sleep(0.5)
        printBoard(snake, apples)
                
        gameloop = True
        while gameloop:
            tickStart = process_time()
            
            if keys["up"].pressed:
                snake.direction = 0
            elif keys["right"].pressed:
                snake.direction = 1
            elif keys["down"].pressed:
                snake.direction = 2
            elif keys["left"].pressed:
                snake.direction = 3
                
            if keys["space"].pressed:
                paused = True
                keys["space"].pressed = False
            if keys["esc"].pressed:
                keys["esc"].pressed = False
                break

                    
                    
            if started:
                if not snake.move():
                    break
            
                # Remove end of tail (unless apple is eaten):
            
                cutTail = True
                for i, apple in enumerate(apples):
                    if snake.head == apple.pos:
                        snake.len += 1
                        if snake.len < WIDTH * HEIGHT - MAX_APPLES:
                            while apple.pos in snake.body:
                                apples[i].__init__()
                        fps += 0.5
                        cutTail = False
                if cutTail and started:
                    snake.body.pop(0)
                    
                if snake.len >= WIDTH*HEIGHT:
                    win = True
                    break
                
                if paused:
                    printBoard(snake, apples, True)
                    while True:
                        if keys["space"].pressed or keys["esc"].pressed:
                            paused = False
                            keys["space"].pressed = False
                            keys["esc"].pressed = False
                            break
                
                for key in keys:
                    if keys[key].pressed:
                        started = True
                    keys[key].pressed = False
                    
            
                printBoard(snake, apples)
                
            for key in keys:
                if keys[key].pressed:
                    started = True
                keys[key].pressed = False
            
            
            sleep(max(0, 1/fps - (process_time() - tickStart))) # Delay for the chosen delay time - the time taken for the tick's process
            
        leaveDeathScreen = False
        onFlash = False
        
        highscore = max(highscore, snake.len - 4) # Update the highscore if necessary
        
        while not leaveDeathScreen:
            tickStart = process_time()
            
            if onFlash:
                onFlash = False
            else:
                onFlash = True
                
            if keys["space"].pressed:
                leaveDeathScreen = True
                replay = True
                
            if keys["esc"].pressed:
                leaveDeathScreen = True
                replay = False
                
            for key in keys:
                keys[key].pressed = False
                
            printDeathScreen(onFlash, highscore, win)
            
            sleep(1 - (process_time() - tickStart))

