# -*- coding: utf-8 -*-
import pyvisa as visa
import time


def replace_escape_sequences(s):
    return s.replace("\\n", "\n").replace("\\r", "\r")


class GpibControl:
    def __init__(self):
        super(GpibControl, self).__init__()
        self.visa_rm = None
        self.visa_ud = None

    def device_open(self, gpio_add='GPIB0::5::INSTR'):
        try:
            res = False
            self.visa_rm = visa.ResourceManager()
            visa_list = self.visa_rm.list_resources()  # type:tuple
            if gpio_add in visa_list:
                self.visa_ud = self.visa_rm.open_resource(gpio_add)  # You need to specify your device here.
                res = True
            return res
        except Exception as e:
            print('{0} device_open err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def device_close(self):
        try:
            self.visa_ud.close()
        except Exception as e:
            print('{0} device_close err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def device_write(self, cmd):
        try:
            cmd = replace_escape_sequences(cmd)
            self.visa_ud.write(cmd)
        except Exception as e:
            print('{0} device_write err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def device_read(self):
        try:
            ret = self.visa_ud.read()
            return ret
        except Exception as e:
            print('{0} device_read err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def set_voltage(self, voltage: float):
        try:
            protect_cmd = 'VOLT:PROT {0};:VOLT:PROT:STAT ON'.format(15)
            voltage_cmd = 'OUTP1 ON;:VOLT1 {0}'.format(voltage)
            self.device_write(protect_cmd)
            self.device_write(voltage_cmd)
        except Exception as e:
            print('{0} set_voltage err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def get_current(self):
        try:
            self.visa_ud.write('MEAS:CURR?')
            recv = (self.visa_ud.read()).split('\n')[0]
            if -1 != recv.find("9.91000E+37"):
                self.visa_ud.write("SENS:CURR:RANG MAX")
                self.visa_ud.write("MEAS:CURR?")
                recv = self.visa_ud.read()
                print('{0} current too big: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), recv))
            else:
                self.visa_ud.write("SENS:CURR:RANG MAX")
            ret_current = float(recv) * 1000
            return ret_current
        except Exception as e:
            print('{0} set_voltage err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def get_average_current(self, span):
        start_time = time.time()
        count = 0
        total = 0
        while span >= (time.time() - start_time):  # 计算一段时间内的均值
            current_value = self.get_current()
            total = total + current_value
            count = count + 1
        if 0 < count:
            return total/count
        return 0

    def set_current_range(self, a_range: float):
        a_range = 2.0 if a_range > 2.0 else a_range
        a_range = 0.2 if a_range < 0.2 else a_range
        set_range_cmd = 'SENS:CURR:RANG {0:F2}'.format(a_range)
        self.visa_ud.write(set_range_cmd)

    def init_dc_source(self):
        self.visa_ud.write("*RST;*CLS")
        self.visa_ud.write("DISP:MODE NORM;:DISP ON;:DISP:CHAN 1")
        self.visa_ud.write("SENS:CURR:DET ACDC")
        self.visa_ud.write("SENS:CURR:RANG 1.0;:SENS:FUNC \"CURR\"")
        self.visa_ud.write("OUTP:STAT ON")
        self.visa_ud.write("OUTP:TYPE LOW")
        self.visa_ud.write("VOLT:PROT 6;:VOLT:PROT:STAT ON")
        self.visa_ud.write("CURR 2")
        self.visa_ud.write("INST:COUP:OUTP:STAT NONE")

    def init_dc_source_extend(self):
        self.visa_ud.write("*RST;*CLS")
        self.visa_ud.write("DISP:MODE NORM;:DISP ON;:DISP:CHAN 1")
        self.visa_ud.write("SENS:CURR:DET ACDC")
        self.visa_ud.write("SENS:CURR:RANG 0.001;:SENS:FUNC \"CURR\"")
        self.visa_ud.write("OUTP:STAT ON")
        self.visa_ud.write("OUTP:TYPE LOW")
        self.visa_ud.write("VOLT:PROT 6;:VOLT:PROT:STAT ON")
        self.visa_ud.write("CURR 2")
        self.visa_ud.write("INST:COUP:OUTP:STAT NONE")

    def reset_dc(self):
        self.visa_ud.write("*RST;*CLS")
