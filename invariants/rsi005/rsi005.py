"""Rotating 1-up/2-down teams; logical ticks, not biological sleep."""
from rsi002 import Engine
from rsi004 import experiment as baseline
TEAMS=((0,1,2),(3,4,5),(6,7,8))
class Watch(Engine):
    def __init__(self):
        super().__init__(); self.events=[]
    def step(self, observations, resistance):
        t=self.memory.archive[-1][0].tick
        current=self.memory.pull(t); prior=self.memory.pull(max(0,t-3))
        signals=[s.last for s in current.states]; roles=['']*9; sentinels=[]
        for team in TEAMS:
            order=team[t%3:]+team[:t%3]
            live=[i for i in order if current.states[i].energy>0]
            if not live:
                for i in team: roles[i]='LOST'
                continue
            up=live[0]; sentinels.append(up)
            for i in team:
                if i==up: roles[i]='UP'; signals[i]=observations[up]
                elif i==order[2]: roles[i]='REPLAY'; signals[i]=observations[up]
                else: roles[i]='REST'; signals[i]=observations[up]
        # Replay is recorded separately; current sentinel signal is used for response.
        replay={i:prior.states[i].last for i,r in enumerate(roles) if r=='REPLAY'}
        f=super().step(signals,resistance)
        self.events.append((t,tuple(roles),tuple(sentinels),replay));return f

def experiment():
    patterns={'steady':[4]*28,'steps':[2]*7+[7]*7+[1]*7+[5]*7,'alternating':[0,8]*14}
    result=baseline()
    for name,pattern in patterns.items():
        e=Watch()
        for t,load in enumerate(pattern):
            signal=max(0,min(8,load+t%3-1));e.step([signal]*9,[load]*9)
        s=e.memory.archive[-1][0].states
        result[name]['watch']={'alive':sum(x.energy>0 for x in s),'energy':[x.energy for x in s],'audit':e.memory.verify(),'sentinel_ticks':sum(len(x[2]) for x in e.events)}
    return result
if __name__=='__main__':
    import json; print(json.dumps(experiment(),indent=2))
