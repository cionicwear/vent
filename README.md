# vent

Vent is a collaboration between CIONIC and FuseProject to build a highly modular low cost ventilator 
to help address a potential capacity shortfall in emergency COVID-19 response.

Our design is a finalist in the [Covent-19 Challenge](https://www.coventchallenge.com/)

## pi development

The fully featured Vent has been tested to run on [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) 

The headless version has been tested to run on [Raspberry Pi 0](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)

### pi setup

```
git clone https://github.com/cionicwear/vent.git
cd vent
sudo pip3 install -r requirements.txt
```

Vent requires running two i2c busses to configure your pi
Add the following overlay to /boot/config.txt
```
dtoverlay=i2c-gpio,i2c_gpio_sda=4,i2c_gpio_scl=26,bus=3
```

  
### pi running

There are three different processes that need to be 

1. start the ui process
```
sudo ./ui.py
```
The UI process manages the rotary encoder and buttons translating them to system wide keystrokes

2. start the vent process
```
sudo ./vent.py
```
The vent process is the primary control point that manges the web server, sensors, and valve.

3. start the screen process
```
./vent.sh
```
The chromium browser serves as the surface for operator input and display of sensor values


## desktop development

In order to enable hardware free development the vent can be run locally via docker.
```
git clone https://github.com/cionicwear/vent.git
cd vent
docker-compose up
```
