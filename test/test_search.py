from os import path
import unittest

from comp61542.database import database

class TestSearch(unittest.TestCase):

    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

    def test_search_by_author(self):
        authorName = "Stefano Ceri"
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        header, data = db.search_author(authorName)
        self.assertEqual(len(header), len(data),
            "header and data column size doesn't match")
        self.assertEqual(data[0],authorName,
            "incorrect number of authors")
        self.assertEqual(data[3], 1,
            "incorrect number of books")
        self.assertEqual(data[6], 2,
            "incorrect number of coauthors")