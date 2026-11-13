from ..models import TestCohort,Specimen,FollowupEvent
from ..utils.serialize import record

def list_cohorts(db):
    result=[]
    for c in db.query(TestCohort).order_by(TestCohort.code):
        events=db.query(FollowupEvent).join(Specimen).filter(Specimen.cohort_id==c.id).all()
        specimens=db.query(Specimen).filter_by(cohort_id=c.id).all()
        rolls={s.roll_no.strip() for s in specimens if s.roll_no and s.roll_no.strip()}
        missing=sum(1 for s in specimens if not (s.roll_no or '').strip())
        result.append(dict(record(c),specimen_count=len(events),events=sum(x.event_observed for x in events),censored=sum(not x.event_observed for x in events),roll_count=len(rolls),roll_missing=missing))
    return result
