import sys,glob
from PIL import Image
d=sys.argv[1];cols=int(sys.argv[2]) if len(sys.argv)>2 else 3
fs=sorted(glob.glob(d+'/*.png'),key=lambda f:float(f.split('/f')[-1][:-4]))
w=1920//cols;h=w*9//16
ims=[Image.open(f).resize((w,h)) for f in fs]
W=Image.new('RGB',(1920,h*((len(ims)+cols-1)//cols)),'white')
for i,im in enumerate(ims):W.paste(im,((i%cols)*w,(i//cols)*h))
W.save(d+'_sheet.png');print(len(fs))
