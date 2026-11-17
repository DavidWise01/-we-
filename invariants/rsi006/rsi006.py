"""RSI-006: rotating sentinel with bounded emergency wake; ERSE logical model."""
from rsi002 import Engine, State, Frame
TEAMS=((0,1,2),(3,4,5),(6,7,8))
class Handoff(Engine):
    def __init__(self, threshold=3, calm=2):
        super().__init__()
        self.threshold=threshold; self.calm=calm
        self.alert=[False]*3; self.quiet=[0]*3; self.last=[4]*3
        self.actions=[4]*9; self.work=0; self.events=[]
    def step(self, observations, resistance, unavailable=()):
        obs,loads=tuple(observations),tuple(resistance)
        if len(obs)!=9 or len(loads)!=9 or any(type(x)!=int or not 0<=x<=8 for x in obs+loads):
            raise ValueError('nine signals and loads in [0,8]')
        t=self.memory.archive[-1][0].tick
        current=self.memory.pull(t); saved=self.memory.pull(max(0,t-3))
        states=list(current.states); roles=['LOST']*9; active=[]
        for k,team in enumerate(TEAMS):
            order=team[t%3:]+team[:t%3]
            live=[i for i in order if states[i].energy>0 and i not in unavailable]
            if not live:continue
            up=live[0]; signal=obs[up]
            if abs(signal-self.last[k])>=self.threshold or up!=order[0]:
                self.alert[k]=True;self.quiet[k]=0
            elif self.alert[k]:
                self.quiet[k]+=1
                if self.quiet[k]>=self.calm:self.alert[k]=False
            self.last[k]=signal
            for i in live:
                s=states[i]; awake=self.alert[k] or i==up
                roles[i]='UP' if awake else ('REPLAY' if i==order[2] else 'REST')
                o=obs[i] if awake else signal
                if awake:
                    pred=max(0,min(8,s.last+s.velocity))
                    w=2 if self.geometry[i]=='box' else (3 if abs(s.velocity)>1 else 1)
                    a=min(range(9),key=lambda a:(abs(a-pred)+w*abs(a-o)+abs(a-saved.states[i].last),a))
                    self.work+=27;active.append(i)
                else:
                    # Cheap direct response, not three nine-action scoring arrays.
                    a=signal;self.work+=1
                self.actions[i]=a
                states[i]=State(max(0,s.energy-1-abs(a-loads[i])),s.position+int(abs(a-loads[i])<=1),o,o-s.last)
        frame=Frame(t+1,tuple(states));self.memory.push(frame)
        self.events.append((t,tuple(roles),tuple(active),tuple(self.alert)))
        return frame

def experiment():
    cases={'steady':[[4]*9 for _ in range(28)],
           'steps':[[[2,7,1,5][t//7]]*9 for t in range(28)],
           'alternating':[[8*(t%2)]*9 for t in range(28)],
           'local_shock':[[8 if 7<=t<14 and i<3 else 4 for i in range(9)] for t in range(28)],
           'hidden_gradient':[[i%3*4 for i in range(9)] for t in range(28)]}
    out={}
    for name,pattern in cases.items():
        a,b=Handoff(),Engine()
        for loads in pattern:a.step(loads,loads);b.step(loads,loads)
        out[name]={'watch_alive':sum(s.energy>0 for s in a.memory.archive[-1][0].states),
                   'awake_alive':sum(s.energy>0 for s in b.memory.archive[-1][0].states),
                   'watch_work':a.work,'awake_work':28*9*27,
                   'audit':a.memory.verify()}
    return out
if __name__=='__main__':
    import json;print(json.dumps(experiment(),indent=2))
