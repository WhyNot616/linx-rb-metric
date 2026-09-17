"""
LINX — self-contained reproduction script (portable; reads CSVs from its own folder).
Run:  python verify_all.py
Prints each HEADLINE number (computed vs the value claimed in the dossier) so an auditor can
confirm or refute the work in one command. No hardcoded paths, no internet needed.
Requires: pandas, numpy, scipy, scikit-learn (pip install pandas numpy scipy scikit-learn).
"""
import os, numpy as np, pandas as pd
from scipy import stats
from sklearn.linear_model import Ridge, RidgeCV, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import make_pipeline

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
def load(f): return pd.read_csv(os.path.join(D, f))
def z(s): return (s - s.mean())/s.std(ddof=0)
def pr(label, computed, claimed): print(f"  {label:52s} computed={computed:>8}   claimed={claimed}")

raw   = load("linx_player_seasons_2018_2025.csv")   # LINX component inputs
print("="*90); print("LINX REPRODUCTION —", len(raw), "player-seasons"); print("="*90)

# ---------- 1) Build LINX from scratch (0.45/0.30/0.25, z within season) ----------
parts=[]
for y,g in raw.groupby("year"):
    g=g.copy(); g["z_yac"]=z(g.yac_att); g["z_brk"]=z(g.brk_rate); g["z_ol"]=z(g.ol_adj_ybc)
    g["LINX"]=0.45*g.z_yac+0.30*g.z_brk+0.25*g.z_ol; parts.append(g)
S=pd.concat(parts, ignore_index=True)

print("\n[1] WITHIN-SEASON VALIDITY (LINX vs YPC-above-team)")
r1,p1=stats.pearsonr(S.LINX,S.ypc_above_team)
pr("Pearson r", round(r1,3), "0.632"); pr("R^2", round(r1**2,3), "0.399"); pr("p-value", f"{p1:.1e}", "<1e-42")

# ---------- 2) YoY pairs, stability, multiple regression ----------
rows=[]
for p,g in S.groupby("player"):
    gi=g.set_index("year")
    for t in gi.index:
        if t+1 in gi.index:
            a=gi.loc[t]; b=gi.loc[t+1]
            rows.append(dict(player=p,year_t=t,LINX_t=a.LINX,LINX_t1=b.LINX,age_t=a.age,
                ol_delta=b.ol_adj_ybc-a.ol_adj_ybc,ypc_t1=b.ypc_above_team,
                z_yac=a.z_yac,z_brk=a.z_brk,z_ol=a.z_ol))
P=pd.DataFrame(rows)
print(f"\n[2] YEAR-OVER-YEAR (n={len(P)} pairs)")
pr("single-year LINX stability r", round(stats.pearsonr(P.LINX_t,P.LINX_t1)[0],3), "0.316")
X=np.column_stack([P.LINX_t,P.ol_delta,P.age_t]); reg=LinearRegression().fit(X,P.LINX_t1)
pr("multiple-reg R^2 (LINX_t+ol_delta+age)", round(reg.score(X,P.LINX_t1),3), "0.157")

# ---------- 3) Blind holdout: do Ridge-derived weights beat 45/30/25 out-of-sample? ----------
tr=P[P.year_t<=2022]; te=P[P.year_t>=2023]; F=["z_yac","z_brk","z_ol"]
def testr(w): return stats.pearsonr(te[F].values@w, te.ypc_t1)[0]
w_orig=np.array([.45,.30,.25])
sc=StandardScaler().fit(tr[F]); w_pred=RidgeCV(alphas=np.logspace(-2,3,60)).fit(sc.transform(tr[F]),tr.ypc_t1).coef_/sc.scale_
print("\n[3] BLIND HOLDOUT (train<=2022 -> test 2024-25); weights should TIE (fancy overfits)")
pr("test r, original 45/30/25", round(testr(w_orig),3), "~0.21")
pr("test r, Ridge-learned weights", round(testr(w_pred),3), "~0.21 (no better)")

# ---------- 4) Stabilized LINX (3yr window, decay .5, shrink K=200) + blind ----------
league={c:raw.groupby("year")[c].mean().to_dict() for c in ["yac_att","brk_rate","ol_adj_ybc"]}
def stab(window=3,decay=0.5,K=200):
    recs=[]
    for p,g in raw.groupby("player"):
        g=g.sort_values("year")
        for t in g.year:
            win=g[(g.year<=t)&(g.year>t-window)]; w=win.att.values*(decay**(t-win.year.values)); n=win.att.sum()
            rec={"player":p,"year":t}
            for c in ["yac_att","brk_rate","ol_adj_ybc"]:
                blend=np.average(win[c].values,weights=w); rec[c]=(n/(n+K))*blend+(K/(n+K))*league[c][t]
            recs.append(rec)
    Sd=pd.DataFrame(recs); out=[]
    for t,g in Sd.groupby("year"):
        g=g.copy(); zz=np.column_stack([z(g.yac_att),z(g.brk_rate),z(g.ol_adj_ybc)])
        g["LINXs"]=zz@np.array([.45,.30,.25]); out.append(g)
    return pd.concat(out)
Sstab=stab(); smap=Sstab.set_index(["player","year"]).LINXs.to_dict()
ypc=raw.set_index(["player","year"]).ypc_above_team.to_dict()
pp=[(p,t,smap[(p,t)],ypc[(p,t+1)]) for p,g in Sstab.groupby("player") for t in g.year
    if (p,t+1) in ypc and (p,t) in smap]
