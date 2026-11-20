import os,json,urllib.request,random
MASK=(1<<64)-1
NAMES='PNBRQKpnbrqk'
V=(100,320,335,500,950,20000)*2
R=[]
for df,dr in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
 ray=[]
 for s in range(64):
  f=s%8+df;r=s//8+dr;b=0
  while 0<=f<8 and 0<=r<8:b|=1<<(r*8+f);f+=df;r+=dr
  ray.append(b)
 R.append(ray)
def table(ds):
 a=[]
 for s in range(64):
  f=s%8;r=s//8;mask=0
  for df,dr in ds:
   x=f+df;y=r+dr
   if 0<=x<8 and 0<=y<8:mask|=1<<(y*8+x)
  a.append(mask)
 return a
N=table(((1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)))
K=table(((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)))
P=[table(((-1,1),(1,1))),table(((-1,-1),(1,-1)))]
F=[sum(1<<(8*r+f) for r in range(8)) for f in range(8)]
rng=random.Random(924643); Z=[[rng.getrandbits(64) for _ in range(64)] for _ in range(12)];ZC=[rng.getrandbits(64) for _ in range(16)];ZE=[rng.getrandbits(64) for _ in range(65)];ZS=rng.getrandbits(64)
def slide(s,occ,dirs):
 result=0
 for d in dirs:
  ray=R[d][s];block=ray&occ
  if block:
   near=(block&-block).bit_length()-1 if d in (0,2,4,5) else block.bit_length()-1
   ray^=R[d][near]
  result|=ray
 return result
ORTH=(0,1,2,3);DIAG=(4,5,6,7);ALL=ORTH+DIAG
def bits(x):
 while x:
  z=x&-x;yield z.bit_length()-1;x-=z
def pos(fen):
 f=fen.split();bb=[0]*12;B=[-1]*64
 for r,row in enumerate(f[0].split('/')):
  file=0
  for x in row:
   if x.isdigit():file+=int(x)
   else:
    s=(7-r)*8+file;p=NAMES.index(x);bb[p]|=1<<s;B[s]=p;file+=1
 white=0;black=0
 for p in range(6):white|=bb[p];black|=bb[p+6]
 c=0 if f[1]=='w' else 1;ca=sum(v for ch,v in zip('KQkq',(1,2,4,8)) if ch in f[2]);ep=(int(f[3][1])-1)*8+ord(f[3][0])-97 if f[3]!='-' else -1
 h=ZC[ca]^ZE[ep+1]^(ZS if c else 0)
 for i in range(12):
  for s in bits(bb[i]):h^=Z[i][s]
 return bb,B,[c,ca,ep,h,white,black,white|black]
def atk(bb,s,c,occ):
 base=6*c
 return bool(P[1-c][s]&bb[base] or N[s]&bb[base+1] or K[s]&bb[base+5] or slide(s,occ,DIAG)&(bb[base+2]|bb[base+4]) or slide(s,occ,ORTH)&(bb[base+3]|bb[base+4]))
def gen(bb,B,st,out,q=True):
 out.clear();c,ca,ep,h,w,b,occ=st;own=w if c==0 else b;enemy=b if c==0 else w;base=6*c;other=6*(1-c);enemyking=bb[other+5]
 for s in bits(bb[base]):
  rank=s//8;step=8 if c==0 else -8;t=s+step
  if 0<=t<64 and B[t]<0:
   if t//8 in (0,7):
    for k in range(4,8):out.append(s|(t<<6)|(k<<12))
   elif q:
    out.append(s|(t<<6))
    if rank==(1 if c==0 else 6) and B[t+step]<0:out.append(s|((t+step)<<6)|(2<<12))
  for t in bits(P[c][s]&(enemy&~enemyking | (1<<ep if ep>=0 else 0))):
   if t//8 in (0,7):
    for k in range(4,8):out.append(s|(t<<6)|(k<<12))
   else:out.append(s|(t<<6)|((3 if t==ep and B[t]<0 else 1)<<12))
 for p in range(1,6):
  for s in bits(bb[base+p]):
   dest=N[s] if p==1 else K[s] if p==5 else slide(s,occ,DIAG if p==2 else ORTH if p==3 else ALL)
   dest&=~own&~enemyking
   if not q:dest&=enemy
   for t in bits(dest):out.append(s|(t<<6)|((1 if B[t]>=0 else 0)<<12))
 if q:
  s=4 if c==0 else 60
  if B[s]==base+5 and not atk(bb,s,1-c,occ):
   for bit,rook,empty,trans,to in ((1,7,(5,6),5,6),(2,0,(1,2,3),3,2)) if c==0 else ((4,63,(61,62),61,62),(8,56,(57,58,59),59,58)):
    if ca&bit and B[rook]==base+3 and all(B[x]<0 for x in empty) and not atk(bb,trans,1-c,occ) and not atk(bb,to,1-c,occ):out.append(s|(to<<6)|(8<<12))
 return out
