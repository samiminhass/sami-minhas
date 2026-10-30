import sys
from PIL import Image, ImageOps, ImageFilter, ImageDraw
import numpy as np
d=sys.argv[1]
out={}
for name in ['ref_girl_braid','ref_baker']:
    im=Image.open(f'{d}/{name}.jpg').convert('RGB'); a=np.asarray(im).astype(int)
    bg=np.median(np.concatenate([a[:5].reshape(-1,3),a[-5:].reshape(-1,3)]),axis=0)
    diff=np.abs(a-bg).sum(2)
    mask=diff>45
    m=Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.MedianFilter(5))
    mask=np.asarray(m)>128
    # remove shadow: shadow is low-sat grey near feet; keep as is but report bbox
    ys,xs=np.where(mask)
    print(name,'size',im.size,'bbox x',xs.min(),xs.max(),'y',ys.min(),ys.max())
    sil=Image.fromarray(np.where(mask,0,255).astype('uint8'))
    sil.save(f'{d}/{name}_silhouette.png')
    ImageOps.grayscale(im).save(f'{d}/{name}_gray.png')
    # row profile of mask width, for head measurement
    w=mask.sum(1)
    for y in range(ys.min(),ys.max(),15): print(' y',y,'width',w[y])
    out[name]=(im,mask,(xs.min(),ys.min(),xs.max(),ys.max()))
# phone sim: 360x640 frame; character height = 50% of frame (320px) per bible silhouette rule
for name,(im,mask,bb) in out.items():
    crop=im.crop((bb[0]-10,bb[1]-5,bb[2]+10,bb[3]+5))
    for frac,tag in [(0.5,'half'),(0.85,'medium')]:
        h=int(640*frac); w=int(crop.width*h/crop.height)
        c=crop.resize((w,h),Image.LANCZOS)
        f=Image.new('RGB',(360,640),(120,110,100))
        f.paste(c,((360-w)//2,640-h-40))
        f.save(f'{d}/{name}_phone_{tag}.png')
        # also face crop of phone frame at 1:1 to inspect pixels
    print(name,'phone half: char height 320px')
