from typing import Any,Iterable,Dict
import numpy as np,pandas as pd
from .config import FEATURE_COLUMNS
def num(v,d=0.):
    try:return float(v)
    except:return d
def cycle_to_features(rows:Iterable[dict])->Dict[str,float]:
    rows=list(rows)
    if not rows: raise ValueError('No telemetry rows supplied.')
    out={}; c=[num((r.get('cycle') or {}).get('duration')) for r in rows]; out['cycle_duration']=next((x for x in reversed(c) if x>0),0.)
    states=[r.get('state','IDLE') for r in rows]; out['busy_ratio']=float(np.mean([s!='IDLE' for s in states])); out['state_transitions']=float(sum(states[i]!=states[i-1] for i in range(1,len(states))))
    out['servo_error_count']=float(sum(bool((r.get(a) or {}).get('error')) for r in rows for a in ('axis1','axis2','axis3')))
    for a,p in [('axis1','a1'),('axis2','a2'),('axis3','a3')]:
        pos=[]; pe=[]; sp=[]; act=[]; dev=[]
        for r in rows:
            x=r.get(a,{}) or {}; position=num(x.get('position')); target=num(x.get('target')); command=abs(num(x.get('speed'))); actual=abs(num(x.get('actual_speed')))
            pos.append(position); pe.append(abs(target-position)); sp.append(command); act.append(actual); dev.append(abs(command-actual)/command if command>1 and actual>1 else 0.)
        out.update({f'{p}_mean_pos_error':float(np.mean(pe)),f'{p}_max_pos_error':float(np.max(pe)),f'{p}_std_pos_error':float(np.std(pe)),f'{p}_mean_speed':float(np.mean(sp)),f'{p}_mean_actual_speed':float(np.mean(act)),f'{p}_speed_deviation':float(np.mean(dev)),f'{p}_position_std':float(np.std(pos))})
    return {k:float(out.get(k,0)) for k in FEATURE_COLUMNS}
