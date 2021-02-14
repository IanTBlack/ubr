import machine
import umath
import utime

class MS5837():
    def __init__(self,model,address=0x76):
        self.set_i2c_parameters()
        self._reset = 0x1E
        self._read = 0x00 
        self._osr = [256,512,1024,2048,4096,8192] #Resolution options.
        self._conv_d1 = [0x40,0x42,0x44,0x46,0x48,0x4A] #Indexed by OSR.
        self._conv_d2 = [0x50,0x52,0x54,0x56,0x58,0x5A] #Indexed by OSR.
        self._wait_time = [1,2,3,5,10,19] #Max values in ms per manual.
        self._prom = [0xA0,0xA2,0xA4,0xA6,0xA8,0xAA,0xAC] #PROM addresses.
        self._address = address
        self._model = model.upper()
        
    def set_i2c_parameters(self,id=0,
                           scl=machine.Pin(9),sda=machine.Pin(8),
                           frequency=400000):
        self.i2c = machine.I2C(id=id,scl=scl,sda=sda,freq=frequency)
        
    def reset_sensor(self):
        self.i2c.writeto(self._address,bytearray([self._reset]))
        utime.sleep_ms(10)
                         
    def _get_calibration_coefficients(self):
        self.cal_coeffs = []
        for c in self._prom:
            self.i2c.writeto(self._address,bytearray([c]))
            raw = self.i2c.readfrom(self._address,2)
            value = int.from_bytes(raw,"big")
            self.cal_coeffs.append(value)
                         
    def _crc4(self,n_prom):
        n_rem = 0
        n_prom[0] = ((n_prom[0]) & 0x0FFF)
        n_prom.append(0)   
        for i in range(16):
            if i%2 == 1:
                n_rem ^= ((n_prom[i>>1]) & 0x00FF)
            else:
                n_rem ^= (n_prom[i>>1] >> 8)
                
            for n_bit in range(8,0,-1):
                if n_rem & 0x8000:
                    n_rem = (n_rem << 1) ^ 0x3000
                else:
                    n_rem = (n_rem << 1)
        n_rem = ((n_rem >> 12) & 0x000F)       
        return n_rem ^ 0x00                         
                         
    def initialize_sensor(self):
        self.reset_sensor()
        self._get_calibration_coefficients()
        check = (self.cal_coeffs[0] & 0xF000) >> 12
        if check != self._crc4(self.cal_coeffs):
            print("PROM read error, cyclic redundancy check failed.")
            return False
        else:
            return True
        
    def _get_data(self):
        self._d1 = 0 
        self._d2 = 0
        idx = self._osr.index(self._resolution) 
        conv_d1_addr = self._conv_d1[idx]
        conv_d2_addr = self._conv_d2[idx]
        wait = self._wait_time[idx]
        
        self.i2c.writeto(self._address,bytearray([conv_d1_addr]))
        utime.sleep_ms(wait)
        d1 = self.i2c.readfrom_mem(self._address,self._read,3) 
        print(int.from_bytes(d1,"big"))
        self._d1 = d1[0] << 16 | d1[1] << 8 | d1[2] 
        print(self._d1)

        self.i2c.writeto(self._address,bytearray([conv_d2_addr])) 
        utime.sleep_ms(wait) 
        d2 = self._i2c.readfrom_mem(self._address,self._read,3) 
        self._d2 = d2[0] << 16 | d2[1] << 8 | d2[2]    
        
    def _first_order_calculation(self):
        c1 = self.cal_coeffs[1]
        c2 = self.cal_coeffs[2]
        c3 = self.cal_coeffs[3]
        c4 = self.cal_coeffs[4]
        c5 = self.cal_coeffs[5]
        c6 = self.cal_coeffs[6]     
        self._dt = self._d2 - c5 * 2**8
        if self._model == "30BA":
            self._sens = c1*2**15+(c3*self._dt)/2**8
            self._off = c2*2**16+(c4*self._dt)/2**7
        elif self._model == "02BA":
            self._sens = c1*2**16+(c3*self._dt)/2**7
            self._off = c2*2**17+(c4*self._dt)/2**6        
        self._temp = (2000 + self._dt * c6/(2**23)) #1st order.
               
    def _second_order_calculation(self):
        if self._model == "30BA":
            if self._temp/100 < 20:
                ti = 3 * self._dt**2 / 2**33
                offi = 3 * (self._temp - 2000)**2 / 2**1
                sensi = 5 * (self._temp - 2000)**2 / 2**3
                if self._temp/100 < -15:
                    offi = offi + 7 * (self._temp + 1500)**2
                    sensi = 4 * (self._temp + 1500)**2
            elif self._temp/100 >= 20:
                ti =  2* self._dt**2 / 2**37
                offi = 1 * (self._temp-2000)**2 / 2**4
                sensi = 0               
            off2 = self._off - offi
            sens2 = self._sens - sensi
            self.p2 = (((self._d1 * sens2)/2**21-off2)/2**13)/10 #2nd order.         
        elif self._model == "02BA":
            if self._temp/100 < 20:
                ti = 11 * self._dt**2 / 2**35
                offi = 31 * (self._temp - 2000)**2 / 2**3
                sensi = 63 * (self._temp - 2000)**2  / 2**5       
            off2 = self._off - offi
            sens2 = self._sens - sensi        
            self.p2 = (((self._d1 * sens2)/2**21-off2)/2*15)/100 #2nd order.       
        self.temp2 = (self._temp - ti)/100 #2nd order.
    
    def get_temperature(self,resolution=8192):
        self._resolution = resolution
        self._get_data()
        self._first_order_calculation()
        self._second_order_calculation()    
        return self.temp2

    def get_absolute_pressure(self,resolution=8192):
        self._resolution = resolution
        self._get_data()
        self._first_order_calculation()
        self._second_order_calculation()
        absp = self.p2/100
        return absp
        
    def get_pressure(self,sea_level_reference=10.1325,resolution=8192):
        absp = self.absolute_pressure(resolution)
        p = absp - sea_level_reference
        if p < 0:
            p = 0
        return p
    
    def get_depth(self,sea_level_reference=10.1325,resolution=8192, 
              lat=45.00000,geo_strf_dyn_height=0,sea_surface_geopotential=0):     
        """Compute depth using TEOS-10.
        @param sea_level_reference -- pressure of atmo at sea level in dbar.
        @param resolution -- the resolution option of the sensor. 
        @param lat -- latitude (DD) of deployment, used in gsw_z_from_p
        @param geo_strf_dyn_height -- dynamic height anomaly (m^2/s^2)
        @param sea_surface_geopotential -- geopotential at zero sea pressure 
        @return -- depth in meters as a float
        """        
        self._lat = lat
        self._geo_strf_dyn_height = geo_strf_dyn_height
        self._sea_surface_geopotential = sea_surface_geopotential
        p = self.pressure(sea_level_reference = sea_level_reference,
                          resolution = resolution)
        z = self._gsw_z_from_p(p)
        depth = self._gsw_depth_from_z(z)                
        if depth < 0:
            depth = 0.00    
        return depth    
    
  
    def _gsw_z_from_p(self,p):        
        """Compute height using pressure.
        z = 0 is sea level. -z is going DOWN into the ocean.        
        @param p -- pressure in decibars
        @return -- z in meters.
        """     
        gamma = 2.26e-7
        deg2rad = umath.pi/180
        sinlat = umath.sin(self._lat*deg2rad)
        sin2 = sinlat**2
        b = 9.780327*(1.0 + (5.2792e-3 + (2.32e-5*sin2))*sin2); 
        a = -0.5 * gamma * b
        c = (self._gsw_enthalpy_sso_0(p) 
            - (self._geo_strf_dyn_height 
            + self._sea_surface_geopotential))
        z = -2 * c / (b + umath.sqrt(b * b - 4 * a *c))
        return z
             
    def _gsw_enthalpy_sso_0(self,p):     
        """Compute enthalpy at Standard Ocean Salinity (SSO).  
        Assumes a Conservative Temperature of zero degrees Celsius.
        @param p -- pressure in decibars
        @return -- the enthalpy value relative to SSO.
        """     
        z = p*1e-4
        h006 = -2.1078768810e-9
        h007 =  2.8019291329e-10
        dynamic_enthalpy_sso_0_p = (z * (9.726613854843870e-4 
                                        + z * (-2.252956605630465e-5 
                                        + z * (2.376909655387404e-6 
                                        + z * (-1.664294869986011e-7 
                                        + z * (-5.988108894465758e-9 
                                        + z * (h006 + h007*z)))))))
        enthalpy_sso_0 = dynamic_enthalpy_sso_0_p*1e8   
        return enthalpy_sso_0 
    
    def _gsw_depth_from_z(self,z):   
        """Compute depth from height (z).
        @param z -- a negative z value denoting depth in the ocean.
        @return -- depth in meters.
        """        
        depth = -z
        return depth