PS=pd.DataFrame(pp,columns=["player","year_t","LINXs_t","ypc_t1"]); tes=PS[PS.year_t>=2023]
base_te=P[P.year_t>=2023]
print(f"\n[4] STABILIZED LINX — blind predictive power (n={len(tes)} pairs; single-year n={len(base_te)})")
pr("blind r, single-year LINX", round(stats.pearsonr(base_te.LINX_t,base_te.ypc_t1)[0],3), "0.214")
pr("blind r, stabilized LINX", round(stats.pearsonr(tes.LINXs_t,tes.ypc_t1)[0],3), "0.291")
print("    NOTE: this n is the figure published on the site next to r = 0.29.")

# ---------- 5) NGS RYOE benchmark ----------
try:
    ngs=load("ngs_ryoe_2018_2025.csv"); SUF={"jr","sr","ii","iii","iv","v"}
    nm=lambda n:" ".join(x for x in str(n).lower().replace(".","").replace("'","").split() if x not in SUF)
    ngs["k"]=ngs.player.map(nm)+"|"+ngs.year.astype(str); S["k"]=S.player.map(nm)+"|"+S.year.astype(str)
    m=S.merge(ngs[["k","ryoe_att"]],on="k")
    print(f"\n[5] NGS RYOE BENCHMARK (merged {len(m)} of {len(S)})")
    pr("within-season r(LINX, RYOE/att)", round(stats.pearsonr(m.LINX,m.ryoe_att)[0],3), "0.715")
    Sstab["k"]=Sstab.player.map(nm)+"|"+Sstab.year.astype(str); rr=dict(zip(ngs.k,ngs.ryoe_att)); ss=dict(zip(Sstab.k,Sstab.LINXs))
    rows2=[(smap.get((p,t)),rr.get(f"{nm(p)}|{t}"),ypc.get((p,t+1))) for p,g in Sstab.groupby("player") for t in g.year if (p,t+1) in ypc]
    q=pd.DataFrame(rows2,columns=["L","R","y"]).dropna()
    pr("predict next-yr: stabilized LINX", round(stats.pearsonr(q.L,q.y)[0],3), "0.258")
    pr("predict next-yr: RYOE/att", round(stats.pearsonr(q.R,q.y)[0],3), "0.141")
except Exception as e: print("[5] NGS section skipped:",e)

# ---------- 6) Fantasy engine + overfit ----------
try:
    fant=load("pfr_fantasy_rb_2018_2025.csv"); SUF={"jr","sr","ii","iii","iv","v"}
    nm=lambda n:" ".join(x for x in str(n).lower().replace(".","").replace("'","").split() if x not in SUF)
    lm=dict(zip(Sstab.player.map(nm)+"|"+Sstab.year.astype(str),Sstab.LINXs))
    fant["k"]=fant.player.map(nm)+"|"+fant.year.astype(str)
    fant["ppr_pg"]=fant.ppr/fant.g; fant["car_pg"]=fant.rush_att/fant.g; fant["tgt_pg"]=fant.targets/fant.g
    fant["rec_pg"]=fant.rec/fant.g; fant["td_rate"]=fant.rush_td/fant.rush_att.clip(lower=1)
    fant["gm"]=np.where(fant.year<=2020,16,17)-fant.g; fant["LINX"]=fant.k.map(lm).fillna(0.0)
    FE=["ppr_pg","car_pg","tgt_pg","rec_pg","td_rate","LINX","age","gm"]; rr=[]
    for p,g in fant.groupby("player"):
        yy={r.year:r for r in g.itertuples()}
        for y,a in yy.items():
            b=yy.get(y+1)
            if b is None or a.g<8 or b.g<6: continue
            rr.append({"yt":y,**{f:getattr(a,f) for f in FE},"y1":b.ppr_pg})
    FP=pd.DataFrame(rr).dropna(); Xf=FP[FE].values; yf=FP.y1.values; A=24.54
    cv=cross_val_score(make_pipeline(StandardScaler(),Ridge(alpha=A)),Xf,yf,cv=KFold(5,shuffle=True,random_state=0),scoring="r2")
    trf=FP[FP.yt<=2022]; tef=FP[FP.yt>=2023]; scf=StandardScaler().fit(trf[FE])
    mdl=Ridge(alpha=A).fit(scf.transform(trf[FE]),trf.y1)
    def R2(a,b): return 1-((b-a)**2).sum()/((b-b.mean())**2).sum()
    print(f"\n[6] FANTASY ENGINE (n={len(FP)} pairs)")
    pr("5-fold CV R^2", round(cv.mean(),3), "0.471")
    pr("BLIND (2024-25) R^2", round(R2(mdl.predict(scf.transform(tef[FE])),tef.y1.values),3), "0.523")
    naive=R2(tef.ppr_pg.values,tef.y1.values); pr("naive 'same as last yr' blind R^2", round(naive,3), "0.427")
except Exception as e: print("[6] Fantasy section skipped:",e)

# ---------- 7) Injury/availability null ----------
try:
    gm=load("pfr_games_2018_2025.csv"); gm["miss"]=np.where(gm.year<=2020,16,17)-gm.g
    mm=gm.set_index(["player","year"]).miss.to_dict()
    rr=[(P.LINX_t.iloc[i],mm.get((r.player,r.year_t)),r.ypc_t1) for i,r in P.iterrows()]
    q=pd.DataFrame(rr,columns=["L","miss","y"]).dropna()
    b0=LinearRegression().fit(q[["L"]],q.y); b1=LinearRegression().fit(q[["L","miss"]],q.y)
    print("\n[7] INJURY/AVAILABILITY (should be ~null)")
    pr("R^2 add from games-missed beyond LINX", round(b1.score(q[["L","miss"]],q.y)-b0.score(q[["L"]],q.y),3), "+0.002")
except Exception as e: print("[7] Injury section skipped:",e)

print("\n"+"="*90); print("Done. Compare 'computed' vs 'claimed' above. Small diffs (<0.01) = rounding.")
print("="*90)
