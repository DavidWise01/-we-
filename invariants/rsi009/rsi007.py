"""Ephemeral rank/file offsets; separate identity from duty. Logical model."""
AXIS=(1,2,3,4,5,0,-5,-4,-3,-2,-1)
TEAMS=((0,1,2),(3,4,5),(6,7,8))
def frame(t, signals, prior, unavailable=()):
    if len(signals)!=9 or len(prior)!=9 or t<0: raise ValueError('invalid frame')
    if any(type(i)!=int or not 0<=i<9 for i in unavailable): raise ValueError('invalid identity')
    roles={}; alerts=[]; work=0
    for k,team in enumerate(TEAMS):
        order=team[t%3:]+team[:t%3]; live=[i for i in order if i not in unavailable]
        if not live: alerts.append(k); continue
        up=live[0]
        alarm=up!=order[0] or any(abs(signals[i]-prior[i])>=3 or abs(signals[i]-signals[up])>=3 for i in live)
        if alarm: alerts.append(k)
        for i in live:
            duty='UP' if alarm or i==up else ('REST' if i==live[1] else 'REPLAY')
            rank=AXIS[(t+k)%11]; file=AXIS[(t+order.index(i)+3)%11]
            roles[i]={'rank':rank,'file':file,'duty':duty,'geometry':'torroid' if (i+1)%2 else 'box'}
            work+=27 if duty=='UP' else 2
    return {'tick':t,'expires':t+1,'identity':'{{j}}','roles':roles,'alerts':alerts,'work':work}
def valid(record,t):return record['tick']==t and t<record['expires']
