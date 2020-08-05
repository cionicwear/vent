# Hardware Specifications

There have been two revisions to the hardware reference design

* RevA initial concept
* RevB functional prototype

## RevB Functional Prototype

The RevB reference design made rapid deployment even easier by leveraging off the shelf breakout boards for almost all components.

[Mechanical Assembly](hardware/mechanical/RevB.pdf)

[Electrical Schematic](hardware/electrical/RevB.pdf)

[Bill of Materials](hardware/bom/RevB.csv)

Electronics

- 1x [Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) for compute
- 1x [Raspberry Pi Touch Display](https://www.raspberrypi.org/products/raspberry-pi-touch-display/) for UI
- 4x [Adafruit LPS33HW Pressure Sensor](https://www.adafruit.com/product/4414) for measuring pressure and flow
- 1x [Adafruit Motor Bonnet](https://www.adafruit.com/product/4280) for driving solenoids and linear actuator
- 2x [SMC PVQ31-6G-40-01-N Solenoid](https://www.smcpneumatics.com/pdfs/PVQ.pdf) for control of O2 and Room Air
- 1x [Actuonix L12-10-50-12-P Linear Actuator](https://s3.amazonaws.com/actuonix/Actuonix+L12+Datasheet.pdf) for controlling PEEP
- 1x [Sensoronics SS-26 O2 Sensor](https://www.sensoronics.com/products/ss-26-replaces-msa-806572) for O2 Sensing
- 1x [Sparkfun QWIIC ADS1105](https://www.sparkfun.com/products/15334) to read analog O2 and actuator position sensors
- 1x [GOOLOO GP37-plus](http://www.gooloo.com/products-detail.php?ProId=41) for power management and battery backup
- 2x [B3F-1020 Tactile Switch](https://www.digikey.com/product-detail/en/omron-electronics-inc-emc-div/B3F-1020/SW402-ND/44059) for UI
- 1x [PEC11R-4015F-S0024 Rotary Encoder](https://www.digikey.com/product-detail/en/bourns-inc/PEC11R-4015F-S0024/PEC11R-4015F-S0024-ND/4499668) for UI
- 1x [CEM-1203_42 Audio Transducer](https://www.digikey.com/product-detail/en/cui-devices/CEM-1203-42/102-1153-ND/412412) for Alarms

