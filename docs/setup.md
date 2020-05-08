# vent

Tested Version 
Raspian Buster
 
## Install Raspian Buster

1. Download image from https://www.raspberrypi.org/downloads/raspbian/
1. Using Etcher - write image to SD card
1. Insert newly flashed SD Card
1. Connect keyboard and monitor
1. Connect Power
1. Login pi/raspberry

## Configure device

```
sudo raspi-config
```

1. Hostname - Change to help distinguish from other devices on the network
1. Password - Change because it is always bad to have default credentials
1. Interfaces
   * SSH
   * I2C
   * Advanced
     * Expand Filesystem
1. Finish (will reboot)


## Add to Wifi network

https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)

Open the wpa-supplicant configuration file in nano:

```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Go to the bottom of the file and add the following:

```
network={
    ssid="testing"
    psk="testingPassword"
}
```

## Install the tools you need for development
```
sudo apt-get update
sudo apt-get install emacs
sudo apt-get install git
```

## Run vent

Clone vent repository
```
git clone https://github.com/cionicwear/vent.git
```

Install dependencies
```
cd vent
sudo pip3 install -r requirements.txt
```

Start the pigpio daemon used for PWM
```
sudo pigpiod
```

Run vent server
```
sudo python3 vent.py
```

this will start the following processes
- sensor loop
- ui loop
- web server

Launch Chromium
```
DISPLAY=:0 chromium-browser http://localhost:3000 -kiosk
```




