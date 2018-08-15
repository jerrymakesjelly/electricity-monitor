# -*- coding:utf-8 -*-
import os
import json

# Configuration Manager
class ConfigMan(object):
    def __init__(self, module, filename):
        self._path = os.path.join(self._make_directory(module), filename)

    # Get module directory or create it if it doesn't exist
    @staticmethod
    def _make_directory(module):
        module_path = os.path.join(os.path.expanduser('~'), '.%s' % module)
        os.makedirs(module_path, mode=0o755, exist_ok=True)
        return module_path
    
    # Load configurations
    def read(self):
        with open(self._path, 'r', encoding='utf-8') as f:
            param = json.load(f)
        return param
    
    # Save configurations
    def write_back(self, params):
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(params, f)
