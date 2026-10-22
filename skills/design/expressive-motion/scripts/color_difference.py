"""sRGB D65 -> CIELAB -> CIEDE2000, kL=kC=kH=1.
Formula/test data: Sharma, Wu & Dalal (2005), doi:10.1002/col.20070.
https://hajim.rochester.edu/ece/sites/gsharma/ciede2000/
Independent vectorized implementation; no image registration or masking.
"""
import numpy as np

def rgb_to_lab(rgb):
    rgb=np.asarray(rgb,dtype=float)/255
    linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
    xyz=linear@np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.0721750],[.0193339,.1191920,.9503041]]).T
    scaled=xyz/np.array([.95047,1,1.08883])
    d=6/29;f=np.where(scaled>d**3,np.cbrt(scaled),scaled/(3*d*d)+4/29)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],axis=-1)

def delta_e_2000(lab1,lab2):
    l1,a1,b1=np.moveaxis(np.asarray(lab1,dtype=float),-1,0)
    l2,a2,b2=np.moveaxis(np.asarray(lab2,dtype=float),-1,0)
    c1=np.hypot(a1,b1);c2=np.hypot(a2,b2);cm=(c1+c2)/2
    g=.5*(1-np.sqrt(cm**7/(cm**7+25**7)))
    ap1=(1+g)*a1;ap2=(1+g)*a2
    cp1=np.hypot(ap1,b1);cp2=np.hypot(ap2,b2)
    hp1=np.where(cp1==0,0,np.degrees(np.arctan2(b1,ap1))%360)
    hp2=np.where(cp2==0,0,np.degrees(np.arctan2(b2,ap2))%360)
    dl=l2-l1;dc=cp2-cp1;dh=hp2-hp1;zero=cp1*cp2==0
    dh=np.where(zero,0,np.where(dh>180,dh-360,np.where(dh< -180,dh+360,dh)))
    dH=2*np.sqrt(cp1*cp2)*np.sin(np.radians(dh/2))
    lm=(l1+l2)/2;cm=(cp1+cp2)/2;hs=hp1+hp2
    hm=np.where(zero,hs,np.where(np.abs(hp1-hp2)<=180,hs/2,np.where(hs<360,(hs+360)/2,(hs-360)/2)))
    cos=lambda deg:np.cos(np.radians(deg))
    t=1-.17*cos(hm-30)+.24*cos(2*hm)+.32*cos(3*hm+6)-.20*cos(4*hm-63)
    sl=1+.015*(lm-50)**2/np.sqrt(20+(lm-50)**2);sc=1+.045*cm;sh=1+.015*cm*t
    rt=-2*np.sqrt(cm**7/(cm**7+25**7))*np.sin(np.radians(60*np.exp(-((hm-275)/25)**2)))
    return np.sqrt(np.maximum(0,(dl/sl)**2+(dc/sc)**2+(dH/sh)**2+rt*(dc/sc)*(dH/sh)))
