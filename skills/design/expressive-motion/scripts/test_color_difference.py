import unittest
from pathlib import Path
import numpy as np
from color_difference import delta_e_2000,rgb_to_lab
class ColorDifferenceTests(unittest.TestCase):
    def test_sharma_34_supplemental_pairs(self):
        rows=np.loadtxt(Path(__file__).resolve().parents[1]/'assets/ciede2000-reference.txt')
        self.assertEqual(len(rows),34)
        np.testing.assert_allclose(delta_e_2000(rows[:,:3],rows[:,3:6]),rows[:,6],atol=5e-5,rtol=0)
    def test_identity_symmetry(self):
        a=np.array([[50,2,-80],[100,0,0],[0,0,0]]);b=np.array([[30,0,50],[0,0,0],[100,0,0]])
        np.testing.assert_allclose(delta_e_2000(a,a),0)
        np.testing.assert_allclose(delta_e_2000(a,b),delta_e_2000(b,a))
    def test_srgb_endpoints(self):
        np.testing.assert_allclose(rgb_to_lab([0,0,0]),[0,0,0],atol=1e-10)
        np.testing.assert_allclose(rgb_to_lab([255,255,255]),[100,0,0],atol=2e-5)
