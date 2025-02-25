# -*- coding: utf-8 -*-
import gpibcontrol as gpibcontrol
import iv_handleFile
import time
from threading import Thread


class DbjPower:   # 程控电源api
    def __init__(self, test_time=10):
        super(DbjPower, self).__init__()
        self.dbj_power = gpibcontrol.GpibControl()
        self.is_open = False
        self.task_thread = []
        self._test_time = test_time
        self.stop_task = False  #
        self._callback = None

    def visa_open(self):
        try:
            if iv_handleFile.DbjBaseInfo.gpib_addr is not None:
                if self.dbj_power.device_open(iv_handleFile.DbjBaseInfo.gpib_addr):
                    self.is_open = True
                    self.stop_task = False

        except Exception as e:
            print('{0} visa_open err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def visa_close(self):
        try:
            if self.is_open:
                '''for t in self.task_thread:
                    if t:
                        # t.stop()
                        t.cancel(1)
                        # t.join(2)'''
                self.stop_task = True
                self.dbj_power.reset_dc()
                print ('visa_close')
                self.is_open = False
        except Exception as e:
            print('{0} visa_close err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def visa_init_control(self, vol=12.0):
        try:
            ret = False
            if not self.is_open:
                self.visa_open()
                self.dbj_power.init_dc_source()
                self.dbj_power.set_voltage(vol)
            if self.is_open:
                ret = True
            return ret
        except Exception as e:
            print('{0} visa_init_control err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def get_current(self, get_time=1):
        try:
            if self.is_open:
                return self.dbj_power.get_average_current(get_time)
            return 0
        except Exception as e:
            print('{0} get_current err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def power_task(self, callback=None):
        try:
            i = self._test_time
            while i and self.is_open and self.stop_task is False:
                avr_current = self.get_current()
                if avr_current:
                    print('{0} avr_current: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), avr_current))
                    if callback:
                        callback(avr_current)
                    time.sleep(2)
                    i = i - 1
        except Exception as e:
            print('{0} power_task1 err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def start_power_task(self, callback=None):
        try:
            if self.is_open:
                t = Thread(target=self.power_task(callback))
                self.task_thread.append(t)
                t.start()
        except Exception as e:
            print('{0} start_power_task err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def stop_power_task(self):
        try:
            for t in self.task_thread:
                if t:
                    # t.stop()
                    t.cancel(1)
                    # t.join(2)
            self.stop_task = True
        except Exception as e:
            print('{0} stop_power_task err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def change_voltage(self, vol: float):
        try:
            if self.is_open:
                self.dbj_power.set_voltage(vol)
        except Exception as e:
            print('{0} change_voltage err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

