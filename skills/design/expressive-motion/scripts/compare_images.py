#!/usr/bin/env python3
"""Compare same-sized RGB ROIs without resizing (requires Pillow and NumPy).
SSIM: 11px Gaussian window sigma1.5, population covariance, valid windows,
per-channel mean, C1=(.01*255)^2,C2=(.03*255)^2. No registration/masking.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from color_difference import rgb_to_lab,delta_e_2000

def blur(a):
    kernel=np.exp(-np.arange(-5,6,dtype=float)**2/(2*1.5**2));kernel/=kernel.sum()
    a=np.tensordot(np.lib.stride_tricks.sliding_window_view(a,11,axis=0),kernel,axes=(-1,0))
    return np.tensordot(np.lib.stride_tricks.sliding_window_view(a,11,axis=1),kernel,axes=(-1,0))

def metrics(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if a.shape!=b.shape or a.ndim!=3 or a.shape[2]!=3:raise ValueError('Require equal RGB image sizes; never rescale an oracle')
    if min(a.shape[:2])<11:raise ValueError('ROI must be at least11px in both dimensions')
    ma,mb=blur(a),blur(b)
    va=np.maximum(0,blur(a*a)-ma*ma);vb=np.maximum(0,blur(b*b)-mb*mb)
    covariance=blur(a*b)-ma*mb
    score=((2*ma*mb+6.5025)*(2*covariance+58.5225))/((ma*ma+mb*mb+6.5025)*(va+vb+58.5225))
    d=np.abs(a-b)
    de=delta_e_2000(rgb_to_lab(a),rgb_to_lab(b))
    return {'ssim':float(score.mean()),'rmse_8bit':float(np.sqrt(np.mean(d*d))),
            'max_channel_error':int(d.max()),'different_pixels':int(np.count_nonzero(d.max(axis=2))),
            'delta_e_2000':{'profile':'sRGB D65 assumed','mean':float(de.mean()),'p95':float(np.percentile(de,95)),'max':float(de.max()),'pixels_over_2':int(np.count_nonzero(de>2))},
            'size':[a.shape[1],a.shape[0]],'ssim_gate':bool(score.mean()>=.98)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('candidate',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--preview',type=Path);p.add_argument('--color-roi',action='append',default=[],help='Separate stable color rectangle x,y,w,h; full SSIM remains unmasked');p.add_argument('--quiet',action='store_true',help='Print only a JSON-quoted result path; persist complete JSON evidence');args=p.parse_args()
    a=Image.open(args.source).convert('RGB');b=Image.open(args.candidate).convert('RGB')
    result=metrics(a,b);result.update(source=str(args.source),candidate=str(args.candidate),method=__doc__.strip())
    result['stable_color_rois']=[]
    for spec in args.color_roi:
        x,y,w,h=map(int,spec.split(','))
        if min(x,y)<0 or min(w,h)<=0 or x+w>a.width or y+h>a.height:raise ValueError('Color ROI outside image')
        aa=np.asarray(a)[y:y+h,x:x+w];bb=np.asarray(b)[y:y+h,x:x+w]
        de=delta_e_2000(rgb_to_lab(aa),rgb_to_lab(bb))
        result['stable_color_rois'].append({'rect':[x,y,w,h],'mean':float(de.mean()),'max':float(de.max()),'gate_max_le_2':bool(de.max()<=2)})
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    if args.preview:
        d=np.abs(np.asarray(a,dtype=float)-np.asarray(b,dtype=float));heat=Image.fromarray(np.clip(d*4,0,255).astype('uint8'))
        w,h=a.size;out=Image.new('RGB',(w*3,h+28),'#202020');draw=ImageDraw.Draw(out)
        for i,(name,im) in enumerate([('Qt source',a),('Web rendered',b),('Abs difference x4',heat)]):
            draw.text((i*w+5,7),name,fill='white');out.paste(im,(i*w,28))
        out.resize((w*6,(h+28)*2)).save(args.preview)
    if args.quiet:
        print(json.dumps(str(args.output.resolve()),ensure_ascii=False))
    else:
        print(json.dumps(result))
if __name__=='__main__':main()
