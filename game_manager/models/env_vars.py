from env_var import EnvVar


class EnvVars:
    def __init__(self):
        self.env_vars = []

    def add_env_var(self, env_var: EnvVar):
        self.env_vars.append(env_var)
        return self