def make(bb,B,st,m):
 c,ca,ep,h,w,b,occ=st;s=m&63;t=(m>>6)&63;k=m>>12;p=B[s];cap=t-8 if k==3 and c==0 else t+8 if k==3 else t;capt=B[cap];put=(1,2,3,4)[k-4]+6*c if 4<=k<=7 else p
 u=(s,t,p,capt,cap,ca,ep,h,w,b,occ,k,put)
 sb=1<<s;tb=1<<t;bb[p]^=sb;B[s]=-1;h^=Z[p][s]
 if capt>=0:bb[capt]^=1<<cap;B[cap]=-1;h^=Z[capt][cap]
 bb[put]^=tb;B[t]=put;h^=Z[put][t]
 if k==8:
  rf=s+3 if t>s else s-4;rt=s+1 if t>s else s-1;rp=base=3+6*c
  bb[rp]^=(1<<rf)|(1<<rt);B[rf]=-1;B[rt]=rp;h^=Z[rp][rf]^Z[rp][rt]
 if p==5:ca&=~3
 if p==11:ca&=~12
 for sq,bit in ((7,1),(0,2),(63,4),(56,8)):
  if s==sq or t==sq:ca&=~bit
 e=(s+t)//2 if k==2 else -1
 h^=ZC[st[1]]^ZC[ca]^ZE[ep+1]^ZE[e+1]^ZS
 w=0;b=0
 for i in range(6):w|=bb[i];b|=bb[i+6]
 st[:]=[1-c,ca,e,h,w,b,w|b]
 return u
def unmake(bb,B,st,u):
 s,t,p,capt,cap,ca,ep,h,w,b,occ,k,put=u;c=st[0]^1
 bb[put]^=1<<t;bb[p]^=1<<s;B[s]=p;B[t]=-1
 if capt>=0:bb[capt]^=1<<cap;B[cap]=capt
 if k==8:
  rf=s+3 if t>s else s-4;rt=s+1 if t>s else s-1;rp=3+6*c
  bb[rp]^=(1<<rf)|(1<<rt);B[rf]=rp;B[rt]=-1
 st[:]=[c,ca,ep,h,w,b,occ]
