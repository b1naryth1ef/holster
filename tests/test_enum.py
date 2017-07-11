from unittest import TestCase

from holster.enum import Enum


class EnumTestCase(TestCase):
    def test_bitmask_enum(self):
        enum = Enum('a', 'b', 'c', 'd', 'e', 'f', 'g')

        self.assertEqual(enum.a, enum.a)
        self.assertNotEqual(enum.a, enum.b)

        self.assertLess(enum.b, enum.e)
        self.assertLess(enum.a, enum.b)
        self.assertGreater(enum.g, enum.a)
        self.assertGreater(enum.g, enum.f)

        self.assertLessEqual(enum.c, enum.c)
        self.assertLessEqual(enum.c, enum.d)
        self.assertGreaterEqual(enum.e, enum.e)
        self.assertGreaterEqual(enum.e, enum.d)

        self.assertEqual(enum.a.index, 1)
        self.assertEqual(enum.b.index, 2)
        self.assertEqual(enum.c.index, 4)
