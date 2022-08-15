import unittest


# TODO DELETE
class TestFake(unittest.TestCase):
    def tearDown(self) -> None:
        pass

    def test_fake(self) -> None:
        self.assertEqual(1, 1)