def uci(m):
 s=m&63;t=m>>6&63;k=m>>12
 return chr(97+s%8)+str(1+s//8)+chr(97+t%8)+str(1+t//8)+('nbrq'[k-4] if 4<=k<=7 else '')
TABLE=[];PHASE=(0,1,1,2,4,0)*2
for p in range(12):
 table=[];sg=1 if p<6 else -1;piece=NAMES[p].lower()
 for s in range(64):
  r=7-s//8 if p<6 else s//8;f=s%8;cen=7-(abs(2*f-7)+abs(2*r-7))//2;adv=6-r
  mg={'p':adv*7+cen*2,'n':cen*9,'b':cen*5,'r':adv*2,'q':cen*2,'k':-cen*7-adv*2}[piece]
  eg={'p':adv*12+cen*2,'n':cen*6,'b':cen*5,'r':adv*3,'q':cen*2,'k':cen*8}[piece]
  table.append((sg*(V[p]+mg),sg*(V[p]+eg)))
 TABLE.append(table)
def evaluate(bb,B,st):
 mg=eg=ph=0;ps=[[],[]];rs=[];ks=[];bs=[0,0];mob=0
 for p in range(12):
  sg=1 if p<6 else -1;color=p//6;kind=p%6;ph+=PHASE[p]*bb[p].bit_count()
  for s in bits(bb[p]):
   a,z=TABLE[p][s];mg+=a;eg+=z;i=(7-s//8)*16+s%8
   if kind==0:ps[1-color].append(i)
   elif kind==2:bs[1-color]+=1
   elif kind==3:rs.append((i,sg))
   elif kind==5:ks.append((i,sg))
   if kind in (1,2):mob+=sg*((N[s] if kind==1 else slide(s,st[6],DIAG))&~st[4+color]).bit_count()
 fs=[[0]*8 for _ in range(2)];front=[[8]*8,[-1]*8]
 for color in (0,1):
  for i in ps[color]:
   f=i%16;r=i//16;fs[color][f]+=1
   if color:front[color][f]=max(front[color][f],r)
   else:front[color][f]=min(front[color][f],r)
 for color in (0,1):
  sg=1 if color else -1
  for f in range(8):
   if fs[color][f]>1:mg-=sg*12*(fs[color][f]-1);eg-=sg*18*(fs[color][f]-1)
  for i in ps[color]:
   r=i//16;f=i%16
   if not (f and fs[color][f-1] or f<7 and fs[color][f+1]):mg-=sg*10;eg-=sg*8
   if (min(front[0][max(0,f-1):f+2])>=r if color else max(front[1][max(0,f-1):f+2])<=r):
    adv=6-r if color else r-1;mg+=sg*adv*4;eg+=sg*adv*10
 for i,sg in rs:
  f=i%16;own=1 if sg==1 else 0
  if not fs[own][f]:bonus=12 if fs[1-own][f] else 24;mg+=sg*bonus;eg+=sg*bonus
 for i,sg in ks:
  f=i%16;own=1 if sg==1 else 0
  if not fs[own][f]:mg-=sg*18
  for df in (-1,0,1):
   t=i-16*sg+df
   if not t&136 and abs(t%16-f)<=1 and B[(7-t//16)*8+t%16]==(0 if sg==1 else 6):mg+=sg*9
 ph=min(24,ph)
 return ((mg*ph+eg*(24-ph))//24+30*((bs[1]>1)-(bs[0]>1))+mob*2)*(1 if st[0]==0 else -1)+8
def choose(fen,allowed,gp=0):
 bb,B,st=pos(fen);root=[m for m in gen(bb,B,st,[]) if uci(m) in allowed];root.sort(key=uci)
 if not root:return sorted(allowed)[0]
 tt={};nodes=0;limit=100000;hist={};kill={};path=set();buf=[[] for _ in range(100)]
 def search(dep,a,be,ply,nullok=True):
  nonlocal nodes
  nodes+=1
  if nodes>limit:raise TimeoutError
  c,ca,ep,h,w,b,occ=st;key=h
  if key in path:return 0
  check=atk(bb,bb[c*6+5].bit_length()-1,1-c,occ)
  if check and dep>0 and ply<32:dep+=1
  if ply>=90:return evaluate(bb,B,st)
  prior=a;hit=tt.get(key)
  if hit and hit[0]>=dep and (hit[2]==0 or hit[2]==1 and hit[1]>=be or hit[2]==-1 and hit[1]<=a):return hit[1]
  if nullok and not check and dep>=3 and ply and be<28000 and (bb[c*6+3]|bb[c*6+4]):
   st[0]^=1;st[2]=-1;st[3]^=ZS^ZE[ep+1]^ZE[0]
   v=-search(dep-3,-be,1-be,ply+1,False)
   st[0]=c;st[2]=ep;st[3]=h
   if v>=be:return be
  if dep<=0 and not check:
   bestval=evaluate(bb,B,st)
   if bestval>=be:return bestval
   a=max(a,bestval)
  else:bestval=-30000
  moves=gen(bb,B,st,buf[ply],dep>0 or check)
  def order(m):
   s=m&63;t=m>>6&63;k=m>>12;capt=B[t];p=B[s]
   return (1000000 if hit and m==hit[3] else 0)+(100000+10*(V[capt] if capt>=0 else 100)-V[p] if capt>=0 or k==3 or 4<=k<=7 else 0)+(900 if 4<=k<=7 else 0)+(8000 if m in kill.get(ply,()) else 0)+hist.get(m,0)
  moves.sort(key=order,reverse=True);best=None;count=0;path.add(key)
  for m in moves:
   capt=B[m>>6&63];u=make(bb,B,st,m)
   if atk(bb,bb[c*6+5].bit_length()-1,1-c,st[6]):unmake(bb,B,st,u);continue
   count+=1
   if count==1:v=-search(dep-1,-be,-a,ply+1)
   else:
    v=-search(dep-1,-a-1,-a,ply+1)
    if a<v<be:v=-search(dep-1,-be,-a,ply+1)
   unmake(bb,B,st,u)
   if v>bestval:bestval=v;best=m
   if v>a:a=v
   if a>=be:
    if capt<0 and m>>12 not in (3,4,5,6,7) and dep>0:
     hist[m]=min(7000,hist.get(m,0)+dep*dep);prev=kill.get(ply,())
     if m not in prev:kill[ply]=(m,)+prev[:1]
    break
  path.remove(key)
  if not count and (dep>0 or check):return -29000+ply if check else 0
  if dep>0 and (not hit or dep>=hit[0]):tt[key]=(dep,bestval,1 if bestval>=be else -1 if bestval<=prior else 0,best)
  return bestval
 best=root[0];sc=0
 for dep in range(1,30):
  try:
   root.sort(key=lambda m:(m==best,V[B[m>>6&63]] if B[m>>6&63]>=0 else 0),reverse=True)
   low,high=(sc-40,sc+40) if dep>1 else (-30000,30000)
   while True:
    a=low;new=best;count=0
    for m in root:
     u=make(bb,B,st,m);count+=1
     if count==1:v=-search(dep-1,-high,-a,1)
     else:
      v=-search(dep-1,-a-1,-a,1)
      if a<v<high:v=-search(dep-1,-high,-a,1)
     unmake(bb,B,st,u)
     if v>a:a=v;new=m
     if a>=high:break
    if (a<=low or a>=high) and (low!=-30000 or high!=30000):low,high=-30000,30000;continue
    best=new;sc=a;break
  except TimeoutError:break
 return uci(best)
def post(path,data):
 req=urllib.request.Request(os.environ['MAKEFUN_ENV_URL']+path,data=json.dumps(data).encode(),headers={'content-type':'application/json'})
 with urllib.request.urlopen(req) as r:return json.load(r)
while True:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'],g['plies'])})
