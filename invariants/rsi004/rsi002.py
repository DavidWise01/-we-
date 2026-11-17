"""ERSE-018 / RSI-002: discrete shared-substrate reference, not atomic physics."""
from dataclasses import dataclass
from collections import OrderedDict, deque
from hashlib import sha256
import json

@dataclass(frozen=True)
class State:
    energy: int = 100
    position: int = 0
    last: int = 4
    velocity: int = 0

@dataclass(frozen=True)
class Frame:
    tick: int
    states: tuple

class Memsistor:
    def __init__(self):
        self.argon = OrderedDict()  # 17 hot frame references
        self.lead = deque(maxlen=208)  # 208 resident frames
        self.archive = []  # append-only reference history, memory-resident
        self.push(Frame(0, (State(),)*9))
    def push(self, frame):
        if self.archive and frame.tick != self.archive[-1][0].tick+1:
            raise ValueError('nonmonotonic tick')
        prev = self.archive[-1][1] if self.archive else '0'*64
        body = json.dumps([prev, frame.tick, [vars(s) for s in frame.states]],sort_keys=True)
        self.archive.append((frame,sha256(body.encode()).hexdigest()))
        self.lead.append(frame)
        self.argon[frame.tick]=frame
        if len(self.argon)>17:self.argon.popitem(last=False)
    def pull(self,tick):
        if tick in self.argon:return self.argon[tick]
        return next((f for f in reversed(self.lead) if f.tick==tick),None)
    def verify(self):
        prev='0'*64
        for i,(f,h) in enumerate(self.archive):
            body=json.dumps([prev,f.tick,[vars(s) for s in f.states]],sort_keys=True)
            if i!=f.tick or sha256(body.encode()).hexdigest()!=h:return False
            prev=h
        return bool(self.archive)

class Engine:
    """Nine branches x nine actions. One logical tick represents one second."""
    def __init__(self):
        self.memory=Memsistor()
        self.geometry=tuple('box' if i%2==0 else 'torroid' for i in range(1,10))
        self.last_layers=None
    def step(self,observations,resistance):
        # observations are noisy signals, not privileged access to actual resistance.
        observations,resistance=tuple(observations),tuple(resistance)
        if len(observations)!=9 or len(resistance)!=9 or any(type(x)!=int or not 0<=x<=8 for x in observations+resistance):
            raise ValueError('nine integer signals and loads in [0,8] required')
        t=self.memory.archive[-1][0].tick
        current=self.memory.pull(t)
        saved=self.memory.pull(max(0,t-3))
        # JIT: predict load from prior observations; OTF: update with current signal.
        jit=tuple(tuple(abs(a-max(0,min(8,s.last+s.velocity))) for a in range(9)) for s in current.states)
        otf=tuple(tuple(abs(a-o) for a in range(9)) for o in observations)
        # PRE-SIST: compare candidate actions against the three-second prior state.
        pre=tuple(tuple(abs(a-s.last) for a in range(9)) for s in saved.states)
        self.last_layers=(jit,otf,pre)
        next_states=[]
        for i,s in enumerate(current.states):
            if s.energy==0:next_states.append(s);continue
            # Same signals and action space for both geometries. Odd branches allow
            # bounded state-dependent weighting; even branches use fixed weighting.
            w=2 if self.geometry[i]=='box' else (3 if abs(s.velocity)>1 else 1)
            action=min(range(9),key=lambda a:(jit[i][a]+w*otf[i][a]+pre[i][a],a))
            cost=1+abs(action-resistance[i]); o=observations[i]
            next_states.append(State(max(0,s.energy-cost),s.position+int(abs(action-resistance[i])<=1),o,o-s.last))
        frame=Frame(t+1,tuple(next_states));self.memory.push(frame);return frame

def run(ticks=30):
    e=Engine()
    for t in range(ticks):
        # Shared deterministic test conditions, no hidden random advantage.
        load=(t*3+(t//5)*2)%9; signal=max(0,min(8,load+((t%3)-1)))
        e.step([signal]*9,[load]*9)
    return e
if __name__=='__main__':
    e=run(); f=e.memory.archive[-1][0]
    print([(i+1,e.geometry[i],s.energy,s.position) for i,s in enumerate(f.states)])
    print('audit',len(e.memory.archive),e.memory.verify())
