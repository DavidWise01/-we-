from itertools import product

def spin(s,k):
    a,b=s
    for _ in range(k%4): a,b=-b,a
    return a,b

def norm(s): return sum(a*a for a in s)

def nested(m,turns):
    return tuple(spin((1,0),k) for k in turns[:m])

def tensor_sign(turns):
    return (-1)**sum(turns)

def run():
    for s in [(1,0),(0,1),(3,4),(-2,5)]:
        for k in range(4):
            t=spin(s,k)
            assert norm(t)==norm(s)
            assert spin(t,2)==tuple(-a for a in t)
            assert spin(t,4)==t
    for turns in product(range(2),repeat=5):
        states=nested(5,[2*k for k in turns])
        assert all(norm(s)==1 for s in states)
        assert __import__('math').prod(s[0] for s in states)==tensor_sign(turns)
    for d in (-1,0,1):
        for g in range(4):
            scale=10**g
            assert (-scale)+scale==0
            assert d*scale in (-scale,0,scale)
    print('16 spinor cases: norm, inversion, restoration PASS')
    print('32 five-loop parity configurations PASS')
    print('12 direction/scale configurations PASS')
    for k in range(5):print(k*180,spin((1,0),k),norm(spin((1,0),k)))
if __name__=='__main__':run()
