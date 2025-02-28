import expyriment
from expyriment.io import ParallelPort

# Initialisation de l'expérimentation
expyriment.design.Experiment(name="My Experiment")
expyriment.control.initialize()

# Initialisation du port parallèle
port = ParallelPort(address="/dev/parport0")  # Remplacez "/dev/parport0" par l'adresse de votre port parallèle
port.set_impedance(0)  # Réglage de l'impédance

# Commencer l'enregistrement des réponses
port.open()
port.set_event_detector(enabled=True)  # Activer le détecteur d'événements

# Affichage de stimuli et traitement des réponses
expyriment.control.start()
# Affichez vos stimuli et attendez les réponses
# Par exemple :
expyriment.stimuli.TextLine(text="Appuyez sur un bouton").present()
response = port.wait_for_event()
if response is not None:
    print("Réponse reçue sur la broche :", response.pin_number)
else:
    print("Aucune réponse reçue")

# Nettoyage et arrêt de l'expérimentation
port.close()
expyriment.control.end()
