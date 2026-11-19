from fractions import Fraction as F
N=(-1,-2,-3,-4,-5,5,4,3,2,1)
def relay(x,b):
    x,b=list(map(F,x)),list(map(F,b))
    if len(x)!=10 or len(b)!=10 or sum(x)!=20 or min(x+b)<0: raise ValueError('state')
    for i in range(10):
        if x[i]<=2: continue
        for direction in (1,-1):
            path=[i]
            for k in range(1,10):
                j=(i+k*direction)%10; path.append(j)
                if x[j]>2: break
                if x[j]==2: continue
                amount=min(x[i]-2,2-x[j],*(b[p] for p in path[:-1]))
                if amount<=0: break
                x[i]-=amount; x[j]+=amount
                for p in path[:-1]: b[p]-=amount
                return x,b,amount*(len(path)-1),(tuple(path),amount)
    return x,b,F(0),None

def run():
    x=[F(8 if n==-5 else 12 if n==5 else 0) for n in N]
    b=[F(54)]*10; spent=F(0)
    for n in range(360):
        old=sum((v-2)**2 for v in x)
        x,b,c,receipt=relay(x,b);spent+=c
        assert sum(x)==20 and sum(b)+spent==540 and min(x+b)>=0
        assert sum((v-2)**2 for v in x)<=old
        if n<10: print(n+1, 'residual',max(abs(v-2) for v in x),'spent',spent,'receipt',receipt)
    print('FINAL',max(abs(v-2) for v in x),sum(b),spent)
if __name__=='__main__':run()
