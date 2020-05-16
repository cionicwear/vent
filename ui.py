from RPi import GPIO
from time import sleep
from evdev import UInput, ecodes as e
import logging
import time

CLK_PIN = 22
DT_PIN = 27
SW_PIN = 17
A_PIN = 10
B_PIN = 11
SPK_PIN = 9

GPIO.setmode(GPIO.BCM)
# rotary
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# buttons
GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#speaker
GPIO.setup(SPK_PIN, GPIO.OUT)
#ui
ui = UInput()

# globals
g_counter = 0
g_clk = GPIO.input(CLK_PIN)

def _keystroke(key):
    logging.warning(key)
    ui.write(e.EV_KEY, key, 1)  # key down
    ui.write(e.EV_KEY, key, 0)  # key up
    ui.syn()

def knob_callback(c):
    _keystroke(e.KEY_K)

def a_callback(c):
    _keystroke(e.KEY_A)

def b_callback(c):
    _keystroke(e.KEY_S)

def rotary_callback(c):
    global g_counter
    global g_clk
    
    clk = GPIO.input(CLK_PIN)
    dt = GPIO.input(DT_PIN)
    if clk != g_clk:
        g_clk = clk
        if dt != clk:
            g_counter += 1
            _keystroke(e.KEY_L)
        else:
            g_counter -= 1
            _keystroke(e.KEY_J)
        

def alarm(seconds):
    GPIO.output(SPK_PIN, 1)
    time.sleep(seconds)
    GPIO.output(SPK_PIN, 0)

def ui_loop():
    GPIO.add_event_detect(SW_PIN, GPIO.FALLING, callback=knob_callback, bouncetime=1200)
    GPIO.add_event_detect(A_PIN, GPIO.FALLING, callback=a_callback, bouncetime=1200)
    GPIO.add_event_detect(B_PIN, GPIO.FALLING, callback=b_callback, bouncetime=1200)
    GPIO.add_event_detect(CLK_PIN, GPIO.FALLING, callback=rotary_callback, bouncetime=2)
    logging.warning("UI running press anything to exit")
    
if __name__ == '__main__':
    ui_loop()
    while True:
        user = input()
        if (user == ""):
            break
        try:
            seconds = int(user)
            alarm(seconds)
        except Exception as e:
            print(e)

    GPIO.cleanup()
    ui.close()
    
