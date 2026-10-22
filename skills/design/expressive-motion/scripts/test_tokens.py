import hashlib
import json
import subprocess
import sys
import unittest
from tokens import ROOT,TOKENS,curve_y,export

class Tokens(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.data=json.loads(TOKENS.read_text())
    def test_geometry(self):
        self.assertEqual(self.data['sections']['Sizes']['sideSheetWidth'],320)
        self.assertEqual(self.data['sections']['Sizes']['cardSize'],176)
        self.assertEqual(self.data['sections']['Rounding']['normal'],17)
        self.assertEqual(self.data['sections']['FontSizes']['hugeAss'],23)
    def test_wrapper_goldens_not_generic_m3(self):
        for name,ms,curve in [('ElementResize',300,'emphasized'),('HoverFade',350,'standard'),('ClickBounce',400,'expressiveDefaultSpatial'),('SidebarSlideEnter',300,'standardDecel'),('SidebarSlideExit',250,'standardAccel')]:
            self.assertEqual(self.data['wrappers'][name]['duration_ms'],ms)
            self.assertEqual(self.data['wrappers'][name]['curve'],curve)
    def test_single_segment_exact(self):
        css,qml=export(self.data,'css'),export(self.data,'qml')
        for name,token in self.data['wrappers'].items():
            points=self.data['curves'][token['curve']]
            if len(points)==6:
                got=[float(x) for x in css[name]['value'].split('(')[1].rstrip(')').split(',')]
                self.assertEqual(got,points[:4])
                self.assertEqual(css[name]['parity'],'exact-fixed-curve')
            self.assertIn(', '.join(format(x,'.12g') for x in points),qml[name]['value'])
    def test_piecewise_joins_and_endpoints(self):
        pts=self.data['curves']['emphasized']
        self.assertEqual(len(pts),12)
        self.assertAlmostEqual(curve_y(pts,0),0,places=10)
        self.assertAlmostEqual(curve_y(pts,1),1,places=10)
        self.assertAlmostEqual(curve_y(pts,pts[4]),pts[5],places=10)
    def test_sampled_error_bound(self):
        pts=self.data['curves']['emphasized']
        samples=[curve_y(pts,i/200) for i in range(201)]
        error=0
        for i in range(10001):
            x=i/10000; idx=min(int(x*200),199); frac=x*200-idx
            linear=samples[idx]*(1-frac)+samples[idx+1]*frac
            error=max(error,abs(linear-curve_y(pts,x)))
        self.assertLess(error,.002, f'Normalized curve error {error}')
        self.assertEqual(export(self.data,'css')['ElementResize']['parity'],'sampled-201-stops')
    def test_deterministic_export_across_processes(self):
        for platform in ('css','qml'):
            runs=[subprocess.check_output([sys.executable,str(ROOT/'scripts/tokens.py'),'--platform',platform]) for _ in range(3)]
            self.assertEqual(len({hashlib.sha256(v).hexdigest() for v in runs}),1)
    def test_settings_helpers(self):
        program='const results=[];'+''.join('function '+n+'(milliseconds){'+b+'}\n' for n,b in self.data['helpers'].items())
        program+='for (const reduced of [false,true]) for(const perf of [false,true]) {globalThis.performanceMode=perf; globalThis.reduceMotion=reduced||perf;results.push([reduceMotion,duration(350),motion(500)]);} console.log(JSON.stringify(results));'
        result=json.loads(subprocess.check_output(['node','-e',program],text=True))
        self.assertEqual(result,[[False,350,500],[True,0,0],[True,350,500],[True,0,0]])

if __name__=='__main__': unittest.main()
