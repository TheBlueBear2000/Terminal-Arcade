from pynput.keyboard import Key, Listener

keyUp = False
keyDown = False
keyLeft = False
keyRight = False

def on_press(key):
    
    if str(key) == "w" or str(key) == "W" or key == Key.up:
        global key_up
        print("     w pressed lol")
        key_up = True
    elif str(key) == "s" or str(key) == "S" or key == Key.down:
        global key_down
        key_down = True
    elif str(key) == "a" or str(key) == "A" or key == Key.left:
        global key_left
        key_left = True
    elif str(key) == "d" or str(key) == "D" or key == Key.right:
        global key_right
        key_right = True
        
        
    print('{0} pressed, type:{1}'.format(key, type(key)))



def on_release(key): {}
    #print('{0} release, type: {1}'.format(key, type(key)))
    #if key == Key.esc:
        # Stop listener
        #return False

# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
    
    
    
def getKeys():
    return [keyUp, keyRight, keyDown, keyLeft]
