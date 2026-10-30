import glob,sys,numpy as np
from PIL import Image
S=sys.argv[1]; fr=sorted(glob.glob(S+'/frames/f*.png'))
a=[np.asarray(Image.open(f).convert('L'),dtype=float) for f in fr]
d=[np.abs(a[i]-a[i-1]).mean() for i in range(1,len(a))]
for i,v in enumerate(d,2):
    # flag: cut if v>15; spike if v>2.5x neighbour median
    nb=np.median(d[max(0,i-6):i-2]+d[i-1:i+3]) if True else 0
    tag='CUT' if v>12 else ('SPIKE' if v>2.5*max(nb,0.3) else '')
    print(f"f{i-1}->f{i}: {v:6.2f} {tag}")
