#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, pathlib, re

def rank(rows,n=35):
    a=list(rows); r=0
    for c in range(n):
        p=next((i for i in range(r,len(a)) if (a[i]>>c)&1),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]
        for i in range(len(a)):
            if i!=r and ((a[i]>>c)&1): a[i]^=a[r]
        r+=1
    return r

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('masks'); ap.add_argument('map'); ap.add_argument('solver_log'); ap.add_argument('r',type=int)
    a=ap.parse_args()
    masks=[int(s,16) for s in pathlib.Path(a.masks).read_text().split()]
    names={}
    for line in pathlib.Path(a.map).read_text().splitlines():
        v,name=line.split(); names[int(v)]=name
    true=set()
    for line in pathlib.Path(a.solver_log).read_text(errors='replace').splitlines():
        if line.startswith('v '):
            for z in line[2:].split():
                q=int(z)
                if q>0:true.add(q)
    rows=[0]*a.r
    for v in true:
        m=re.fullmatch(r'h_(\d+)_(\d+)',names.get(v,''))
        if m: rows[int(m.group(1))]|=1<<int(m.group(2))
    uncovered=[m for m in masks if all(((m&t).bit_count()&1)==0 for t in rows)]
    print('rows_hex='+' '.join(f'{x:09x}' for x in rows))
    print('rank='+str(rank(rows)))
    print('uncovered='+str(len(uncovered)))
    print('masks_sha256='+hashlib.sha256(pathlib.Path(a.masks).read_bytes()).hexdigest())
    ok=rank(rows)==a.r and not uncovered
    print('RESULT='+('PASS' if ok else 'FAIL'))
    raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()
