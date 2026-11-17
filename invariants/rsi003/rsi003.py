"""Matched-energy resistance transfer; no selection or reward update."""
from rsi002 import Engine, State, Frame, run
from dataclasses import replace
from copy import deepcopy

def trial(pattern, inherited):
    e=deepcopy(run()) if inherited else Engine()
    if inherited:
        f=e.memory.archive[-1][0]
        e.memory.push(Frame(f.tick+1,tuple(replace(s,energy=100,position=0) for s in f.states)))
    for t,load in enumerate(pattern):
        signal=max(0,min(8,load+(t%3-1)))
        e.step([signal]*9,[load]*9)
    return [s.energy for s in e.memory.archive[-1][0].states],e.memory.verify()

def experiment():
    patterns={'step':[2]*10+[7]*10+[1]*10,'reverse':[8-t%9 for t in range(30)],'alternating':[0,8]*15,'ramp':[t//4 for t in range(30)]}
    return {name:{'inherited':trial(p,True),'cold':trial(p,False)} for name,p in patterns.items()}
if __name__=='__main__':
    import json
    print(json.dumps(experiment(),indent=2))
