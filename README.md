# vent

Vent is a collaboration between CIONIC, FuseProject, and Accenture to build a highly modular low cost ventilator 
to help address a potential capacity shortfall in emergency COVID-19 response.

Our design is a finalist in the [Covent-19 Challenge](https://www.coventchallenge.com/)

## pi development

Vent runs on the [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) 

### pi setup

```
git clone https://github.com/cionicwear/vent.git
cd vent
sudo pip3 install -r requirements.txt
```

  
### pi running

There are three different processes that need to be 

1. start the ui process
```
sudo python3 ui.py
```
The UI process manages the rotary encoder and buttons translating them to system wide keystrokes

2. start the vent process
```
sudo python3 vent.py
```
The vent process is the primary control point that manges the web server, sensors, and valve.

3. launch chromium 
```
DISPLAY=:0 chromium-browser http://localhost:3000 --kiosk --disk-cache-dir=/dev/null
```
The chromium browser serves as the surface for operator input and display of sensor values


## desktop development

In order to enable hardware free development the vent can be run locally via docker.
```
git clone https://github.com/cionicwear/vent.git
cd vent
docker-compose up
```
