import RPi.GPIO as GPIO
import time
from losantmqtt import Device
from neopixel import *
import atexit

# Define our pins
BUTTON_PIN = 12
KEY_PIN = 23
LED_PIN = 18

# Define Losant credentials
DEVICE_ID = '57578afde7a2700100d1dcb3'
ACCESS_KEY = '8ac0fd3f-1805-4087-82f0-b6e7ac3a5f04'
ACCESS_SECRET = '72722375d01b66217ce250e5a708dfeb5faf83573563a4b711a847eb09423faa'
MY_LED_INDEX = 0 # the index that this device ID is mapped to in the workflow

# Define Neopixels
LED_COUNT = 100 # Number of switches. set to a high number so we don't have to come back later and change devices if we add more switches
LED_FREQ_HZ = 800000 # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5 # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255 # Set to 0 for darkest and 255 for brightest
LED_INVERT = False # True to invert the signal (when using NPN transistor level shift

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()

red = Color(0, 255, 0)
green = Color(255,0,0)
off = Color(0,0,0)

# Construct device
device = Device(DEVICE_ID, ACCESS_KEY, ACCESS_SECRET)

def switch_offline(i):
    strip.setPixelColor(i, red)
    strip.show()
    print('Switch went offline: ', i)

def switch_all_offline():
    for i in range(0, LED_COUNT):
        strip.setPixelColor(i, red)
    strip.show()

def on_command(device, command):
    print("Command received.")
    print(command["name"])
    print(command["payload"])
    if(command["name"] == "setKeyStatus"):
        ledIndex = command["payload"]["ledIndex"]
        keyStatus = command["payload"]["keyStatus"]
        print(ledIndex)
        print(keyStatus)
        new_color = red # default offline
        if(keyStatus == 'engaged'):
            new_color = green
        strip.setPixelColor(ledIndex, new_color)
        strip.show()
    if(command["name"] == "btnPressedAnim"):
        animColor = red # assume failure
        if(command["payload"] and command["payload"]["status"] == "succeeded"):
            animColor = green #yay!
        statusBlink(strip, animColor, 150, 7)
        switch_all_offline()


# Listen for commands.
device.add_event_observer("command", on_command)

# Connect to Losant.
device.connect(blocking=False)

# gpio setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #try switching this to PUD_DOWN and flipping the bangs below
GPIO.setup(KEY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

is_button_pressed = False
is_key_turned = 0 # treating this as a number instead of a boolean. will make it easier to calculate if all buttons are pressed


def statusBlink(strip, color, wait_ms=50, iterations=10):
	for j in range(iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, off)
		strip.show()
		time.sleep(wait_ms/1000.0)

# on boot, mark all as offline
switch_all_offline()
# on exit, mark all as offline
atexit.register(switch_all_offline)

while True:
    device.loop()

    # Key
    key_state = GPIO.input(KEY_PIN) # False is when the key is turned, so we're flipping it for sanity's sake
    #if key_state == True: #changed from false (flipped above)
    if key_state == True and is_key_turned == 0:
    # state changed to turned
        print('Key Turned')
        is_key_turned = 1
        if device.is_connected():
            device.send_state({ "isKeyTurned": is_key_turned})
    if key_state == False and is_key_turned == 1:
    # state changed to unturned
        print('Key Released')
        is_key_turned = 0
        if device.is_connected():
            device.send_state({ "isKeyTurned": is_key_turned})
# Button
    button_state = GPIO.input(BUTTON_PIN) # False is when the button is pressed, so we're flipping it for sanity's sake
    if button_state == True and is_button_pressed == False:
    # state changed to pressed
        print('Button Pressed')
        is_button_pressed = True
        if device.is_connected():
            device.send_state({ "isButtonPressed": is_button_pressed })
    if button_state == False and is_button_pressed == True:
    # state changed to released
        print('Button Released')
        is_button_pressed = False
        # no need to send state here
    time.sleep(0.2) # wait before executing again
