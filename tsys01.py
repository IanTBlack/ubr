'''ubr.tsys01.TSYS01() is a class for communicating with the 
Blue Robotics TSYS01 via Micropython 1.14.
'''
import machine
import utime

class TSYS01():
    def __init__(self,address=0x77):
        '''This class defaults to bus 0, scl on pin 9, and sda on pin 8.
        To adjust it, use the set_i2c_parameters() function.
        '''
        self.set_i2c_parameters() #Set defaults.
        self._address = address
        self._reset = 0x1E
        self._convert = 0x48
        self._read = 0x00
        self._prom = [0xAA,0xA8,0xA6,0xA4,0xA2] #Order: k0,k1,k2,k3,k4
        self._sn = [0xAE,0xAC] #Order: SN7_0, SN23_8

    def set_i2c_parameters(self,id=0,
                           scl=machine.Pin(9),sda=machine.Pin(8),
                           frequency=400000):
        '''Adjust the I2C settings for the connected sensor. Default settings
        are for bus 0 at scl pin 9 and sda pin 8.
        @param id -- The bus position.
        @param scl -- The SCL pin position given as a machine.Pin() object.
        @param sda -- The SDA pin position given as a machine.Pin() object.
        @frequency -- The SCL clock frequency, by default this value
        is 4kHz per the manual.'''
        self.i2c = machine.I2C(id=id,scl=scl,sda=sda,freq=frequency)

    def reset_sensor(self):
        '''Reset the sensor from an unknown state.
        This function can be called separately if the user determines
        that the sensor is in an unknown state.'''
        self.i2c.writeto(self._address,bytearray([self._reset]))
        utime.sleep_ms(10)

    def _get_calibration_coefficients(self):
        '''Get the cal coeffs (k) from the sensor's prom.
        There is no return, but the cal coeffs are accessible
        within the object scope. The cal coeffs are in an array that
        is ordered k0,k1,k2,k3,k4.'''
        self.cal_coeffs = []
        for k in self._prom:
            self.i2c.writeto(self._address,bytearray([k]))
            raw = self.i2c.readfrom(self._address,2)
            value = int.from_bytes(raw,"big")
            self.cal_coeffs.append(value)

    def initialize_sensor(self):
        '''Initialize the sensor at the address defined at the class call.
        This is done by resetting the sensor and then requesting the
        calibration coefficients from prom so that they can be used
        in computing the temperature.'''
        self.reset_sensor()
        self._get_calibration_coefficients()

    def _read_adc(self):
        '''Request a conversion from the sensor and
        get a 24 bit word ADC response.'''
        self.i2c.writeto(self._address,bytearray([self._convert]))
        utime.sleep_ms(10) #Max conversion time is 9.04ms per manual.
        self.i2c.writeto(self._address,bytearray([self._read]))
        raw = self.i2c.readfrom(self._address,3)
        self._adc24 = int.from_bytes(raw,"big")

    def _adc2temp(self):
        '''Take the 24 bit word, convert to 16 bit,
        and then compute temperature in Celsius using the equation provided
        in the manual.'''
        k0 = self.cal_coeffs[0] #Coeffs are indexed per __init__.
        k1 = self.cal_coeffs[1]
        k2 = self.cal_coeffs[2]
        k3 = self.cal_coeffs[3]
        k4 = self.cal_coeffs[4]
        adc16 = self._adc24/256
        self.t = (-2 * k4 * 10**-21 * adc16**4
                  + 4  * k3 * 10**-16 * adc16**3
                  + -2 * k2 * 10**-11 * adc16**2
                  + 1  * k1 * 10**-6  * adc16
                  + -1.5 * k0 * 10**-2)

    def get_temperature(self):
        '''Get the temperature in Celsius.
        @return -- The temperature in Celsius as a float.'''
        self._read_adc()
        self._adc2temp()
        return self.t