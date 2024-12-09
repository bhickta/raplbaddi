# import os
# import importlib.util
# import inspect

# def auto_import_from_folder(folder_path):
#     current_file = os.path.basename(__file__)
#     imported_objects = {}

#     for file in os.listdir(folder_path):
#         if file.endswith(".py") and file != current_file:
#             module_name = file[:-3]
#             module_path = os.path.join(folder_path, file)

#             spec = importlib.util.spec_from_file_location(module_name, module_path)
#             module = importlib.util.module_from_spec(spec)
#             spec.loader.exec_module(module)

#             prefix = getattr(module, "prefix", "")
#             for name, obj in inspect.getmembers(module):
#                 if not name.startswith("_"):
#                     imported_objects[f"{prefix}{name}"] = obj

#     return imported_objects

# if __name__ == "__main__":
#     folder_path = os.path.dirname(os.path.abspath(__file__))
#     imported_objects = auto_import_from_folder(folder_path)