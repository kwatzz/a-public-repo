#!/usr/bin/env python3
"""Completeness-preserving SAT encoding primitives for the Myrvold cases."""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path
from typing import Iterable,Sequence
N=10
TYPES={'R':[1]*8+[4]*2,'S':[1]*7+[3]*3,'T':[1]*7+[2,3,4],'U':[1]*6+[2]*2+[3]*2,'V':[1]*6+[2]*3+[4],'W':[1]*5+[2]*4+[3],'X':[1]*4+[2]*6}
CASES={'SX','UX','VX','WX','XX','UU','UW','WW'}
OMEGA={'z4':[[0,1,2,3],[1,2,3,0],[2,3,0,1],[3,0,1,2]],'z2x2':[[0,1,2,3],[1,0,3,2],[2,3,0,1],[3,2,1,0]]}
PATTERNS=[[0,1,2,4,5,6,3,7,8,9],[0,1,3,4,5,6,2,7,8,9],[0,2,3,4,5,6,1,7,8,9]]
class Enc:
 def __init__(self):self.n=0;self.clauses=[];self.blocks={}
 def var(self):self.n+=1;return self.n
 def cube(self,name):
  start=self.n+1;z=[[[self.var() for _ in range(N)] for _ in range(N)] for _ in range(N)];self.blocks[name]={'start':start,'end':self.n,'shape':[N,N,N]};return z
 def matrix(self,name):
  start=self.n+1;z=[[self.var() for _ in range(N)] for _ in range(N)];self.blocks[name]={'start':start,'end':self.n,'shape':[N,N]};return z
 def add(self,x:Iterable[int]):
  q=list(x);assert q and all(q);self.clauses.append(q)
 def unit(self,x:int):self.add([x])
 def exactly_one(self,x:Sequence[int]):
  self.add(x)
  for a,b in itertools.combinations(x,2):self.add([-a,-b])
 def exactly_k_bruteforce(self,x:Sequence[int],k:int):
  for q in itertools.combinations(x,k+1):self.add(-v for v in q)
  for q in itertools.combinations(x,len(x)-k+1):self.add(q)
def latin(e:Enc,X):
 for r in range(N):
  for c in range(N):e.exactly_one(X[r][c])
 for r in range(N):
  for s in range(N):e.exactly_one([X[r][c][s] for c in range(N)])
 for c in range(N):
  for s in range(N):e.exactly_one([X[r][c][s] for r in range(N)])
def trp(e:Enc,name,X,Y):
 E=e.cube(name)
 for xr in range(N):
  for yr in range(N):
   for c,d in itertools.combinations(range(N),2):e.add([-E[xr][yr][c],-E[xr][yr][d]])
   for c in range(N):
    for s in range(N):e.add([-X[xr][c][s],-Y[yr][c][s],E[xr][yr][c]])
def colour_channel(e:Enc,name,X):
 W=e.matrix(name+'_white');D=e.matrix(name+'_dark')
 for r in range(N):
  for c in range(N):
   e.add([-W[r][c],-D[r][c]])
   if c<6:
    e.unit(-W[r][c]);e.add([-D[r][c]]+[X[r][c][s] for s in range(4,10)])
   else:
    e.unit(-D[r][c]);e.add([-W[r][c]]+[X[r][c][s] for s in range(4)])
    for s in range(4):e.add([-X[r][c][s],W[r][c]])
 return W,D
def type_constraints(e:Enc,typ,W,D):
 for r,k in enumerate(TYPES[typ]):
  e.exactly_k_bruteforce([W[r][c] for c in range(6,10)],k);e.exactly_k_bruteforce([D[r][c] for c in range(6)],2*k-2)
 for c in range(6):e.exactly_k_bruteforce([D[r][c] for r in range(N)],2)
def dark_consistency(e:Enc,P,Q,PD,QD):
 for c in range(6):
  for s in range(N):
   for pr in range(N):
    for qr in range(N):
     e.add([-QD[qr][c],-Q[qr][c][s],-P[pr][c][s],PD[pr][c]]);e.add([-PD[pr][c],-Q[qr][c][s],-P[pr][c][s],QD[qr][c]])
def lex_equal_type_rows(e:Enc,typ,X):
 t=TYPES[typ]
 for r in range(N-1):
  if t[r]!=t[r+1]:continue
  for upper in range(N):
   for lower in range(upper):e.add([-X[r][0][upper],-X[r+1][0][lower]])
def subsquare_consistency(e:Enc,om,X):
 for r in range(N):
  for c,d in itertools.combinations(range(6,10),2):
   for a in range(4):e.add([-X[r][c][om[a][c-6]],-X[r][d][om[a][d-6]]])
