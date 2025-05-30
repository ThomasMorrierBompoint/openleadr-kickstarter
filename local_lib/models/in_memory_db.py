from local_lib.models.domain import generate_ven_props
from local_lib.utils.main import SingletonMeta, extract_values_from_dicts


def match_condition(doc, key, condition):
    if isinstance(condition, dict):
        if '$lt' in condition:
            return doc.get(key) < condition['$lt']
        if '$lte' in condition:
            return doc.get(key) <= condition['$lte']
        elif '$gt' in condition:
            return doc.get(key) > condition['$gt']
        elif '$gte' in condition:
            return doc.get(key) >= condition['$gte']
        elif '$ne' in condition:
            return doc.get(key) != condition['$ne']
    return doc.get(key) == condition  # $eq


class InMemoryDB(metaclass=SingletonMeta):
    def __init__(self):
        self.collections = {}

    def seed(self):
        self.create_collection('ven_props')
        ven_props = [generate_ven_props(i) for i in range(5)]
        [self.insert('ven_props', ven_prop) for ven_prop in ven_props]

    def create_collection(self, name):
        if name not in self.collections:
            self.collections[name] = []
        return self.collections[name]

    def insert(self, collection_name, document):
        if collection_name not in self.collections:
            self.create_collection(collection_name)
        self.collections[collection_name].append(document)
        return document

    def find(self, collection_name, query=None):
        if collection_name not in self.collections:
            return []
        if query is None:
            return self.collections[collection_name]

        return [doc for doc in self.collections[collection_name]
                if all(match_condition(doc, k, v) for k, v in query.items())]

    def find_one(self, collection_name, query=None):
        doc = self.find(collection_name, query)[0]
        return doc if doc else None

    def update(self, collection_name, query, update_data):
        documents = self.find(collection_name, query)
        for doc in documents:
            doc.update(update_data)
        return len(documents)

    def delete(self, collection_name, query):
        if collection_name not in self.collections:
            return 0
        initial_length = len(self.collections[collection_name])
        self.collections[collection_name] = [
            doc for doc in self.collections[collection_name]
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        return initial_length - len(self.collections[collection_name])

    def drop_collection(self, collection_name):
        if collection_name in self.collections:
            del self.collections[collection_name]

    def list_collections(self):
        return list(self.collections.keys())


if __name__ == "__main__":
    """
    For learning purposes...
    """
    db = InMemoryDB()
    db.seed()
    print(db.list_collections())

    results = db.find('ven_props')
    print(extract_values_from_dicts(results, 'name'))
