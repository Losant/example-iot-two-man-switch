# Losant IoT Two-Man Switch

Create a two-man (nuclear launch style) Internet-connected switch using two
Raspberry Pi 3's and Losant's MQTT and REST Python packages. Two separate
users must turn a key, and then and only then can a user press a button
to kick off a process in a Losant workflow.

## Losant Setup

1.  [Sign in](https://accounts.losant.com) to your Losant account or [create a new one](https://accounts.losant.com/create-account).
2.  Create a new application. Name it anything you would like.
3.  Create two new devices within your application. Each device must have the tag ```type=twoManSwitch``` and attributes ```isButtonPressed``` (type Boolean) and ```isKeyTurned``` (type Number).
4.  For each device, set up a separate application key and secret that is scoped only to the one device. Make sure to copy your device IDs, application keys and application secrets to a safe place for later use.
5.  Create a new workflow, naming it anything you like, and then import the workflow {{{GIST LINK}}}.
6.  Add your phone number under the "Globals" tab or edit the workflow to include your own action to kick off when the button is successfully pressed. Also, make sure that all nodes are valid, especially that the workflow triggers and gauge query nodes include the tags you set up when creating your devices.

## Wiring Setup

See the post about the two-man switch on the Losant blog for a
complete wiring diagram and more information about the necessary
components and their connections.

## Device / Application Setup

You will need to go through these steps on each of your
connected devices.

1.  Once your Raspberry Pi is set up and connected to the Internet, clone this repository onto your device.
2.  From the root of the project directory, run ```pip install -r requirements.txt``` to install the Losant dependencies.
3.  Run ```cp losantconfigexample.py losantconfig.py``` to copy the example config file to a new file called "losantconfig.py".
4.  Open the new config file in your favorite editor and update the **device ID**, **application ID**, **application secret** and **other Pi device ID**. Also, make sure to set your RGB LED type and any of the GPIO pins you may have changed from the default wiring.
