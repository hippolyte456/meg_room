#TODO...

class Button:
    def __init__(self, label, ttl, status):
        self.label = label
        self.ttl = ttl
        self.status = status

    def __repr__(self):
        return f"Button(label={self.label}, ttl={self.ttl}, status={self.status})"


class Buttons:
    def __init__(self, buttons_dict):
        self._buttons = {label: Button(label, data["ttl"], data["status"]) for label, data in buttons_dict.items()}

    def __getitem__(self, label):
        return self._buttons[label]

    def __getattr__(self, label):
        return self._buttons[label]

    def __repr__(self):
        return f"Buttons({list(self._buttons.keys())})"
