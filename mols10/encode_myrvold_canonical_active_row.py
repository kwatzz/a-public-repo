#!/usr/bin/env python3
"""Myrvold pair plus a canonical active row of a prospective third TRP.

Completeness: an active row has six outer symbols in columns 0..5 and one row
of Omega in columns 6..9. The projected autotopism group of either Omega is
transitive on its rows, and arbitrary relabelling of outer symbols 4..9
preserves the type/colour conditions. Thus it can be normalized to
[4,5,6,7,8,9,0,1,2,3]. We deliberately do not impose the official first-row
normal form on P because it uses overlapping symbol symmetry.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from encode_myrvold_triple import N,CASES,OMEGA,Enc,latin,trp,colour_channel,type_constraints,dark_consistency,lex_equal_type_rows,subsquare_consistency

def fixed_row_channel(e:Enc,name:str,row,X):
 start=e.n+1;A=[[e.var() for _ in range(N)] for _ in range(N)];e.blocks[name]={'start':start,'end':e.n,'shape':[N,N]}
 for xr in range(N):
  e.exactly_one(A[xr])
  for c,s in enumerate(row):
   e.add([-X[xr][c][s],A[xr][c]]);e.add([-A[xr][c],X[xr][c][s]])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case',choices=sorted(CASES),required=True);ap.add_argument('--omega',choices=OMEGA,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--metadata',type=Path,required=True);a=ap.parse_args()
 e=Enc();P=e.cube('P');Q=e.cube('Q');latin(e,P);latin(e,Q);trp(e,'E_PQ',P,Q)
 PW,PD=colour_channel(e,'P',P);QW,QD=colour_channel(e,'Q',Q)
 type_constraints(e,a.case[0],PW,PD);type_constraints(e,a.case[1],QW,QD);dark_consistency(e,P,Q,PD,QD)
 lex_equal_type_rows(e,a.case[0],P);lex_equal_type_rows(e,a.case[1],Q)
 om=OMEGA[a.omega];subsquare_consistency(e,om,P);subsquare_consistency(e,om,Q)
 row=[4,5,6,7,8,9,0,1,2,3]
 fixed_row_channel(e,'E_RP',row,P);fixed_row_channel(e,'E_RQ',row,Q)
 with a.output.open('w') as f:
  f.write(f'p cnf {e.n} {len(e.clauses)}\n')
  for q in e.clauses:f.write(' '.join(map(str,q))+' 0\n')
 meta={'order':N,'case':a.case,'omega':a.omega,'canonical_active_row':row,'variables':e.n,'clauses':len(e.clauses),'blocks':e.blocks,'normalization':['active Omega row mapped to row 0 by Omega autotopism','outer symbols relabelled to make prefix 4,5,6,7,8,9','equal-type rows of P,Q lexicographically ordered'],'semantics':'Myrvold-compatible P,Q are a TRP and both are TRP with the canonical active row','completeness':'every triple in the specified Myrvold case has an equivalent representative satisfying this formula'}
 a.metadata.write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'case':a.case,'omega':a.omega,'variables':e.n,'clauses':len(e.clauses)}))
if __name__=='__main__':main()
