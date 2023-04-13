import networkx as nx
import sys
import os
import json
import copy
sys.path.append('/Users/basic/Documents/gardens/docs')
import instabot_spider as ib
from functools import reduce
# 
#     '''
#         super().__init__(id, mode_obtained, parent)
#     def __init__(self, id, mode_obtained, parent):
# class Leaf(Branch):
#         
# 
#         self.mode_obtained = mode_obtained
#         super().__init__(id,**kwargs)
#     def __init__(self, id, mode_obtained, parent, **kwargs):
# class Branch(Root):
#             
#     
#     
# 
#                 self.attrs[key] = None
#             except ValueError:
#                 self.found_attrs.append(key)
#                 self.attrs[key] = kwargs[key]
#             try:
#         for key in self.possible_attrs:
# 
#         self.found_attrs = []
#         self.attrs = {}
# 
#     def __init__(self, id, **kwargs):
# class Root(object):
# '''

class Leaf(object):
#     base class for ig tree.
    def __init__(self, id, mode_obtained, parent):
#         assumes id is numeric string, mode_obtained string, parent string
        self.id = id
#         dictionary of attributes
        self.attrs = {}
#         containers with id strings representing edges
        self.attrs['followee_of'] = set()
        self.attrs['follower_of'] = set()
#         int representing # of other accs with same edge
        self.attrs['mutual_follower'] = 0
        self.attrs['mutual_followee'] = 0
#         raise error if invalid lineage type
        if mode_obtained == 'followers':
            self.attrs['follower_of'].add(parent)
        elif mode_obtained == 'followings':
            self.attrs['followee_of'].add(parent)
        else:
            raise ValueError('{} not valid'.format(mode_obtained))
        
    
    def __eq__(self,other):
#         eq for comparison and set containment
        return isinstance(self,Leaf) and isinstance(other,Leaf) \
        and self.id == other.id

    def __hash__(self):
#         for set containment
#         note that id uniquely identifies account
        return hash(self.id)
    
    def get_attrs(self):
#         getter for attributes
        return self.attrs
        
#     def absorb(self,other):
# #         
#         for provenance in ['follower_of','followee_of']:
#             self.attrs[provenance].extend(other.attrs[provenance])
#         

class Branch(Leaf):
#     child class of leaf, for scraped accounts
    def __init__(self, id, **meta):
#         assumes meta is a dictionary of kwargs
        self.id = id
        self.attrs = {}
        self.topics = ['mode','limit','status','username','followers','followees',
        'followee_of','follower_of','mutual_followee','mutual_follower']
        self.set_attrs(**meta)
        
    def set_attrs(self, **meta):
#         set attrs by input kwargs
        for val in self.topics:
            try:
#                 set val
                self.attrs[val] = meta[val]
            except KeyError as e:
#                 or init as empty of val type
                if val in ['followee_of','follower_of']:
                    self.attrs[val] = set()
                elif val in ['mutual_follower','mutual_followee']:
                    self.attrs[val] = 0
                else:
                    self.attrs[val] = ''
    
        
    

# 
# def create_graph_instabot(library):
#     G = nx.DiGraph()
#     
#     for path in library:
#         if not os.path.isfile(path): 
#             print('404 {}'.format(path)); continue
#         steps = path.split('/')
#         filename = steps[-1]
#         if filename[0] == '.':
#             continue
#         try:
#             id,mode = filename.split('_')
#         except ValueError:
#             print('format error {}'.format(filename))
#             continue
#         with open(path) as f:
#             data = f.read()
#             meta_raw,*children = data.split('\n')
# 
#         try:
#             meta = json.loads(meta_raw[1:])
#         except json.decoder.JSONDecodeError:
#             print(meta_raw)
#         
#         mode = meta['mode']
#         limit = meta['limit']
#         
#             
#         node_attrs = {key : meta[key] for key in meta if not key in ['mode','limit']}
#         G.add_node(id,**node_attrs)
#         E = 0 if len(children) < limit else 1
#         if mode == 'followings':
#             for child in children:
#                 G.add_node(child)
#                 G.add_edge(id,child,ERROR=E)
#         elif mode == 'followers':
#             for child in children:
#                 G.add_node(child)
#                 G.add_edge(child,id,ERROR=E)
#                 
#                 
#         else:
#             print('invalid mode {}'.format(mode))
#             
#     return G

# def set_nodes(G, library):
#     all = {}
#     for path in library:
# 
#         data = read_ib_file(path)
#         if None in data:
#             continue
#         
#         id,mode,meta,children = data
#         



        
        
        
        

def read_ib_file(path):
#     helper that takes a path and gets metadata (attrs and scrape mode), entries, and id
    if not os.path.isfile(path): 
        raise ValueError('404 {}'.format(path))
        
    steps = path.split('/')
