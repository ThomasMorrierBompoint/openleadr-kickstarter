import pytest
from local_lib.models.in_memory_db import InMemoryDB


@pytest.fixture
def db():
    return InMemoryDB()


def test_create_collection(db):
    collection = db.create_collection("test_collection")
    assert "test_collection" in db.collections
    assert collection == db.collections["test_collection"]


def test_insert_document(db):
    db.insert("test_collection", {"id": 1, "name": "Test"})
    assert db.collections["test_collection"] == [{"id": 1, "name": "Test"}]


def test_find_documents_no_query(db):
    db.insert("test_collection", {"id": 1, "name": "Test"})
    result = db.find("test_collection")
    assert result == [{"id": 1, "name": "Test"}]


def test_find_documents_with_query(db):
    db.insert("test_collection", {"id": 1, "name": "Test"})
    db.insert("test_collection", {"id": 2, "name": "Another Test"})
    result = db.find("test_collection", {"id": 1})
    assert result == [{"id": 1, "name": "Test"}]


def test_update_documents(db):
    db.insert("test_collection", {"id": 1, "name": "Test"})
    updated_count = db.update("test_collection", {"id": 1}, {"name": "Updated Test"})
    assert updated_count == 1
    assert db.collections["test_collection"] == [{"id": 1, "name": "Updated Test"}]


def test_delete_documents(db):
    db.insert("test_collection", {"id": 1, "name": "Test"})
    db.insert("test_collection", {"id": 2, "name": "Another Test"})
    deleted_count = db.delete("test_collection", {"id": 1})
    assert deleted_count == 1
    assert db.collections["test_collection"] == [{"id": 2, "name": "Another Test"}]


def test_drop_collection(db):
    db.create_collection("test_collection")
    db.drop_collection("test_collection")
    assert "test_collection" not in db.collections


def test_list_collections(db):
    db.create_collection("collection1")
    db.create_collection("collection2")
    collections = db.list_collections()
    assert set(collections) == {"collection1", "collection2"}


def test_find_with_conditions(db):
    db.insert("test_collection", {"id": 1, "value": 10})
    db.insert("test_collection", {"id": 2, "value": 20})
    result = db.find("test_collection", {"value": {"$gt": 15}})
    assert result == [{"id": 2, "value": 20}]
