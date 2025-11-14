from pypika import Case, CustomFunction
class ColumnBuilder:
    def __init__(self):
        self.columns = []

    def add_column(self, label, fieldtype, width, fieldname, **kwargs):
        column = {"label": label, "fieldtype": fieldtype, "width": width, "fieldname": fieldname, **kwargs}
        self.columns.append(column)
        return self

    def build(self):
        return self.columns

Greatest = CustomFunction('Greatest', ['default', 'value'])

def get_mapped_data(data, key='box'):
    return {item[key]: item for item in data}
def accum_mapper(key: str, data: list) -> dict:
    from collections import defaultdict
    result = defaultdict(list)
    for item in data:
        result[item[key]].append(item)
    return dict(result)

def remove_negative(keys: list, data: list[dict]) -> dict:
    for key in keys:
        for d in data:
            if d.get(key, 0) < 0:
                d[key] = 0
    return data


from abc import ABC, abstractmethod
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass