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

## command line testing

Much of the vent functionality can be tested via the command line.  

```
sudo ./vent.py -h
```

will print out diffrent vent parameters that can be tested

```
usage: vent.py [-h] [-m MODE] [-a ASSIST] [-i INSPIRE] [-e EXPIRE] [-u RAMPUP]
               [-d RAMPDN] [-s START] [-t TOP] [-p PAUSE] [-b BOTTOM]
               [-c COUNT] [-f FIO2] [-v VTIDAL] [-w PWAIT] [-x PCROSS]

Run vent

optional arguments:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  0 = Demo 1 = Volume Control 2 = Pressure Control
  -a ASSIST, --assist ASSIST
                        pressure trigger for assist 0 = no assist
  -i INSPIRE, --inspire INSPIRE
                        seconds of inspiration time
  -e EXPIRE, --expire EXPIRE
                        seconds of expiration time
  -u RAMPUP, --rampup RAMPUP
                        seconds to ramp from <start> to <top>
  -d RAMPDN, --rampdn RAMPDN
                        seconds to ramp from <top> to <pause>
  -s START, --start START
                        percent open at start of breathing cycle
  -t TOP, --top TOP     percent open at peak of breathing cycle
  -p PAUSE, --pause PAUSE
                        percent open at pause in breathing cycle
  -b BOTTOM, --bottom BOTTOM
                        percent open at end of breathing cycle
  -c COUNT, --count COUNT
                        number of breathing cycles
  -f FIO2, --fio2 FIO2  fio2
  -v VTIDAL, --vtidal VTIDAL
                        tidal volume
  -w PWAIT, --pwait PWAIT
                        seconds to wait before closing peep
  -x PCROSS, --pcross PCROSS
                        peep crossing threshold
```

For example if you wanted to test
 - 1 second of inspire time
 - 90% air flow
 - with a 0.2 second peep time
 - for 10 cycles

You would run the command

```
sudo ./vent.py -c 10 -t 90 -w 0.2 -x 0.1
```

Note: the `-x -1` sets the peep pressure threshold to -1 to set the auto peep to trigger at -1 cmH20.  This is useful when testing the system with no airflow.
