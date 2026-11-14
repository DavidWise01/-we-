"""WAG-036 semantic graph reference. Reviewer relations are declarations."""
import hashlib,json
from decimal import Decimal
class ClaimGraph:
    def __init__(self,alpha="0.05"):
        self.alpha=Decimal(alpha);self.claims={};self.edges=[];self.roots={};self.tests={};self.log=[]
        if not 0<self.alpha<1:raise ValueError("alpha")
        self._log("genesis",{"alpha":str(self.alpha)})
    def _hash(self,x):
        return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def _log(self,k,p):
        r={"seq":len(self.log),"kind":k,"data":p,"prev":self.log[-1]["hash"] if self.log else "0"*64}
        r["hash"]=self._hash(r);self.log.append(r)
    def verify(self):
        return all(r["seq"]==i and r["prev"]==(self.log[i-1]["hash"] if i else "0"*64) and r["hash"]==self._hash({k:v for k,v in r.items() if k!="hash"}) for i,r in enumerate(self.log))
    def claim(self,id,proposition,domain):
        if not all([id,proposition,domain]) or id in self.claims:raise ValueError("claim")
        self.claims[id]=(proposition,domain);self.roots[id]=set();self._log("claim",{"id":id,"proposition":proposition,"domain":domain})
    def equivalents(self,id):
        seen={id};todo=[id]
        while todo:
            u=todo.pop()
            for a,b,k,*_ in self.edges:
                v=b if a==u else a if b==u else None
                if k=="equivalent" and v and v not in seen:seen.add(v);todo.append(v)
        return seen
    def relation(self,a,b):
        if a not in self.claims or b not in self.claims:raise ValueError("unknown")
        if b in self.equivalents(a):return "equivalent"
        def entails(s,t):
            seen={s};todo=[s]
            while todo:
                x=todo.pop()
                for u,v,k,*_ in self.edges:
                    if k=="entails" and u==x and v not in seen:
                        if v==t:return True
                        seen.add(v);todo.append(v)
            return False
        if entails(a,b):return "entails"
        if entails(b,a):return "entailed_by"
        for x,y,k,*_ in self.edges:
            if {x,y}=={a,b} and k in ("overlaps","disjoint"):return k
        return "unknown"
    def relate(self,a,b,kind,reviewer,evidence):
        if a not in self.claims or b not in self.claims or a==b or kind not in ("equivalent","entails","overlaps","disjoint") or not reviewer or not evidence:raise ValueError("relation")
        if any({x,y}=={a,b} and ((k=="disjoint" and kind!="disjoint") or (kind=="disjoint" and k!="disjoint") or k==kind) for x,y,k,*_ in self.edges):raise ValueError("conflict")
        if kind=="disjoint" and self.relation(a,b)=="equivalent":raise ValueError("equivalence conflict")
        self.edges.append((a,b,kind,reviewer,tuple(evidence)))
        self._log("relation",{"a":a,"b":b,"kind":kind,"reviewer":reviewer,"evidence":list(evidence)})
    def observe(self,claim,root):
        if claim not in self.claims or not root or root in self.roots[claim]:raise ValueError("evidence")
        self.roots[claim].add(root);self._log("observe",{"claim":claim,"root":root})
    def distinct_roots(self,claims):
        if any(c not in self.claims for c in claims):raise ValueError("claim")
        return len(set().union(*(self.roots[c] for c in claims)))
    def register(self,id,claim,roots,alpha):
        a=Decimal(str(alpha));roots=frozenset(roots)
        if id in self.tests or claim not in self.claims or not roots or a<=0 or a>self.remaining:raise ValueError("registration")
        if any(roots & x["roots"] for x in self.tests.values()):raise ValueError("recycled confirmatory evidence")
        self.tests[id]={"claim":claim,"roots":roots,"alpha":a}
        self._log("test",{"id":id,"claim":claim,"roots":sorted(roots),"alpha":str(a)})
    @property
    def remaining(self):return self.alpha-sum((v["alpha"] for v in self.tests.values()),Decimal(0))
if __name__=="__main__":
    g=ClaimGraph()
    for c in "ABCD":g.claim(c,c,"sensors")
    g.relate("A","B","equivalent","reviewer",["r1"])
    g.relate("A","C","overlaps","reviewer",["r2"])
    g.relate("A","D","disjoint","reviewer",["r3"])
    g.observe("A","root1");g.observe("B","root1")
    g.register("t1","A",["holdout1"],".02")
    try:g.register("t2","B",["holdout1"],".02")
    except ValueError:print("Recycled test evidence blocked")
    print(g.relation("A","B"),g.relation("A","C"),g.relation("A","D"),g.distinct_roots(["A","B"]),g.remaining,g.verify())
