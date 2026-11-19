from fractions import Fraction as F
N=(-1,-2,-3,-4,-5,5,4,3,2,1)
def relay(x,b,permit):
    x,b=list(map(F,x)),list(map(F,b))
    if len(x)!=10 or len(b)!=10 or len(permit)!=10 or sum(x)!=20 or min(x+b)<0: raise ValueError('state')
    candidates=[]
    for i in range(10):
        if x[i]<=2 or not permit[i]: continue
        for direction in (1,-1):
            path=[i]
            for k in range(1,10):
                j=(i+k*direction)%10;path.append(j)
                if not permit[j] or x[j]>2: break
                if x[j]==2: continue
                amount=min(x[i]-2,2-x[j],*(b[p] for p in path[:-1]))
                if amount>0: candidates.append((len(path),tuple(path),amount))
                break
    if not candidates:return x,b,F(0),None
    _,path,amount=min(candidates)
    x[path[0]]-=amount;x[path[-1]]+=amount
    for p in path[:-1]:b[p]-=amount
    return x,b,amount*(len(path)-1),(path,amount)

def run():
    x=[F(8 if n==-5 else 12 if n==5 else 0) for n in N];b=[F(54)]*10;spent=F(0)
    for k in range(360):
        old=sum((v-2)**2 for v in x);x,b,c,r=relay(x,b,[True]*10);spent+=c
        assert sum(x)==20 and sum(b)+spent==540 and min(x+b)>=0 and sum((v-2)**2 for v in x)<=old
        if r:print(k+1,'residual',max(abs(v-2) for v in x),'spent',spent,'receipt',r)
    print('FINAL',max(abs(v-2) for v in x),sum(b),spent)
if __name__=='__main__':run()
