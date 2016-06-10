import RPi.GPIO as GPIO
import time
from losantmqtt import Device
from losantrest import Client
import losantconfig

# MQTT SETUP
def on_command(device, command):
    print("Command received.")
    print(command["name"])
    print(command["payload"])
    if(command["name"] == "setKeyStatus"):
        deviceId = command["payload"]["deviceId"]
        keyStatus = command["payload"]["keyStatus"]
        print(deviceId)
        print(keyStatus)
        new_color = 'blue' #default offline
        if(keyStatus == 'engaged'):
            new_color = 'green'
        if(keyStatus == 'disengaged'):
            new_color = 'red'
        setColor(deviceId, new_color)
    if(command["name"] == "btnPressedAnim"):
        animColor = 'red' # assume failure
        if(command["payload"] and command["payload"]["status"] == "succeeded"):
            animColor = 'green' #yay!
        statusBlink(animColor, 150, 7)


# Construct device
device = Device(losantconfig.MY_DEVICE_ID, losantconfig.ACCESS_KEY, losantconfig.ACCESS_SECRET)
# Listen for commands.
device.add_event_observer("command", on_command)
# Connect to Losant.
device.connect(blocking=False)


# REST setup
client = Client()
creds = {
    'deviceId': losantconfig.MY_DEVICE_ID,
    'key': losantconfig.ACCESS_KEY,
    'secret': losantconfig.ACCESS_SECRET
}
rest_response = client.auth.authenticate_device(credentials=creds)

client.auth_token = rest_response['token']
app_id = rest_response['applicationId']


# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(losantconfig.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(losantconfig.KEY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def ledPinSetup(pins):
    # turn off by default
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)

ledPinSetup(losantconfig.LED_PINS[losantconfig.MY_DEVICE_ID])
ledPinSetup(losantconfig.LED_PINS[losantconfig.OTHER_DEVICE_ID])

# initial state
is_button_pressed = False
is_key_turned = 0 # treating this as a number instead of a boolean. will make it easier to calculate if all buttons are pressed


def statusBlink(color, wait_ms=50, iterations=10):
    print(color)
    for i in range(iterations):
        time.sleep(wait_ms/1000.0)
        setColor(losantconfig.MY_DEVICE_ID, color)
        setColor(losantconfig.OTHER_DEVICE_ID, color)
        time.sleep(wait_ms/1000.0)
        setColor(losantconfig.MY_DEVICE_ID, 'blue')
        setColor(losantconfig.OTHER_DEVICE_ID, 'blue')
    # set back to red (disengaged) on end
    setColor(losantconfig.MY_DEVICE_ID, 'red')
    setColor(losantconfig.OTHER_DEVICE_ID, 'red')

# define colors
colors = {
    'red': [1,0,0],
    'green': [0,1,0],
    'blue': [0,0,1] # not hooking up to the blue pin for now so this will be off
}

# in common anode mode, these are flipped
if(losantconfig.LED_COMMON_MODE == 'anode'):
    colors = {
        'red': [0,1,1],
        'green': [1,0,1],
        'blue': [1,1,0] # not hooking up to the blue pin for now so this will be off
    }

def setColor(deviceId, color):
    print(deviceId)
    color_to_set = colors[color]
    for index, pin in enumerate(losantconfig.LED_PINS[deviceId]):
        print('setting pin',pin,'to',index)
	GPIO.output(pin, color_to_set[index])


# set both lights to red to begin
setColor(losantconfig.MY_DEVICE_ID, 'red')
setColor(losantconfig.OTHER_DEVICE_ID,'red')

try:
    while True:
        device.loop()
        # Key
        key_state = not GPIO.input(losantconfig.KEY_PIN) # False is when the key is turned, so we're flipping it for sanity's sake
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
        button_state = not GPIO.input(losantconfig.BUTTON_PIN) # False is when the button is pressed, so we're flipping it for sanity's sake
        if button_state == True and is_button_pressed == False:
        # state changed to pressed
            print('Button Pressed')
            is_button_pressed = True
            if device.is_connected():
                # send this state via REST
                state = {'data': {'isButtonPressed': is_button_pressed}}
                client.device.send_state(deviceId=losantconfig.MY_DEVICE_ID,
                    applicationId=app_id, deviceState=state)

        if button_state == False and is_button_pressed == True:
        # state changed to released
            print('Button Released')
            is_button_pressed = False
            # no need to send state here
        time.sleep(0.02) # wait before executing again

except KeyboardInterrupt:
    GPIO.cleanup()
