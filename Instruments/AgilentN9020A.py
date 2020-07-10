import sys
import time
import os
import re

from pyvisa import *

def visa_address_for_ip(ip_address):
    return 'TCPIP0::%s::inst0::INSTR' % ip_address

#####################################################
# Agilent N9020A MXA Class                          #
# Used to control an Agilent Signal Analyzer        #
#                                                   #
#####################################################
class AgilentN9020A:
    gpib_address = 'GPIB0::18::INSTR'
    tcpip_address = 'TCPIP0::192.168.1.6::inst0::INSTR'
    verbose = 0
    timeout = 60

    def __init__(self, instr_address = gpib_address, verbose = 0):
        self.verbose = verbose
        if self.verbose != 0:
            print("Request connection to analyzer on address: " + str(instr_address))
        self.rm = ResourceManager()
        self.resource = self.rm.open_resource(instr_address) #("GPIB::" + str(gpib_address))
        print(self.resource.query("*IDN?").rstrip(),'\n')

    def reset(self):
        if self.verbose != 0:
            print("Resetting known state")
        self.resource.write("*RST")

        if self.verbose != 0:
            print("Reset Done")


    def close(self):
        if self.verbose != 0:
            print("Closing instrument")
        self.resource.close()
    def open(self):
        if self.verbose != 0:
            print("Opening instrument")
        self.resource.open()        

    # Low-level commands to access it all (should you wish to experiment)
    def ask(self, text):
        return self.resource.ask(text)
    def ask_for_values(self, *args, **kwargs):
        return self.resource.ask_for_values(*args, **kwargs)
    def read(self):
        return self.resource.read()
    def write(self, text):
        return self.resource.write(text)

    # Some common higher level functionality:
    def set_center_frequency(self, frequencyMHz):
        return self.resource.write(":SENSe:FREQuency:CENTer %f MHz" % frequencyMHz)
    def set_span(self, spanMHz):
        return self.resource.write(":SENSe:FREQuency:SPAN %f MHz" % spanMHz)
    def set_sweep_time(self, timeS):
        return self.resource.write(":SENSe:SWEep:TIME %f" % timeS)

    def set_trace_format_ascii(self):
        return self.resource.write(":FORMat:TRACe:DATA ASCii")
    def set_trace_format_float(self):
        self.resource.write(":FORMat:TRACe:DATA REAL,32")
        return self.resource.write(":FORMat:BORDer SWAP")

    def read_trace(self, traceNum):
        self.resource.write(":TRACe:DATA? TRACE%d" % traceNum)
        return self.resource.read()

    def set_burst_mode(self):
        return self.resource.write(":CONF:TXP")
    def set_frequency(self, freq):
        return self.resource.write(":SENS:FREQ:CENT %d" % freq)
    def set_avg_hold_state(self, state):
        return self.resource.write(":TXP:AVER %s" % state)
    def set_avg_hold_num(self, num):
        return self.resource.write(":TXP:AVER:COUN %d" % num)
    def set_avg_hold_mode(self, mode):
        return self.resource.write(":TXP:AVER:TCON %s" % mode)
    def set_avg_type(self, type):
        return self.resource.write(":TXP:AVER:TYPE %s" % type)
    def set_threshold_type(self, type):
        return self.resource.write(":TXP:THR:TYPE %s" % type)
    def set_threshold_lvl(self, level):
        return self.resource.write(":TXP:THR %e" % level)
    def set_measure_method(self, method):
        return self.resource.write(":TXP:THR:TYPE %s" % method)
    def set_bandwidth(self, bw):
        return self.resource.write(":TXP:BAND %s" % bw)
    def set_bar_graph(self, state):
        return self.resource.write("DISP:TXP:BARG %s" % state)
    def set_bw_res(self, res):
        return self.resource.write("SENS:BAND:RES %s" % res)
    def set_freq_span(self, span):
        return self.resource.write("SENS:FREQ:SPAN %s" % span)
    def set_sweep_time(self, sweep_time):
        return self.resource.write("SWE:TIME %e" % sweep_time)
    def set_trigger_source(self, source):
        return self.resource.write(":TRIG:SOUR %s" % source)
    def set_trigger_lvl(self, level):
        return self.resource.write(":TRIG:VID:LEV: %e" % level)
    def set_trigger_slope(self, slope):
        return self.resource.write(":TRIG:SLOP %s" % slope)
    def set_trigger_delay_state(self, state):
        return self.resource.write(":TRIG:RFB:DEL:STAT %s" % state)
    def set_trigger_delay(self, delay):
        return self.resource.write(":TRIG:DEL %e" % delay)
    def read_power(self):
        self.resource.write(':FETC:TXP?')
        return self.resource.read()


    def get_error(self):
        return self.resource.query(":SYStem:ERRor?")

