"""ERSE temporal persistence: accelerated logical sleep, not neuroscience simulation."""
from rsi002 import Engine, Frame, State
from dataclasses import replace

SCHEDULE = ('WAKE',)*12+('N1',)*3+('N2',)*4+('N3',)*5+('REM',)*4
PHASE_HZ={'WAKE':20,'N1':6,'N2':12,'N3':2,'REM':6}

class CyclicEngine(Engine):
    def __init__(self, cyclic=True):
        super().__init__(); self.cyclic=cyclic; self.events=[]; self.replay=[]
    def step(self, observations, resistance):
        t=self.memory.archive[-1][0].tick
        phase=SCHEDULE[t%len(SCHEDULE)] if self.cyclic else 'WAKE'
        current=self.memory.pull(t)
        if phase=='WAKE': signals=tuple(observations)
        elif phase=='REM':
            prior=self.memory.pull(max(0,t-3)); signals=tuple(s.last for s in prior.states)
            self.replay.append(prior.tick)
        else: signals=tuple(s.last for s in current.states)
        frame=super().step(signals,resistance)
        self.events.append((t,phase,tuple(signals),tuple(resistance)))
        return frame

def trial(pattern,cyclic):
    e=CyclicEngine(cyclic)
    for t,load in enumerate(pattern):
        signal=max(0,min(8,load+t%3-1));e.step([signal]*9,[load]*9)
    states=e.memory.archive[-1][0].states
    return {'alive':sum(s.energy>0 for s in states),'energy':[s.energy for s in states], 'functional_steps':[s.position for s in states], 'audit':e.memory.verify(),'replays':len(e.replay)}

def experiment():
    patterns={'steady':[4]*28,'steps':[2]*7+[7]*7+[1]*7+[5]*7,'alternating':[0,8]*14}
    return {n:{'cyclic':trial(p,True),'awake':trial(p,False)} for n,p in patterns.items()}
if __name__=='__main__':
    import json; print(json.dumps(experiment(),indent=2))
