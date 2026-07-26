#!/usr/bin/env python3
"""Check a Kissat SAT model against DIMACS and decode P,Q exactly."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def read_model(path:Path):
 truth={};status=None
 for line in path.read_text(errors='replace').splitlines():
  if line.startswith('s '):status=line.split()[1]
  elif line.startswith('v '):
   for z in map(int,line.split()[1:]):
    if z:truth[abs(z)]=z>0
 return status,truth

def check_cnf(path:Path,truth):
 nv=nc=None;clauses=[];cur=[]
 for line in path.read_text().splitlines():
  if not line or line[0]=='c':continue
  if line[0]=='p':_,fmt,nv,nc=line.split();assert fmt=='cnf';nv=int(nv);nc=int(nc);continue
  for z in map(int,line.split()):
   if z:cur.append(z)
   else:clauses.append(cur);cur=[]
 assert not cur and len(clauses)==nc
 bad=[i for i,c in enumerate(clauses,1) if not any(truth.get(abs(z),False)==(z>0) for z in c)]
 assert not bad,bad[:10]
 return nv,nc

def cube(start,truth):
 A=[]
 for r in range(10):
  row=[]
  for c in range(10):
   vals=[s for s in range(10) if truth.get(start+(r*10+c)*10+s,False)]
   assert len(vals)==1,(r,c,vals);row.append(vals[0])
  A.append(row)
 return A

def latin(A):
 t=set(range(10));return all(set(x)==t for x in A) and all({A[r][c] for r in range(10)}==t for c in range(10))
def trp(A,B):return all(sum(A[r][c]==B[s][c] for c in range(10))<=1 for r in range(10) for s in range(10))

def main():
 p=argparse.ArgumentParser();p.add_argument('--cnf',type=Path,required=True);p.add_argument('--meta',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 status,t=read_model(a.model);assert status=='SATISFIABLE',status
 nv,nc=check_cnf(a.cnf,t);m=json.loads(a.meta.read_text());P=cube(m['blocks']['P']['start'],t);Q=cube(m['blocks']['Q']['start'],t);R=m['canonical_active_row']
 assert latin(P) and latin(Q) and trp(P,Q)
 assert all(sum(P[r][c]==R[c] for c in range(10))<=1 for r in range(10))
 assert all(sum(Q[r][c]==R[c] for c in range(10))<=1 for r in range(10))
 out={'status':'SAT','variables':nv,'clauses':nc,'P':P,'Q':Q,'canonical_active_row':R,'checks':{'cnf':True,'P_latin':True,'Q_latin':True,'PQ_trp':True,'P_row_trp':True,'Q_row_trp':True}}
 a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['checks'],sort_keys=True))
if __name__=='__main__':main()
