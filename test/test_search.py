from os import path
import unittest

from comp61542.database import database

class TestSearch(unittest.TestCase):

    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

    """def test_search_by_author(self):
        authorName = "Stefano Ceri"
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        header, data = db.search_author(authorName)
        self.assertEqual(len(header), len(data),
            "header and data column size doesn't match")
        self.assertEqual(data[0],authorName,
            "incorrect author")
        self.assertEqual(data[3], 1,
            "incorrect number of books")
        self.assertEqual(data[5], 2,
            "incorrect number of times he appears first")
        self.assertEqual(data[6], 0,
            "incorrect number of times he appears last")
        self.assertEqual(data[8], 2,
            "incorrect number of coauthors")"""

    def test_search_first_author(self):
        authorName = "AUTHOR1"
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        data = db.get_first_author_stats(authorName)
        self.assertEqual(data[0],authorName,
            "incorrect author")
        self.assertEqual(data[1], 2,
            "incorrect number of times he appears first in conference paper")
        self.assertEqual(data[2], 0,
            "incorrect number of times he appears first in journal")
        self.assertEqual(data[3], 0,
            "incorrect number of times he appears first in book")
        self.assertEqual(data[4], 0,
            "incorrect number of times he appears first in book chapter")
        self.assertEqual(data[5], 2,
            "incorrect number of times he appears first in total")

    def test_search_last_author(self):
        authorName = "Stefano Ceri"
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "publications_small_sample.xml")))
        data = db.get_last_author_stats(authorName)
        self.assertEqual(data[0],authorName,
            "incorrect author")
        self.assertEqual(data[1], 0,
            "incorrect number of times he appears first in conference paper")
        self.assertEqual(data[2], 0,
            "incorrect number of times he appears first in journal")
        self.assertEqual(data[3], 0,
            "incorrect number of times he appears first in book")
        self.assertEqual(data[4], 0,
            "incorrect number of times he appears first in book chapter")
        self.assertEqual(data[5], 0,
            "incorrect number of times he appears first in total")

    def test_search_sole_author_pub(self):
        authorName = "AUTHOR1"
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        data = db.get_sole_author_stats(authorName)
        self.assertEqual(data[0],authorName,
            "incorrect author")
        self.assertEqual(data[1], 1,
            "incorrect number of conference papers")
        self.assertEqual(data[2], 0,
            "incorrect number of journals")
        self.assertEqual(data[3], 0,
            "incorrect number of books")
        self.assertEqual(data[4], 0,
            "incorrect number of book chapters")
        self.assertEqual(data[5], 1,
            "incorrect number of total")

    def test_search_all_author_pub(self):
        authorName = "AUTHOR1"
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        data = db.get_all_author_stats(authorName)
        self.assertEqual(data[0],authorName,
            "incorrect author")
        self.assertEqual(data[1], 3,
            "incorrect number of conference papers")
        self.assertEqual(data[2], 0,
            "incorrect number of journals")
        self.assertEqual(data[3], 0,
            "incorrect number of books")
        self.assertEqual(data[4], 0,
            "incorrect number of book chapters")
        self.assertEqual(data[5], 3,
            "incorrect number of total")