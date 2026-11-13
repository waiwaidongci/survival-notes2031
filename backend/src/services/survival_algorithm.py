from .km_algorithm import kaplan_meier
from .logrank_algorithm import logrank
from .bootstrap_algorithm import validate_rolls,cluster_bootstrap
from ..constants.bootstrap import DEFAULT_SEED,REPLICATES,BOOTSTRAP_METHOD,METHOD_VERSION
from ..utils.fingerprint import fingerprint

def analyze_survival(cohort_a,cohort_b,rows_a,rows_b,confidence=.95,seed=DEFAULT_SEED,replicates=REPLICATES):
    if cohort_a.id==cohort_b.id:raise ValueError("必须选择两批不同工艺")
    validate_rolls(rows_a,rows_b,cohort_a.code,cohort_b.code)
    groups=[];inputs=[]
    for cohort,rows in [(cohort_a,rows_a),(cohort_b,rows_b)]:
        rows=sorted(rows,key=lambda x:x['code'])
        if len({r['code'] for r in rows})!=len(rows):raise ValueError("同组试件编号重复")
        observations=[(r['duration_hours'],r['event_observed']) for r in rows]
        info={"id":cohort.id,"code":cohort.code,"name":cohort.name,"process":cohort.process}
        groups.append({"cohort":info,**kaplan_meier(observations,confidence)})
        inputs.append({"cohort":info,"rows":rows})
    comparison=logrank([(r['duration_hours'],r['event_observed']) for r in rows_a],[(r['duration_hours'],r['event_observed']) for r in rows_b])
    grid_a=sorted({r['duration_hours'] for r in rows_a});grid_b=sorted({r['duration_hours'] for r in rows_b})
    bootstrap=cluster_bootstrap(rows_a,rows_b,grid_a,grid_b,confidence,seed,replicates,(cohort_a.id,cohort_a.code),(cohort_b.id,cohort_b.code))
    return {"groups":groups,"logrank":comparison,"bootstrap":bootstrap,"confidence":confidence,"time_unit":"小时","input_hash":fingerprint({"method":METHOD_VERSION,"groups":inputs,"confidence":confidence,"risk_times":[400,800,1200],"time_unit":"hours","bootstrap":{"method":BOOTSTRAP_METHOD,"seed":seed,"replicates":replicates}}),"method_version":METHOD_VERSION,"interpretation":"两批耐久分布存在统计差异；结合删失与工艺条件审阅" if comparison['estimable'] and comparison['p_value']<.05 else "尚无足够差异证据；不能据此认定两批等效" if comparison['estimable'] else "事件信息不足，log-rank不可估计","assumptions":"独立卷为抽样单元、卷内试件缺陷相关、非信息性右删失；同一时点事件先计入风险集，再移除事件与删失。Greenwood区间与整卷重抽样带都是逐点区间，不是同时置信带；中位未达到的重复单列计数，不混入区间数值；比较为关联研究，不自动决定维护周期。"}