#     file is of form {id}_{mode}.txt
    file = steps[-1]
    
    if file[0] == '.':
#         .DS_Store
        raise ValueError('.DS_Store')
        
    #     filename is of form {id}_{mode}
    filename = file.split('.')[0]
    try:
        id,mode = filename.split('_')
    except ValueError:
        raise ValueError('format error {}'.format(filename))
    
#     file content is of the form '${key1:attr1,...}\n{id1}\n...{idn}\n
    with open(path) as f:
        meta_raw,*entries = f.read().split('\n')
    children = {e for e in entries if e != ''}
    
#     decode metadata dict
    try:
        meta = json.loads(meta_raw[1:])
    except json.decoder.JSONDecodeError:
        raise ValueError('invalid meta {}'.format(meta_raw))
    
    return id,mode,meta,children
        
def set_tree(dir):
    
#     branches maps ids to branch structures
    branches = {}
#     leaves maps ids to dict containing edge attributes
    leaves = {}
#     synonym maps
    mv = lambda mode:{'followers':'followee_of','followings':'follower_of'}[mode] 
    uv = lambda mode:{'followers':'mutual_followee','followings':'mutual_follower'}[mode]
    
#     loop through data dir
    print('reading files for tree {}...'.format(dir))
    for file in os.listdir(dir):
        path = os.path.join(dir,file)
#         get data or skip if invalid
        try:
            data = read_ib_file(path)
        except ValueError as e:
            print(e)
            continue
        
        branch_id,mode,meta,children = data
#         init branch object
        # branches[branch_id] = Branch(branch_id, **meta)
#         n is # of mutuals for leaves associated with branch
        n = len(children) - 1
#         loop thru connected nodes
        for child_id in children:
#             if exists leaf
            if child_id in leaves.keys():
#                 add parent under attrs
                temp = copy.copy(leaves[child_id])
                temp[mv(mode)].add(branch_id)
                leaves[child_id] = temp
#             else
            else:
                temp = Leaf(child_id,mode,branch_id).attrs
                leaves[child_id] = temp
#                 add n mutuals of mode
            # leaves[child_id][uv(mode)] += n
    print('pruning...')
    skipped = set()
    for id in branches:
        try:
            curr_leaf = copy.copy(leaves[id])
        except KeyError:
            skipped.add(id)
            continue
        curr_branch = branches[id]
        for key in curr_leaf:
            curr_branch.attrs[key] = curr_leaf[key]
    
        leaves.pop(id)
    print('skipped ' + str(len(skipped)))
    return leaves,branches
def set_fnodes(graph,mode,root,collection):
    for item in collection:
        if mode == 'followers':
            graph.add_edge(item,root)
        elif mode == 'followings':
            graph.add_edge(root,item)
        else:
            raise ValueError
'''
class random_walk(object):

def set_off(G, k, f, alpha=0, theta=1):
    node0 
    return random_walk(G, k, node0, f, alpha, theta)
def random_walk(G, k, node, f, alpha, theta):

'''
if __name__ == '__main__':
#     get leaf and branch containers
    leaves,branches = set_tree('/Users/basic/venv/Instaspider/data')
#     init empty digraph
    G = nx.DiGraph()
#     keys
    mfr = 'mutual_follower'; mfe = 'mutual_followee'
#     function that maps an id to a dict consisting of its int mutual attrs
    get_mutual_vals = lambda id : {mfr : leaves[id][mfr], mfe : leaves[id][mfe]}
    print('adding leaves...') #log
    for id in leaves:
#         get follower and followee sets
        followers = leaves[id]['followee_of']
        followees = leaves[id]['follower_of']
        mutual_vals = get_mutual_vals(id)
#         add node with mutual val attrs
        G.add_node(id, **mutual_vals)
#         add directed edges
        G.add_edges_from([(flwr,id) for flwr in followers])
        G.add_edges_from([(id,flwe) for flwe in followees])
    print('adding branches...')
    for id in branches:
        # get branch object
        branch = branches[id]
        # get edge attrs
        followers = branch.attrs.pop('followee_of')
        followees = branch.attrs.pop('follower_of')
        graph_attrs = ['followee_of','follower_of']
        # node attrs
        node_attrs = {key:branch.attrs[key] for key in branch.attrs \
                        if not key in graph_attrs and key != 'mode'}
        G.add_node(id,**node_attrs)
        # add directed edges
        G.add_edges_from([(flwr,id) for flwr in followers])
        G.add_edges_from([(id,flwe) for flwe in followees])
    
    # print('writing gexf...')
    # nx.write_gexf(G,'/Users/basic/venv/iboop1.gexf')
    