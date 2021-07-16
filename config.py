from configparser import ConfigParser

class Config:
    def __init__(self):
        self.cp = ConfigParser()
        self.cp.read("config.ini")
    
    def get(self, section_name, config_name, default_data=None):
        try:
            result = self.cp.get(section_name, config_name)
        except:
            return default_data
        return result
    
    def set(self, section_name, config_name, config_data):
        self.cp.set(section_name, config_name, str(config_data))
        with open("config.ini", "w") as f:
            self.cp.write(f)
        return True