from expyriment import  io, design
from expyriment.misc._timer import get_time
import os.path as op
import expyriment

'''
key_exit, rt_exit = exp.keyboard.wait_char(['q'], duration=1)
if key_exit:
    expyriment.control.end('Ending experiment')
'''


class MEG_ports(object):
    port1 = []
    port2 = []
    port3 = []


    def __init__(self, exp, port1Num, port2Num, port3Num):
        # from psychopy import parallel

        self.exp = exp
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


    #----------------------------------------
    # Check if subject responded.
    # Return 0 if not; 1 or 2 if they did; and -1 if they clicked ESC
    def checkResponse(self):
        # if userPressedEscape():
        #     return -1
        #-- Check if exactly one button was pressed

        # Here we apply some small tricky correction for port whose return is always non-null
        # TODO check for consistency.
        resp1 = self.port1.read_status() - self.port1_baseline_value
        resp2 = self.port2.read_status() - self.port2_baseline_value
        resp3 = self.port3.read_status() - self.port3_baseline_value

        if (resp1 != 0 and resp2 == 0 and resp1 != self.port1_last_value):# and resp3 == 0):
            self.port1_last_value = resp1
            print(f'port1_{resp1 + self.port1_baseline_value}')
            return f'port1_{resp1 + self.port1_baseline_value}'
        if (resp1 == 0 and resp2 != 0 and resp2 != self.port2_last_value):# and resp3 == 0):
            self.port2_last_value = resp2
            print(f'port2_{resp2 + self.port2_baseline_value}')
            return f'port2_{resp2 + self.port2_baseline_value}'
        if (resp1 == 0 and resp2 == 0 and resp3 != 0 and resp3 != self.port3_last_value):
            self.port3_last_value = resp3
            print(f'port3_{resp3 + self.port3_baseline_value}')
            return f'port3_{resp3 + self.port3_baseline_value}'

        if (resp1 != self.port1_last_value):
            self.port1_last_value = resp1
        if(resp2 != self.port2_last_value):
            self.port2_last_value = resp2
        if(resp3 != self.port3_last_value):
            self.port3_last_value = resp3

        return None



    def wait(self,  codes=None, duration=None):

        """Homemade wait for MEG response buttons

        Parameters
        ----------
        codes : int or list, optional !!! IS IGNORED AND KEPT ONLY FOR CONSISTENCY WITH THE KEYBOARD METHOD
            bit pattern to wait for
            if codes is not set (None) the function returns for any
            event that differs from the baseline
        duration : int, optional
            maximal time to wait in ms
        no_clear_buffer : bool, optional
            do not clear the buffer (default = False)
        """
        start = get_time()
        rt = None
        while True:
            found = self.checkResponse()
            if found :
                rt = int((get_time() - start) * 1000)
                break

            if duration is not None:
                if int((get_time() - start) * 1000) > duration:
                    return None, None

        return found, rt



if __name__ == '__main__':
    pass
    # import os

    # def check_parallel_ports():
    #     parallel_ports = []
    #     dev_dir = '/dev/'

    #     # Check common parallel port device files
    #     for i in range(10):  # Adjust the range based on the expected number of parallel ports
    #         port = f'parport{i}'
    #         if os.path.exists(os.path.join(dev_dir, port)):
    #             parallel_ports.append(os.path.join(dev_dir, port))

    #     return parallel_ports

    # available_ports = check_parallel_ports()
    # print(f"Available parallel ports: {available_ports}")
#######################

#     expyriment.control.defaults.window_mode = True

#     exp = design.Experiment(name="Explore+", text_size=30)

#     receive_port1 = '/dev/parport0' 
#     receive_port2 = '/dev/parport1' 
#     receive_port3 = '/dev/parport4'
#     response_meg = response_in_MEG(exp, receive_port1, receive_port2, receive_port3)
#     port2send = response_meg.port2

#     port2send.send(data=0)

#     responses = []
#     while len(responses)<9:
#         key, rt = response_meg.wait(duration=20)



'''
port1_17 : droite bleu
port2_24 : droite jaune
port2_20 : droite vert
port2_18 : droite rouge
'''


