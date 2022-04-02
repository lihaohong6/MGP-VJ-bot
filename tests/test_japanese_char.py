import unittest

from utils.japanese_char import get_pronunciations


class MyTestCase(unittest.TestCase):
    def test_get_pronunciations(self):
        self.assertEqual(["ひと", "り", "と", "じん", "にん"], get_pronunciations("人"))
        self.assertEqual(['よかい', 'せいかい', 'せかい', 'そうかい'], get_pronunciations("世界"))


if __name__ == '__main__':
    unittest.main()
