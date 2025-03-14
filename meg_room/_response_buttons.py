'''
TODO
'''

class Button:
    def __init__(self, label, data):
        """
        Initialise un bouton avec ses informations issues du dictionnaire de configuration.

        :param label: Nom du bouton (ex: "l_red").
        :param data: Données associées au bouton (ex: "STI012").
        """
        self.label = label
        self.ttl = data  # Le YAML ne semble fournir qu'une seule valeur par bouton
        self.status = None  # Valeur par défaut, à adapter si nécessaire

    def __repr__(self):
        return f"Button(label={self.label}, ttl={self.ttl}, status={self.status})"


class ResponseButtons:
    def __init__(self, config):
        """
        Initialise les boutons de réponse à partir de la configuration.

        :param config: Dictionnaire contenant la configuration des boutons.
        """
        buttons_dict = config.get("buttons", {})  # Récupère la section "buttons" du YAML
        self._buttons = {label: Button(label, data) for label, data in buttons_dict.items()}

    def __getitem__(self, label):
        """Permet d'accéder aux boutons via response_buttons["l_red"]."""
        return self._buttons[label]

    def __getattr__(self, label):
        """Permet d'accéder aux boutons via response_buttons.l_red."""
        if label in self._buttons:
            return self._buttons[label]
        raise AttributeError(f"'ResponseButtons' object has no attribute '{label}'")

    def __repr__(self):
        return f"ResponseButtons({list(self._buttons.keys())})"

