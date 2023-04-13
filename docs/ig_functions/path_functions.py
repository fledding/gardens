import os
def define_path_functions():
    get_name = lambda p : '.'.join(p.split('/')[-1].split('.')[:-1])
    get_entries = lambda txt : (txt.split('\n')[0],
                            {e for e in txt.split('\n') if e.isalnum()} )          
    get_ratio = lambda s : int(''.join([
                            c for c in s[1:s.index('/')]
                            ])) / int(
                            ''.join([s for s in s[s.index('/')+1:]])
                            )
    get_trait_path = lambda p : os.path.join(
                                '/'.join(p.split('/')[:-1]),
                                '%' + get_name(p) + '.txt'
                                )
    get_parent = lambda p : '/'.join(p.split('/')[:-1])
    get_p_from_trait_p = lambda p : p[:p.index('%')] + p[p.index('%')+1:]
    return get_name,get_entries,get_ratio,get_parent,get_trait_path,get_p_from_trait_p