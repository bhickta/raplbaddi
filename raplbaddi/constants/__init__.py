import os
import importlib

def execute():
    current_dir = os.path.dirname(__file__)

    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module = importlib.import_module(f'.{module_name}', package=__package__)
            if hasattr(module, 'execute'):
                module.execute()