#!/usr/bin/env python3
"""Export the style's fixed motion tokens as CSS or QML values."""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT/'assets/tokens.json'

def cubic(p0,p1,p2,p3,t):
    return (1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3

def curve_y(points,x):
    if len(points)%6 or not points: raise ValueError('Expected complete Qt spline segments')
    start_x,start_y = 0.,0.
    for i in range(0,len(points),6):
        x1,y1,x2,y2,end_x,end_y = points[i:i+6]
        if x<=end_x or i+6==len(points):
            lo,hi=0.,1.
            for _ in range(50):
                mid=(lo+hi)/2
                if cubic(start_x,x1,x2,end_x,mid)<x: lo=mid
                else: hi=mid
            return cubic(start_y,y1,y2,end_y,(lo+hi)/2)
        start_x,start_y=end_x,end_y
    raise ValueError('No segment')

def export(data,platform):
    result = {}
    for name,token in sorted(data['wrappers'].items()):
        points=data['curves'][token['curve']]
        n=lambda v:format(v,'.12g')
        if platform=='qml':
            value=f"duration: {token['duration_ms']}\neasing.type: Easing.BezierSpline\neasing.bezierCurve: [{', '.join(map(n,points))}]"
            parity='exact-fixed-curve'
        elif len(points)==6 and points[-2:]==[1,1]:
            value=f"{token['duration_ms']}ms cubic-bezier({', '.join(map(n,points[:4]))})"
            parity='exact-fixed-curve'
        else:
            stops=', '.join(f'{curve_y(points,i/200):.8f} {i/2:g}%' for i in range(201))
            value=f"{token['duration_ms']}ms linear({stops})"
            parity='sampled-201-stops'
        result[name]=dict(value=value,parity=parity,helper=token['helper'])
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform',choices=['css','qml'],required=True)
    args=parser.parse_args()
    print(json.dumps(export(json.loads(TOKENS.read_text()),args.platform),indent=2,sort_keys=True))
if __name__=='__main__': main()
