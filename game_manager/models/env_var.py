class EnvVar:
    def __init__(self):
        self.name = None
        self.value = None

    def set_name(self, name):
        self.name = name
        return self

    def set_value(self, value):
        self.value = value
        return self
