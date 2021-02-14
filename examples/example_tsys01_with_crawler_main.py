'''
Rename this example to main.py before loading onto your Pico.

This example asks searches all of the I2C ports until the address
for the TSYS01 is found. Temperatures is then requested from the TSYS01
every 3 seconds.
'''
from ubr import crawler
from ubr.tsys01 import TSYS01
import utime 

#Search for the I2C port that the TSYS01 is on.
#Default address for the BR TSYS01 is 0x77 or 119.
i2c_params = crawler.crawl_I2C_until(0x77)

tsys01 = TSYS01() #Create an instance for the TSYS01.
tsys01.set_i2c_parameters(id=i2c_params[0],scl=i2c_params[2],sda=i2c_params[1])

tsys01.initialize_sensor() #This resets the sensor and gets the cal data.

while True: #Loop forever.
    celsius = tsys01.get_temperature() #Get the temp in Celsius as a float.
    fahrenheit = 1.8 * celsius + 32
    kelvin = celsius + 273.15
    
    #Cut values off at the thousandths mark.
    fmt = "{:.3f}"
    celsius = fmt.format(celsius)
    fahrenheit = fmt.format(fahrenheit)
    kelvin = fmt.format(kelvin)
    
    msg = "Celsius: {} | Fahrenheit: {} | Kelvin: {}"
    print(msg.format(celsius,fahrenheit,kelvin))
    utime.sleep(3) #Wait 3 seconds before going through the loop again.
    