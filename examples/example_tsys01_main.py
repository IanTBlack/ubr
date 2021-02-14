'''
Rename this example to main.py before loading onto your Pico.
In order to access the TSYS01 module you will need to put tsys01.py 
on a folder labeled "ubr" on your Pico.

This example asks the TSYS01 for the temperature and converts it to other
formats once every 3 seconds.
'''
from ubr.tsys01 import TSYS01
import utime 

tsys01 = TSYS01() #Create an instance for the TSYS01.
tsys01.initialize_sensor() #This resets the sensor and gets the cal data.

while True: #Loop forever.
    celsius = tsys01.get_temperature() #Get the temp in Celsius as a float.
    fahrenheit = 1.8 * celsius + 32
    kelvin = celsius + 273.15
    
    #Cut values off at the thousandths mark for formatting.
    fmt = "{:.3f}"
    celsius = fmt.format(celsius)
    fahrenheit = fmt.format(fahrenheit)
    kelvin = fmt.format(kelvin)
    
    msg = "Celsius: {} | Fahrenheit: {} | Kelvin: {}"
    print(msg.format(celsius,fahrenheit,kelvin))
    utime.sleep(3) #Wait 3 seconds before going through the loop again.