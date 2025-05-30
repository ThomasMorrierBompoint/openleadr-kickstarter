import pytest
from local_lib.models.domain import Ven, VenList, generate_ven_props, VenProps


@pytest.fixture
def sample_ven_props() -> VenProps:
    return {
        'name': 'test-ven',
        'id': 'ID_123',
        'registration_id': 'REG_456',
        'fingerprint': 'abc123'
    }


@pytest.fixture
def sample_ven(sample_ven_props) -> Ven:
    return Ven(sample_ven_props)


@pytest.fixture
def sample_ven_list(sample_ven) -> VenList:
    return VenList([sample_ven])


class TestVen:
    def test_ven_initialization(self, sample_ven_props):
        ven = Ven(sample_ven_props)
        assert ven.name == sample_ven_props['name']
        assert ven.id == sample_ven_props['id']
        assert ven.registration_id == sample_ven_props['registration_id']
        assert ven.fingerprint == sample_ven_props['fingerprint']

    def test_ven_string_representation(self, sample_ven):
        expected = f"VEN(name={sample_ven.name}, id={sample_ven.id}, registration_id={sample_ven.registration_id}, fingerprint={sample_ven.fingerprint})"
        assert str(sample_ven) == expected


class TestVenList:
    def test_venlist_initialization(self, sample_ven):
        ven_list = VenList([sample_ven])
        assert len(ven_list) == 1

    def test_get_names(self, sample_ven_list, sample_ven):
        assert sample_ven_list.get_names() == [sample_ven.name]

    def test_find_by_id(self, sample_ven_list, sample_ven):
        found_ven = sample_ven_list.find_by_id(sample_ven.id)
        assert found_ven is not None
        assert found_ven.id == sample_ven.id

    def test_find_by_id_not_found(self, sample_ven_list):
        found_ven = sample_ven_list.find_by_id("non_existent_id")
        assert found_ven is None

    def test_find_by_registration_id(self, sample_ven_list, sample_ven):
        found_ven = sample_ven_list.find_by_registration_id(sample_ven.registration_id)
        assert found_ven is not None
        assert found_ven.registration_id == sample_ven.registration_id

    def test_has_ven_with_id(self, sample_ven_list, sample_ven):
        assert sample_ven_list.has_ven_with_id(sample_ven.id) is True
        assert sample_ven_list.has_ven_with_id("non_existent_id") is False

    def test_has_ven_with_name(self, sample_ven_list, sample_ven):
        assert sample_ven_list.has_ven_with_name(sample_ven.name) is True
        assert sample_ven_list.has_ven_with_name("non_existent_name") is False

    def test_append_ven(self, sample_ven_list):
        new_ven_props: VenProps = {
            'name': 'new-ven',
            'id': 'ID_789',
            'registration_id': 'REG_789',
            'fingerprint': 'def456'
        }
        new_ven = Ven(new_ven_props)
        original_length = len(sample_ven_list)
        sample_ven_list.append(new_ven)
        assert len(sample_ven_list) == original_length + 1
        assert sample_ven_list.has_ven_with_name('new-ven')

    def test_ven_props_list_immutability(self, sample_ven_list):
        original_list = sample_ven_list.ven_props_list
        sample_ven_list.append(Ven(generate_ven_props(original_list.__len__())))
        modified_list = sample_ven_list.ven_props_list
        modified_list[0].name = "modified"
        assert original_list[0].name != modified_list[0].name

    def test_venlist_string_representation(self, sample_ven_list):
        assert str(sample_ven_list) == "VenList(1 VENs)"


def test_generate_ven_props():
    ven_props = generate_ven_props(0)
    assert isinstance(ven_props, dict)
    assert all(key in ven_props for key in ['name', 'id', 'registration_id', 'fingerprint'])
    assert ven_props['id'].startswith('ID_')
    assert ven_props['registration_id'].startswith('REG_')
    assert len(ven_props['fingerprint']) == 64  # SHA256 hash length
