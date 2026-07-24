#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, pathlib

class CNF:
    def __init__(self):
        self.nvars=0; self.clauses=[]; self.names={}
    def var(self,name):
        v=self.names.get(name)
        if v is None:
            self.nvars+=1; v=self.nvars; self.names[name]=v
        return v
    def add(self,*lits):
        assert lits and all(lits); self.clauses.append(tuple(lits))
    def xor2(self,a,b,name):
        z=self.var(name)
        self.add(-a,-b,-z); self.add(a,b,-z)
        self.add(a,-b,z); self.add(-a,b,z)
        return z
    def parity(self,lits,name):
        assert lits
        if len(lits)==1: return lits[0]
        z=self.xor2(lits[0],lits[1],f'{name}_1')
        for j,x in enumerate(lits[2:],2): z=self.xor2(z,x,f'{name}_{j}')
        return z

def read_masks(path):
    vals=[int(s,16) for s in pathlib.Path(path).read_text().split()]
    if len(vals)!=2982 or len(set(vals))!=2982 or any(v<=0 or v >= 1<<35 for v in vals):
        raise ValueError('expected 2982 distinct nonzero 35-bit masks')
    return vals

def generate(masks,r):
    F=CNF()
    h=[[F.var(f'h_{i}_{k}') for k in range(35)] for i in range(r)]
    p=[[F.var(f'p_{i}_{k}') for k in range(35)] for i in range(r)]
    # Unique RREF basis for every r-dimensional row space.
    for i in range(r):
        F.add(*p[i])
        for k in range(35):
            for l in range(k+1,35): F.add(-p[i][k],-p[i][l])
    for i in range(r-1):
        for k in range(35):
            for l in range(k+1): F.add(-p[i][k],-p[i+1][l])
    for i in range(r):
        for k in range(35):
            F.add(-p[i][k],h[i][k])
            for j in range(r):
                if j!=i: F.add(-p[i][k],-h[j][k])
            for l in range(k): F.add(-p[i][k],-h[i][l])
    # Each QR72 minimum-word evaluation column has nonzero image.
    for j,m in enumerate(masks):
        supp=[k for k in range(35) if (m>>k)&1]
        out=[F.parity([h[i][k] for k in supp],f'y_{j}_{i}') for i in range(r)]
        F.add(*out)
    return F

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('masks'); ap.add_argument('r',type=int); ap.add_argument('cnf'); ap.add_argument('--map')
    a=ap.parse_args(); masks=read_masks(a.masks); F=generate(masks,a.r)
    with open(a.cnf,'w') as o:
        o.write(f'p cnf {F.nvars} {len(F.clauses)}\n')
        for c in F.clauses: o.write(' '.join(map(str,c))+' 0\n')
    mp=a.map or a.cnf+'.map'
    with open(mp,'w') as o:
        for name,v in sorted(F.names.items(),key=lambda kv:kv[1]): o.write(f'{v} {name}\n')
    print(f'r={a.r} vars={F.nvars} clauses={len(F.clauses)} masks={len(masks)}')
    for p in (a.cnf,mp): print(pathlib.Path(p).name+'_sha256='+hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest())
if __name__=='__main__': main()
