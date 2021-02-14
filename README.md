# ubr
ubr is a Micropython 1.14 compatible port of Python 3 libraries developed for Blue Robotics sensors.

## Modules
### crawler
A tool for identifying the I2C port that an address is connected to.

### TSYS01
This module is for driving the Blue Robotics TSYS01 Celsius Fast Response Temperature Sensor.

## Testing
Testing for these modules was performed on a Raspberry Pi Pico (Micropython v1.14).


## References
[Raspberry Pi Pico Pinout](https://datasheets.raspberrypi.org/pico/Pico-R3-A4-Pinout.pdf)

[TE MS5837 Manual](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FMS5837-30BA%7FB1%7Fpdf%7FEnglish%7FENG_DS_MS5837-30BA_B1.pdf%7FCAT-BLPS0017)

[TE TSYS01 Manual](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FTSYS01%7FA%7Fpdf%7FEnglish%7FENG_DS_TSYS01_A.pdf%7FG-NICO-018)
