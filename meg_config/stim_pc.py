
import os.path as op

from expyriment import  io
from expyriment.misc._timer import get_time
# from __future__ import annotations


class StimPC(object):
    ''' 
    Class to manage the stimulation PC.
    '''
    '''
    key_exit, rt_exit = exp.keyboard.wait_char(['q'], duration=1)
    if key_exit:
        expyriment.control.end('Ending experiment')
    '''
    
    def __init__(self, port1Num, port2Num, port3Num):
      

        # only works at the MEG. WORKS ONLY IF THE SUBJECT PRESS THE RED BUTTONS ON BOTH RESPON PANELS
        self.port1 = io.ParallelPort(port1Num)
        self.port2 = io.ParallelPort(port2Num)
        self.port3 = io.ParallelPort(port3Num)
        _ = self.port1.read_status()
        _ = self.port2.read_status()
        _ = self.port3.read_status()

        self.port1_baseline_value = self.port1.read_status()
        self.port2_baseline_value = self.port2.read_status()
        self.port3_baseline_value = self.port3.read_status()
        self.port1_last_value = self.port1_baseline_value
        self.port2_last_value = self.port2_baseline_value
        self.port3_last_value = self.port3_baseline_value
      
     
    # def checkResponse(self):
    #     '''
    #     Check if subject responded.
    #     Return 0 if not; 1 or 2 if they did; and -1 if they clicked ESC
    #     '''
    #     # if userPressedEscape():
    #     #     return -1
    #     #-- Check if exactly one button was pressed

    #     # Here we apply some small tricky correction for port whose return is always non-null
    #     # TODO check for consistency.
    #     resp1 = self.port1.read_status() - self.port1_baseline_value
    #     resp2 = self.port2.read_status() - self.port2_baseline_value
    #     resp3 = self.port3.read_status() - self.port3_baseline_value

    #     if (resp1 != 0 and resp2 == 0 and resp1 != self.port1_last_value):# and resp3 == 0):
    #         self.port1_last_value = resp1
    #         print(f'port1_{resp1 + self.port1_baseline_value}')
    #         return f'port1_{resp1 + self.port1_baseline_value}'
    #     if (resp1 == 0 and resp2 != 0 and resp2 != self.port2_last_value):# and resp3 == 0):
    #         self.port2_last_value = resp2
    #         print(f'port2_{resp2 + self.port2_baseline_value}')
    #         return f'port2_{resp2 + self.port2_baseline_value}'
    #     if (resp1 == 0 and resp2 == 0 and resp3 != 0 and resp3 != self.port3_last_value):
    #         self.port3_last_value = resp3
    #         print(f'port3_{resp3 + self.port3_baseline_value}')
    #         return f'port3_{resp3 + self.port3_baseline_value}'

    #     if (resp1 != self.port1_last_value):
    #         self.port1_last_value = resp1
    #     if(resp2 != self.port2_last_value):
    #         self.port2_last_value = resp2
    #     if(resp3 != self.port3_last_value):
    #         self.port3_last_value = resp3

    #     return None


    # def wait(self,  codes=None, duration=None):

    #     """Homemade wait for MEG response buttons

    #     Parameters
    #     ----------
    #     codes : int or list, optional !!! IS IGNORED AND KEPT ONLY FOR CONSISTENCY WITH THE KEYBOARD METHOD
    #         bit pattern to wait for
    #         if codes is not set (None) the function returns for any
    #         event that differs from the baseline
    #     duration : int, optional
    #         maximal time to wait in ms
    #     no_clear_buffer : bool, optional
    #         do not clear the buffer (default = False)
    #     """
    #     start = get_time()
    #     rt = None
    #     while True:
    #         found = self.checkResponse()
    #         if found :
    #             rt = int((get_time() - start) * 1000)
    #             break

    #         if duration is not None:
    #             if int((get_time() - start) * 1000) > duration:
    #                 return None, None

    #     return found, rt


    # def check_parallel_ports():
    #     parallel_ports = []
    #     dev_dir = '/dev/'

    #     # Check common parallel port device files
    #     for i in range(10):  # Adjust the range based on the expected number of parallel ports
    #         port = f'parport{i}'
    #         if os.path.exists(os.path.join(dev_dir, port)):
    #             parallel_ports.append(os.path.join(dev_dir, port))

    #     return parallel_ports



    def send_all_triggers(self,):
        '''send 0 to 255 to the parallel port'''
        #creation d'une expérience avec expyriment
        exp = io.Experiment(name="send_all_triggers")
        # toutes les 50ms, on envoie un trigger
        for i in range(256):
            self.port1.send_code(i)
            exp.clock.wait(50)