import json


class Settings:
    def __init__(self, path):
        self.path = path
        self.branch = 'master'
        self.sql_regex = '"(select|call|update|delete|insert|nvl){1}.*";'
        self.java_mask = '\.java$'
        self.xml_mask = '\.(lc|check|action)$'

    def parse(self):
        with open(self.path) as file:
            template = json.load(file)
            self.branch = template['branch']
            self.sql_regex = template['sql_regex']
            self.java_mask = template['java_mask']
            self.xml_mask = template['xml_mask']