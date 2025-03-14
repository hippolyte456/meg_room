'''
Definition of the StimPC class, which handles the communication with the parallel ports of the StimPC.
'''

import os
import time
from expyriment import io
from expyriment.misc._timer import get_time


# TODO remove hardocing and see with Fosca how to improve parport related code
# port1, port2, port3, etc. ou avec des tests sur les noms ?

class StimPC:

    def __init__(self, config, dev_mode=True):
        """
        Initialise l'objet StimPC à partir d'un dictionnaire de configuration.

        :param config: Dictionnaire contenant la configuration du StimPC.
                       Il doit contenir une clé 'parport' avec les numéros de port.
        """
        self.parport = config.get("parport", {})  # Récupère le sous-dictionnaire des ports
        self.config = config
        # Choisir la bonne classe pour les ports
        PortClass = MockPort if dev_mode else io.ParallelPort
        
        # Vérifie que les ports requis existent #TODO the number of PP should not be hardcoded
        self.port1 = PortClass(self.parport.get("port1"))
        self.port2 = PortClass(self.parport.get("port2"))
        self.port3 = PortClass(self.parport.get("port3"))

        # Lire les statuts initiaux #TODO remove ?
        _ = self.port1.read_status()
        _ = self.port2.read_status()
        _ = self.port3.read_status()

        self.port1_baseline_value = self.port1.read_status()
        self.port2_baseline_value = self.port2.read_status()
        self.port3_baseline_value = self.port3.read_status()
        self.port1_last_value = self.port1_baseline_value
        self.port2_last_value = self.port2_baseline_value
        self.port3_last_value = self.port3_baseline_value

    
    def __repr__(self):
        return f"StimPC(config={self.config})"

#-------- RELATED TO RESPONSES BUTTONS --------#   
    def _check_response(self):
        ''' By Fosca
        Check if subject responded.
        Return 0 if not; 1 or 2 if they did; and -1 if they clicked ESC
        '''

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


    def wait_response(self, duration=None):

        """ By Fosca
        Homemade wait for MEG response buttons

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
            found = self._check_response()
            if found :
                rt = int((get_time() - start) * 1000)
                break

            if duration is not None:
                if int((get_time() - start) * 1000) > duration:
                    return None, None

        return found, rt


#-------- RELATED TO TRIGGERS --------# 
    def _get_sending_port(self, device):
        '''Return the port to send triggers to the MEG'''
        #TODO detect the port2send automatically
        return self.port2
    
    
    def _get_read_port(self, device):
        '''return the adress for reading from the wanted device'''
        pass

  
    def send(self, trigger = 255, duration = 5):
        '''
        esay sent of triggers to the MEG
        '''
        port2send = self._get_sending_port()
        port2send.send(data = trigger)
        time.sleep(duration / 1000)
        # exp.clock.wait(duration) #TODO check with Christophe that this changes is okay ?
        port2send.send(data = 0) 
 
            
    def write_response(self):
        print("Not implemented yet")
        
#-------- 3  SOME QUICK DIAGNOSTICS --------# 
    def find_parports_addresses(self):
        """
        Searches for available parallel ports on the system.
        This function scans the '/dev/' directory for files or directories that contain 'parport' in their names,
        indicating the presence of parallel ports. It prints the results of the search and returns a list of paths
        to the detected parallel ports.
        Returns:
            list: A list of strings representing the paths to the detected parallel ports. If no parallel ports are found,
                  an empty list is returned.
        """
  
        dev_dir = '/dev/'
        parallel_ports = []
        print("\n🔍 Recherche des ports parallèles disponibles sur le système...")

        try:
            # Liste tous les fichiers / dossiers dans /dev/
            dev_files = os.listdir(dev_dir)
            # Filtrer ceux qui contiennent 'parport'
            parallel_ports = [os.path.join(dev_dir, f) for f in dev_files if 'parport' in f and os.path.exists(os.path.join(dev_dir, f))]
        except FileNotFoundError:
            print(f"❌ Le dossier {dev_dir} n'existe pas sur ce système.")
            return []

        if parallel_ports:
            print("\n✅ Ports parallèles trouvés :")
            for idx, port in enumerate(parallel_ports, 1):
                print(f"  {idx}. {port}")
        else:
            print("\n⚠️ Aucun port parallèle détecté sur ce système.")

        return parallel_ports


    def record_pressed_buttons(self):
        """
        Interactive function to help the user press each response button.
        Uses `wait_response` from parent class to capture button addresses.
        Returns the list of addresses (values) corresponding to each button.
        """

        print("\n🎮 Please press each response button one by one when prompted.")
        print("⚠️ Make sure the device is ready and connected.")
        print("👉 After pressing each button, wait until the system detects it.\n")
        print("💡 When finished (no more buttons to press), just press 'Enter' to stop.\n")

        recorded_buttons = []
        button_index = 1

        while True:
            user_input = input(f"➡️  Press button {button_index} and press 'Enter' to start detection (or 'Enter' empty to finish): ")
            
            # If user just presses Enter, we finish
            if user_input.strip() == '':
                print("\n🛑 Button recording stopped by user.\n")
                break

            print("⏳ Waiting for button press...")

            # Here we call the parent's wait_response method to get the button address
            value = self.wait_response()

            print(f"✅ Button {button_index} recorded with value/address: {value}\n")
            recorded_buttons.append(value)
            button_index += 1

        print("\n📝 All recorded button addresses:", recorded_buttons)
        print("✅ You can now use these addresses to define your button-response mappings.\n")

        return recorded_buttons


#-------- 4 - ROBUSTNESS OF THE ACQUISITION --------# 
    def send_all_triggers(self):
        '''Send triggers from 0 to 255 to the parallel port, every 50 ms'''

        print("\n⚠️ Please make sure that raw signal recording is running.")
        input("✅ Press Enter when you are ready to start sending triggers...")

        print("\n🚀 Starting to send triggers from 0 to 255...\n")

        for i in range(256):
            self.port1.send(i)
            print(f"Trigger sent: {i}", end='\r')  # Inline print for real-time feedback without flooding
            time.sleep(0.05)  # 50 ms delay

        print("\n✅ All triggers have been sent successfully.")

           

#FOR DEV MODE                            
class MockPort:
    """Simule un port parallèle pour le mode développement."""
    def __init__(self, port_name):
        self.port_name = port_name

    def __repr__(self):
        return f"MockPort(port_name={self.port_name})"
    
    def read_status(self):
        print(f"[DEV MODE] Lecture fictive du port {self.port_name}")
        return 0  # Valeur par défaut pour éviter les erreurs


    def send(self, data):
        print(f"[DEV MODE] Envoi de {data} sur {self.port_name}")
