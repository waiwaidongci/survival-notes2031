"""Whole-roll (cluster) bootstrap: strips cut from one roll share defects.

Resampling draws entire rolls with replacement; a drawn roll contributes all
of its specimens to the replicate. Replicates whose median is not reached are
counted separately and never enter numeric interval statistics. Given the same
seed the replicate sequence is identical, so recomputation is reproducible.
"""
import random
from ..constants.bootstrap import BOOTSTRAP_METHOD

def validate_rolls(rows_a,rows_b,code_a,code_b):
    missing=[f"{code} 缺 {sum(1 for r in rows if not (r.get('roll_no') or '').strip())} 件" for code,rows in [(code_a,rows_a),(code_b,rows_b)] if any(not (r.get('roll_no') or '').strip() for r in rows)]
    if missing:raise ValueError("存在未记录来源卷的试件（"+"、".join(missing)+"）；同卷灯带共用缺陷，整卷重抽样要求每件试件都有卷号，请补齐后再创建研究")
    shared=sorted({r['roll_no'].strip() for r in rows_a}&{r['roll_no'].strip() for r in rows_b})
    if shared:raise ValueError(f"卷号 {shared[0]} 等 {len(shared)} 个卷同时出现在 {code_a} 与 {code_b}；同一卷只能属于一个批次，请核对卷号后再创建研究")

def _rolls(rows):
    grouped={}
    for r in rows:grouped.setdefault(r['roll_no'].strip(),[]).append((r['duration_hours'],r['event_observed']))
    return dict(sorted(grouped.items()))

def km_fit(observations):
    """Single-pass Kaplan-Meier; returns (times, survival, median)."""
    ordered=sorted(observations,key=lambda o:o[0]);n=len(ordered)
    times=[];curve=[];survival=1.;median=None;at_risk=n;i=0
    while i<n:
        t=ordered[i][0];events=censored=0
        while i<n and ordered[i][0]==t:
            if ordered[i][1]:events+=1
            else:censored+=1
            i+=1
        if events:survival*=1-events/at_risk
        times.append(t);curve.append(survival)
        if median is None and survival<=.5:median=t
        at_risk-=events+censored
    return times,curve,median

def _step_values(times,curve,grid):
    values=[];j=-1
    for g in grid:
        while j+1<len(times) and times[j+1]<=g:j+=1
        values.append(curve[j] if j>=0 else 1.)
    return values

def _percentile(ordered,q):
    if not ordered:return None
    if len(ordered)==1:return ordered[0]
    pos=q*(len(ordered)-1);lo=int(pos);hi=min(lo+1,len(ordered)-1)
    return ordered[lo]+(ordered[hi]-ordered[lo])*(pos-lo)

def _band(samples_by_point,grid,alpha):
    lower=[];upper=[]
    for samples in samples_by_point:
        s=sorted(samples);lower.append(_percentile(s,alpha/2));upper.append(_percentile(s,1-alpha/2))
    return {"time":list(grid),"lower":lower,"upper":upper}

def cluster_bootstrap(rows_a,rows_b,grid_a,grid_b,confidence,seed,replicates,cohort_a,cohort_b):
    rolls_a=_rolls(rows_a);rolls_b=_rolls(rows_b)
    pools_a=list(rolls_a.values());pools_b=list(rolls_b.values())
    rng=random.Random(seed);alpha=1-confidence
    band_a=[[] for _ in grid_a];band_b=[[] for _ in grid_b]
    medians_a=[];medians_b=[];diffs=[];not_reached=[]
    for rep in range(replicates):
        obs_a=[o for _ in pools_a for o in pools_a[int(rng.random()*len(pools_a))]]
        obs_b=[o for _ in pools_b for o in pools_b[int(rng.random()*len(pools_b))]]
        ta,sa,ma=km_fit(obs_a);tb,sb,mb=km_fit(obs_b)
        for k,v in enumerate(_step_values(ta,sa,grid_a)):band_a[k].append(v)
        for k,v in enumerate(_step_values(tb,sb,grid_b)):band_b[k].append(v)
        if ma is not None:medians_a.append(ma)
        if mb is not None:medians_b.append(mb)
        if ma is None or mb is None:not_reached.append(rep)
        else:diffs.append(mb-ma)
    medians_a.sort();medians_b.sort();diffs.sort()
    def group(cohort,rolls,band,grid,medians):
        return {"cohort_id":cohort[0],"code":cohort[1],"rolls":len(rolls),"roll_numbers":list(rolls),"band":_band(band,grid,alpha),"median_interval":[_percentile(medians,alpha/2),_percentile(medians,1-alpha/2)] if medians else None,"median_valid":len(medians),"median_not_reached":replicates-len(medians)}
    return {"method":BOOTSTRAP_METHOD,"seed":seed,"replicates":replicates,"confidence":confidence,
        "groups":[group(cohort_a,rolls_a,band_a,grid_a,medians_a),group(cohort_b,rolls_b,band_b,grid_b,medians_b)],
        "median_difference":{"order":"B-A","valid":len(diffs),"not_reached":len(not_reached),"not_reached_replicates":not_reached,"interval":[_percentile(diffs,alpha/2),_percentile(diffs,1-alpha/2)] if diffs else None}}
