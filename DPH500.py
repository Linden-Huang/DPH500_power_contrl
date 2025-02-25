# -*- coding: utf-8 -*-
import time
import serial
import struct
from binascii import *
from crcmod import *


class FunCode:
    ReadCode = 0x03  # 读寄存器数据
    WriteSingle = 0x06  # 写单个寄存器
    WriteMul = 0x10  # 写多个寄存器


class DPH500Control:
    def __init__(self):
        super(DPH500Control, self).__init__()
        self.address = 0x01  # 地址为1 的从机
        self.dhp_ser = None  # 状态
        self.port = None

    def is_open(self):
        return self.dhp_ser and self.dhp_ser.is_open

    def dph500_open(self, dph_port):  # 打开端口 连接端口
        print ('dph500_open:', dph_port)
        try:
            if self.dhp_ser is None or self.dhp_ser is False:
                self.dhp_ser = serial.serial_for_url(dph_port, baudrate=9600, timeout=2, stopbits=1)
            if self.dhp_ser.is_open:
                print('dph500_open_succeed=>', self.dhp_ser)
                return True
            else:
                print('dph500_open_fail=>', self.dhp_ser)
                return False
        except Exception as e:
            self.dhp_ser = None
            print('{0} dhp500_open err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def is_open(self):
        return self.dhp_ser and self.dhp_ser.is_open

    def dph500_close(self):  # 关闭端口 断开端口
        try:
            if self.dhp_ser.is_open:
                self.dhp_ser.close()
        except Exception as e:
            print('{0} dhp500_close err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def dph500_write(self, cmd: bytes):
        try:
            if self.dhp_ser and self.dhp_ser.is_open:
                if cmd is not None:
                    self.dhp_ser.flushInput()
                    time.sleep(0.5)
                    self.dhp_ser.write(cmd)
                    # print('{0} dhp500 write: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(cmd)))
        except Exception as e:
            print('{0} dhp500_write err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def dph500_read(self):
        try:
            if self.dhp_ser and self.dhp_ser.is_open:
                recv = b''
                start_time = int(time.time())
                while int(time.time()) - start_time < 1.2:
                    count = self.dhp_ser.inWaiting()  # 获取串口缓冲区数据
                    if count != 0:
                        recv = recv + (self.dhp_ser.read(self.dhp_ser.in_waiting))  # 读出串口数据
                        break
                # print('{0} dhp500_read: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(recv)))
                return recv
        except Exception as e:
            print('{0} dhp500_read err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def dph500_get_current(self):
        try:
            if self.dhp_ser and self.dhp_ser.is_open:
                cmd = b'\x01\x03\x00\x02\x00\x02\x65\xcb'
                recv = b'\x01\x03\x04'
                voltage = None
                current = None
                self.dph500_write(cmd)
                res = self.dph500_read()
                head_index = res.find(recv)
                if len(res) >= 9 and head_index != -1:
                    voltage = struct.unpack('>h', res[head_index + 3:head_index + 5])[0] / 100
                    current = struct.unpack('>h', res[head_index + 5:head_index + 7])[0] / 1000
                return voltage, current # 电压 v , 电流 A
        except Exception as e:
            print('{0} dhp500_get_current err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def modbus_crc(self, data: bytes):
        crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        readcrcout = crc16(unhexlify(data.hex()))
        return struct.pack("<H", readcrcout)

    def dph500_set_voltage(self, set_voltage=3.8):
        try:
            if self.dhp_ser and self.dhp_ser.is_open:
                cmd = b'\x01\x06\x00\x00'
                v_tobyte = struct.pack(">H", int(set_voltage * 100))
                crc = self.modbus_crc(cmd + v_tobyte)
                send_cmd = cmd + v_tobyte + crc
                voltage = 0
                self.dph500_write(send_cmd)
                res = self.dph500_read()
                head_index = res.find(cmd)
                if len(res) >= 8 and head_index != -1:
                    voltage = struct.unpack('>h', res[head_index + 4:head_index + 6])[0] / 100
                if voltage == set_voltage:
                    return voltage
                else:
                    return False
            else:
                return False
        except Exception as e:
            print('{0} dhp500_set_voltage err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def dph500_set_voltage_current(self, voltage=3.8, current=1.5):  # 单位 V A
        try:
            if self.dhp_ser and self.dhp_ser.is_open:
                cmd = b'\x01\x10\x00\x00\x00\x02\x04'
                recv = b'\x01\x10\x00\x00\x00\x02\x41\xc8'
                vol_byte = struct.pack(">H", int(voltage * 100))
                cur_byte = struct.pack(">H", int(current * 1000))
                crc = self.modbus_crc(cmd + vol_byte + cur_byte)
                send_cmd = cmd + vol_byte + cur_byte + crc
                self.dph500_write(send_cmd)
                res = self.dph500_read()
                head_index = res.find(recv)
                if len(res) >= 8 and head_index != -1:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print('{0} dph500_set_voltage_current err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))

    def dph500_on_off(self, status: int):
        try:
            if self.dhp_ser and self.dhp_ser.is_open:
                cmd = b'\x01\x06\x00\x09'
                status_byte = struct.pack(">H", status)
                crc = self.modbus_crc(cmd + status_byte)
                send_cmd = cmd + status_byte + crc
                self.dph500_write(send_cmd)
                res = self.dph500_read()
                head_index = res.find(send_cmd)
                if len(res) >= 8 and head_index != -1:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print('{0} dph500_on_off err: {1}'.format(time.strftime('[%Y-%m-%d-%H:%M:%S]'), str(e)))
