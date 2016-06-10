# Losant Credentials
MY_DEVICE_ID = 'my_device_id'
ACCESS_KEY = 'my_access_key'
ACCESS_SECRET = 'my_access_secret'

OTHER_DEVICE_ID = 'other_switch_device_id'

# Define our pins
BUTTON_PIN = 12
KEY_PIN = 23

# are the RGB LEDs common cathode or anode?
LED_COMMON_MODE = 'cathode'

LED_PINS = {}
LED_PINS[MY_DEVICE_ID] = [13, 19, 26] # [R, G, B]
LED_PINS[OTHER_DEVICE_ID] = [16, 20, 21] # [R, G, B]
