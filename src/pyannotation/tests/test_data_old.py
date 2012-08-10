from pyannotation.data import DataStructureType

__author__ = 'Peter Bouda'

class TestDataStructureType():
    def setUp(self):
        self.data_structure_type = DataStructureType()

    def test_get_siblings_of_type(self):
        s = self.data_structure_type.get_siblings_of_type("utterance")
        assert(s == ["utterance", "translation"])

    def test_get_parents_of_type(self):
        s = self.data_structure_type.get_parents_of_type("word")
        assert(s == ["utterance", "translation"])