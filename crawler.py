import machine

#RPI Pico I2C Options
#ID,SDA,SCL
I2C_001 = (0,machine.Pin(1),machine.Pin(0))
I2C_123 = (1,machine.Pin(2),machine.Pin(3))
I2C_045 = (0,machine.Pin(4),machine.Pin(5))
I2C_167 = (1,machine.Pin(6),machine.Pin(7))
I2C_089 = (0,machine.Pin(8),machine.Pin(9))
I2C_11011 = (1,machine.Pin(10),machine.Pin(11))
I2C_01213 = (0,machine.Pin(12),machine.Pin(13))
I2C_11415 = (1,machine.Pin(14),machine.Pin(15))
I2C_12627 = (1,machine.Pin(26),machine.Pin(27))
I2C_02021 = (0,machine.Pin(20),machine.Pin(21))
I2C_11819 = (1,machine.Pin(18),machine.Pin(19))
I2C_01617 = (0,machine.Pin(16),machine.Pin(17))
I2Cs = [I2C_001,I2C_123,I2C_045,I2C_167,I2C_089,
        I2C_11011,I2C_01213,I2C_11415,I2C_12627,I2C_02021,I2C_11819,I2C_01617]

def crawl_I2C_until(address):
    """Scan each of the I2C options until a matching address is found. 
    Very inefficient.
    @param -- the address of a I2C slave
    @return -- a tuple indicating the I2C port (id,scl,sda)."""
    for bus in I2Cs:
        print(bus)
        try:
            i2c = machine.I2C(id=bus[0],scl=bus[2], sda=bus[1])
            if address in i2c.scan():
                msg = "Address {} found on I2C bus {}"
                print(msg.format(address,bus))
                return bus
            else:
                continue
        except:
            continue