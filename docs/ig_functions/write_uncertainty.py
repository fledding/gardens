import os
from json import loads
path = '/Users/basic/Desktop/dethrowrexords'
ns = {}
for r,d,f in os.walk(path):
    for g in f:
        file = os.path.join(r,g)
        if g[0] == '%': 
            with open(file,'r') as data:
                d = loads(data.read())
                name = g[1:]
                ns[name] = str(d['n_followers'])
        else: 
            continue
    for g in f:
        file = os.path.join(r,g)
        if not g[0] in ['%','.']:
            with open(file,'r') as txt:
                L = txt.read()
            with open(file,'w') as paper:
                
                b = ns[g]
                a = str(len(L.split('\n')))
                paper.write('!%s/%s' % (a,b) )
                paper.write(L)
        else:
            continue
            