import unittest
import numpy as np
from compare_images import metrics
class ImageMetricTests(unittest.TestCase):
    def test_identity(self):
        a=np.random.default_rng(42).integers(0,256,(30,40,3),dtype=np.uint8)
        m=metrics(a,a);self.assertEqual(m['ssim'],1);self.assertEqual(m['rmse_8bit'],0)
    def test_constant_analytic(self):
        a=np.full((20,20,3),20);b=np.full((20,20,3),80)
        self.assertAlmostEqual(metrics(a,b)['ssim'],(2*20*80+6.5025)/(20**2+80**2+6.5025),places=10)
        self.assertEqual(metrics(a,b)['rmse_8bit'],60)
    def test_size_mismatch_rejected(self):
        with self.assertRaises(ValueError):metrics(np.zeros((20,20,3)),np.zeros((21,20,3)))
    def test_black_white_fails(self):
        self.assertFalse(metrics(np.zeros((20,20,3)),np.full((20,20,3),255))['ssim_gate'])
