
import DPH500 as DPH500

import time

class ElectricalSource():
    def __init__(self):
        self.select = 0 # 0: 程控电源 1:DPH500
        self.mydph500 = DPH500.DPH500Control()  # dph500 实例
        self.com = None

    def __del__(self):
        self.close()

    def open(self, voltage = 3.0, select=0, com=None): # 默认电压为3.0v,默认电源为程控电源
        if self.is_open():
            return True
        self.select = select
        if select == 1 and com: # DPH500
            self.com = com # 电源端口
            if self.com and '请选择' not in self.com and len(self.com) > 0:
                if (self.mydph500.dph500_open(self.com)):
                    self.mydph500.dph500_set_voltage_current(voltage, 0.5)
                    self.mydph500.dph500_on_off(1)
                else:
                    print ('DPH500 open fail')
        return self.is_open()
            
    def close(self):
        if self.select == 1 and self.mydph500.dhp_ser:
            return self.mydph500.dph500_close()
        return True

    # 获取电流
    def get_current(self):  # mA
        try:
            if self.select == 1 and self.mydph500.dhp_ser:
                return self.mydph500.dph500_get_current()[1] * 1000 
            return None
        except:
            return None
    # 设置电压
    def set_voltage(self, voltage=12.0):
        if self.select == 1 and self.mydph500.dhp_ser:
            return self.mydph500.dph500_set_voltage(voltage)
        return None
    
    # 是否存在电源
    def is_open(self):
        # print ('ElectricalSource is_open: ', 'power=>', self.my_power.is_open, 'dph=>', self.mydph500.dhp_ser)
        if self.select == 1:
            return self.mydph500.dhp_ser and self.mydph500.dhp_ser.is_open

    def __enter__(self):
        self.open()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        



