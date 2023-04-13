import os
import sys
import json
import networkx as nx
from selenium import webdriver
sys.path.append('/Users/basic/Documents/gardens')
sys.path.append('/Users/basic/Documents/gardens/docs/')
from ig_functions import instagiraffe_login as login
from ig_functions.path_functions import define_path_functions
import time
import __init__ as igir
get_name,get_entries,get_ratio,get_parent,get_trait_path,get_p_from_trait_p = \
define_path_functions()

def get_nodes(library):
    nodes = set()
    for path in library:
        if not os.path.isfile(path): 
            print(path + ' does not xist')
            continue
        name = get_name(path)
        file = open(path)
        status,entries = get_entries(file.read())
        assert ('!' in status or '$' in status)

        with open(get_trait_path(path)) as traits:
            trait_data = json.loads(traits.read())
            
        if status in ('$closed','$failed'):
            nodes.add(name,status=status[1:],E=0,**trait_data)
        else:
            ERROR = get_ratio(status)

            nodes.add(name,status='open',E=ERROR,**trait_data)
    
    return nodes

def create_graph_instabot(library):
    G = nx.DiGraph()
    for path in library:
        if not os.path.isfile(path): 
            print('404 {}'.format(path)); continue
        steps = path.split('/')
        filename = steps[-1]
        if filename[0] == '.':
            continue
        try:
            id,mode = filename.split('_')
        except ValueError:
            print('format error {}'.format(filename))
            continue
        with open(path) as f:
            data = f.read()
            meta_raw,*children = data.split('\n')

        try:
            meta = json.loads(meta_raw[1:])
        except json.decoder.JSONDecodeError:
            print(meta_raw)
        
        mode = meta['mode']
        limit = meta['limit']
        
            
        node_attrs = {key : meta[key] for key in meta if not key in ['mode','limit']}
        G.add_node(id,**node_attrs)
        E = 0 if len(children) < limit else 1
        if mode == 'followings':
            for child in children:
                G.add_node(child)
                G.add_edge(id,child,ERROR=E)
        elif mode == 'followers':
            for child in children:
                G.add_node(child)
                G.add_edge(child,id,ERROR=E)
                
                
        else:
            print('invalid mode {}'.format(mode))
            
    return G
        
        

def create_graph_instagiraffe(library,
                auth=('tatyanaponidaeva','865256bhtd22'),
                init_attrs=True,
                mode = 'followers'):
    G = nx.DiGraph()
    if init_attrs:
        s = login.login_deprecated(auth)
        
    for path in library:
        if not os.path.isfile(path): print('404 ' + path); continue
        
        name = get_name(path)
        
        with open(path,'r') as file:
            status,entries = get_entries(file.read())
        
        if not init_attrs:
            for entry in entries:
                if mode == 'followers':
                    G.add_edge(entry,name)
                else:
                    G.add_edge(name,entry)
    
        else:
            try:
                with open(get_trait_path(path)) as traits:
                    trait_data = json.loads(traits.read())
            except (FileNotFoundError):
                parent = get_parent(path)
                ig = igir.Instagiraffe_account(name,s,parent)
                with open(get_trait_path(path)) as traits:
                    trait_data = json.loads(traits.read())
            try:
                mom = get_parent(path)
            except:
                print(path)
            
            if not name in G.nodes:
                if status in ('$closed','$failed'):
                    ERROR = 0
                else:
                    ERROR = get_ratio(status)
                G.add_node(name,status='open',E=ERROR,
                parent=mom,**trait_data)
            
            for entry in entries:
                G.add_node(entry,pos='margin')
                if mode == 'followers':
                    
                    G.add_edge(entry,name,E = ERROR)
                
                else:
                    G.add_edge(name,entry,E=ERROR)
                    
    return G

def update_attrs(G):
    for node in G.nodes:
        print(node)
    
def draw_graph(G,path):
    
    A = nx.nx_agraph.to_agraph(G)
    A.write(path+'G.dot')
    A.draw(path+'G.png',prog='sfdp')
    
    

def write_traits1(library,auth=('tatyanaponidaeva','865256bhtd22')):
    s = login.login_deprecated(auth)
    
    parent = '/Users/basic/Documents/gardens/sloppy_boat'
    for p in library:
        name = get_name(p)
        trait_path = get_trait_path(p)
        try:
            f = open(trait_path,'r')
            continue
        except (FileNotFoundError):
            ig = igir.Instagirrafe_account(name,s,parent)
            if not ig.shared_data_response.status_code == 404:
                time.sleep(1)
        
def write_traits(root_ig):
    #master trait file
    path = os.path.join(root_ig.path,'%.txt')
    
    with open(path,'a+') as f:
        #ref is dict form of master trait file
        if f.read() != '':
            ref = json.loads(f.read())
        #if dne, make new dict
        else: ref = {}
        
        #db is the directory that contains library
        db = os.path.join(root_ig.path,root_ig.username)

        for r,d,f in os.walk(db):
            for file in f:
                if file[0] == '.': continue #.ds_store
                
                #initiate file not found, account not found values
                four_oh_four = False 
                data = {}
                
                name = get_name(file)
                #trait file
                new_path = os.path.join(r,'%'+file)
                
                if os.path.isfile(new_path) and name in ref:
                    
                    continue
                elif os.path.isfile(new_path):
                    ref[name] = open(new_path).read()
                    
                try: 
                    #if entry already exists, load it
                    data = ref[name]
                    
                except KeyError:
                    #else, create it from instagram endpoint
                    url = 'https://instagram.com/%s/?__a=1' % name
                    response = root_ig.session.get(url)
                    time.sleep(1.0)

                    if response.status_code != 200:
                        four_oh_four = True 
                    else:
                        dict = json.loads(response.text)
                        if dict == {}:
                            four_oh_four = True 

                    if not four_oh_four:
                        sub_dict = dict["graphql"]["user"]
                        data["is_private"] \
                        = bool(sub_dict["is_private"])
                        data["followed_by_viewer"] \
                        = bool(sub_dict["followed_by_viewer"])
                        data["n_followers"] = \
                        int(sub_dict["edge_followed_by"]["count"])
                        data["n_following"] \
                        = int(sub_dict["edge_follow"]["count"])
                        ref[name] = data
                        
                    else: data[name] = 0
                    
                if not os.path.isfile(new_path):
                    with open(new_path,'w+') as dict:
                        dict.write(json.dumps(data))
                        
        f.write(json.dumps(ref))

# with open(path) as f:
#     ref = json.loads(f.read())
#     for r,d,f in os.walk(root + '/trickbrowser'):
#         for user in ref.keys(): 
#             print(user)
#             for dir in d:
#                 print('\t'+dir)
#                 dir_path = os.path.join(r,dir)
#                 for file in os.listdir(dir_path):
#                     print('\t\t' + file)
#                     if user in file:
#                         dest = os.path.join(
#                         dir_path,'%' + user + '.txt'
#                         )
#                         user_ref = open(dest,'w+')
#                         open(dest,'w+').write(json.dumps(ref[user]))
#                     
                        
                    
        
        # for entry in entries:
            
                
            
        
        
        
        
        # name = get_name(path)
        # if 
        #     
        #     file = open(path)
        #     assert ('!' in file.read() or '$' in file.read())
        #     status,entries = get_entries(file.read())
        #     if '$' in status: continue
        #     for entry in entries:
            
        
            
            
            
            
        

