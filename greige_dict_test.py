from app.style.greige import GreigeStyle
import unittest

class Greige_Test(unittest.TestCase):
    def test_dict(self):
        g1 = GreigeStyle("AU4398", 1.0, 2.0)
        g2 = GreigeStyle("AU4398", 3.0, 4.0)
        greige_dict = {g1 : 10}
        self.assertEqual(greige_dict[g2], 10)
        g3 = GreigeStyle("AU7389G", 5.0, 6.0)
        greige_dict[g3] = 20
        self.assertNotEqual(greige_dict[g1], greige_dict[g3])

if __name__ == '__main__':
    unittest.main()
