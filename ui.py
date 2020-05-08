from RPi import GPIO
from time import sleep
from evdev import UInput, ecodes as e

CLK_PIN = 22
DT_PIN = 27
SW_PIN = 17
A_PIN = 6
B_PIN = 5

GPIO.setmode(GPIO.BCM)
# rotary
GPIO.setup(CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# buttons
GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#ui
ui = UInput()

def _keystroke(key):
    ui.write(e.EV_KEY, key, 1)  # key down
    ui.write(e.EV_KEY, key, 0)  # key up
    ui.syn()

def knob_callback(c):
    _keystroke(e.KEY_ENTER)

def a_callback(c):
    _keystroke(e.KEY_A)

def b_callback(c):
    _keystroke(e.KEY_B)

def ui_loop():
    counter = 0
    clkLastState = GPIO.input(CLK_PIN)
    swLastState = GPIO.input(SW_PIN)
    
    GPIO.add_event_detect(SW_PIN, GPIO.FALLING, callback=knob_callback, bouncetime=300)
    GPIO.add_event_detect(A_PIN, GPIO.FALLING, callback=a_callback, bouncetime=300)
    GPIO.add_event_detect(B_PIN, GPIO.FALLING, callback=b_callback, bouncetime=300)
    
    try:
        while True:
            clkState = GPIO.input(CLK_PIN)
            dtState = GPIO.input(DT_PIN)
            swState = GPIO.input(SW_PIN)
            if clkState != clkLastState:
                if dtState != clkState:
                    counter += 1
                    _keystroke(e.KEY_R)
                else:
                    counter -= 1
                    _keystroke(e.KEY_L)
                print(counter)
                clkLastState = clkState
                sleep(0.01)

    finally:
        GPIO.cleanup()
        ui.close()
    
if __name__ == '__main__':
    ui_loop()
