import sys, math, datetime as dt
import os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ypres_data as Y
U={u[0]:u for u in Y.U}
print(len(Y.U),'units',len(Y.A),'assign',len(Y.P),'positions',len(Y.PL),'places; used',len({k for p in Y.P for k in p['keys']}))
for p in Y.P:
    assert p['unit_id'] in U, p
    for k in p['keys']: assert k in Y.PL,(p['pos_id'],k)
for a in Y.A: assert a[0] in U and (a[1]=='' or a[1] in U), a
def dd(s): return None if s=='unknown' else dt.date.fromisoformat(s)
# per unit ordering / overlaps
by={}
for p in Y.P: by.setdefault(p['unit_id'],[]).append(p)
for u,rows in by.items():
    for a,b in zip(rows,rows[1:]):
        if dd(a['ee'])>=dd(b['se']) and not (dd(a['ee'])<dd(b['sl'] if b['sl']!='unknown' else b['se']) ): print('overlap',u,a['pos_id'],a['ee'],b['pos_id'],b['se'],b['sl'])
# crossings between opposing lines, per day
def seg_x(p1,p2,p3,p4):
    def o(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    d1,d2,d3,d4=o(p3,p4,p1),o(p3,p4,p2),o(p1,p2,p3),o(p1,p2,p4)
    return d1*d2<0 and d3*d4<0
seen=set()
day=dt.date(1914,10,16)
while day<=dt.date(1914,11,22):
    act=[p for p in Y.P if Y.line(p) and dd(p['se'])<=day<=(dd(p['el']) or dd(p['ee']))]
    for i,a in enumerate(act):
        for b in act[i+1:]:
            if U[a['unit_id']][3]==U[b['unit_id']][3]: continue
            A=Y.line(a); B=Y.line(b)
            if len(A)<2 or len(B)<2: continue
            for x in range(len(A)-1):
                for y in range(len(B)-1):
                    if seg_x(A[x],A[x+1],B[y],B[y+1]) and (a['pos_id'],b['pos_id']) not in seen:
                        seen.add((a['pos_id'],b['pos_id'])); print('CROSS',day,a['pos_id'],a['unit_id'],a['se'],a['ee'],'x',b['pos_id'],b['unit_id'],b['se'],b['ee'])
    day+=dt.timedelta(days=1)
print('crossings',len(seen))
