import os
import json
import sys
import time
import shutil
from copy import copy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
parent = '/Users/basic/Documents/gardens'
sys.path.append(parent + '/docs')
from ig_functions import create_instagiraffe_edges as ig
from ig_functions import instagiraffe_login as login
from ig_functions import ig_nx
from ig_functions.path_functions import define_path_functions

from instabot import Bot
# username = input("Enter your username")
# password = input("Enter your password")

driver_path = '/Users/basic/Desktop/chromedriver'
get_name,get_entries,get_ratio,get_parent,get_trait_path,get_p_from_trait_p = \
define_path_functions()

#instagiraffe object stores metadata about account 
#in addition to the browser session from which the account is #scraped
class Instagiraffe_account(object):
    def __init__(self,username,session,path,browser=None,bot=None):
        if browser == None:
            self.use_browser = False
        else:
            self.use_browser = True
            self.browser = browser
        self.session = session
        
        self.username = username
        
        #path is the parent directory
        self.path = path
        if self.path[-1] == '/':
            self.parent = self.path + self.username
        else:
            self.parent = self.path + '/' + self.username
        self.parent = os.path.join(self.path,self.username)
        self.data = self.parent + '.txt'
        self.edges = {} 
        self.library = [self.data]
        
        print(self.parent)
        
        self.url = 'https://www.instagram.com'
        self.acc_page = self.url + '/' + self.username
        self.shared_data_response = self.session.get(self.acc_page\
         + '/?__a=1')
        #https://stackoverflow.com/questions/49788905/what-is-the-new- instagram-json-endpoint
        while self.shared_data_response.status_code == 403:
            print('Your session\'s not logged in !')
            if self.use_browser:
                for cookie in self.session.cookies:
                    browser.add_cookie({
                        'name': cookie.name, 
                        'value': cookie.value,
                        'domain': cookie.domain
                    })
            self = Instagiraffe_account(self.username,
            self.session,self.path,browser = self.browser)

        if self.shared_data_response.status_code == 404:
            self.children = False
            self.traits = {}
        
        else:                
            self.trait_path = self.path + '/%' + self.username + '.txt'
            try:
                with open(self.trait_path,'r') as f:
                    self.traits = json.loads(f.read())
            except (FileNotFoundError):
                self.shared_data = json.loads(
                self.shared_data_response.text
                )
                self.scrape_traits()
                self.children = set()

        # if self.traits != {} and self.use_browser:
        #     self.is_root = self.traits["is_root"] \
        #     = ( self.username == ig.get_root_user(self.browser) )
    
   #      
    def scrape_traits(self):
        self.traits = dict()
        #gets traits from account json endpoint
        try:
            self.sub_dict = self.shared_data["graphql"]["user"]
        
            self.is_private = self.traits["is_private"] \
            = bool(self.sub_dict["is_private"])
            self.followed_by_viewer = self.traits["followed_by_viewer"] \
            = bool(self.sub_dict["followed_by_viewer"])
            self.n_followers = self.traits["n_followers"] = \
            int(self.sub_dict["edge_followed_by"]["count"])
            self.n_following = self.traits["n_following"] \
            = int(self.sub_dict["edge_follow"]["count"])
            
        
                
        except (KeyError,AttributeError):
            print(self.shared_data_response.text[:2000])
            self.traits = {}
        try:
            f = open(self.trait_path,'r')
            f.close()
        except (FileNotFoundError):
            with open(self.trait_path,'w+') as f:
                f.write(json.dumps(self.traits))
        
    def scrape_as_root(self,deg):
        #generate a follower tree of deg degrees of separation
        print('Scraping from root ' + self.username + '!')
        #library represents already written follower txts
        self.article = self.path + '/%' + '.txt'
        if not os.path.isfile(self.article):
            open(self.article,'w+').close()
            self.reference = dict()
        else:
            with open(self.article) as article:
                self.reference = json.loads(article.read())
        self.update_library()
        self.edges[self.username] = self.scrape_branches(deg)
        return self.edges
        
    def scrape_branches(self, deg, user=None):  
    
        #for initial call on root user
        if user == None: 
        #get file if written
            if os.path.isfile(self.data):
                f = open(self.data,'r')
                s = f.read()
                if s == '$closed':
                    print('Follow yourself!')
                    self.children = False
                    ERROR = 1
                elif s == '$failed':
                    self.children,ERROR = ig.get_followers(self)
                    
                else:
                    self.children = {child for child in \
                    s.split('\n')[1:] if (child != '')}
        #if not written
            else:
                (self.children,ERROR) = ig.get_followers(self)
                self.write_children(self)
            user = self
            
        else:
            print('Degree = ' + str(deg))
            print('Scraping from branch ' + user.username)
            txt_exists = False
            for file in self.library:
                if user.username + '.txt' in file:
                    print('using data from library (%s)' % file)
                    txt_exists = True
                    if file != user.data:
                        
                        shutil.copy(file,user.data)
                        self.library.append(user.data)
                    with open(file,'r') as book:
                        s = book.read()
                        if s == '$closed':
                            user.children = False
                            ERROR = 0
                        elif s == '$failed':
                            user.children = ig.get_followers(user)
                            user.write_children(self)
                            if open(user.data).read() != s:
                                shutil.copy(user.data,file)
                        else:
                            user.status,user.children = get_entries(s)
                            print(user.traits)
                            if user.traits['n_followers'] != 0:
                                ERROR = 1 \
                                - len(user.children)/user.traits['n_followers']
                            else:
                                ERROR = 0
                    break
            if not txt_exists:
                (user.children,ERROR) = ig.get_followers(user)
                user.write_children(self)
        
        if user.children in [None,False] or deg == 0:
            return (ERROR,user.children)
        
        branches = dict()
        local_children = copy(user.children)
        if not os.path.isdir(user.parent): os.mkdir(user.parent)
        
        for child in local_children:
            child_ig = Instagiraffe_account(
            child, self.session, user.parent, browser = self.browser
            )
            if not child in self.reference:
                self.reference[child] = child_ig.traits
            with open(self.article,'w') as article:
                article.write(json.dumps(self.reference))
            branches[child] = self.scrape_branches(deg-1, child_ig)
            time.sleep(0.5)
        user.children = local_children

        return branches
    
    def write_children(self,root):
        print('writing to ' + self.data)
        root.library.append(self.data)
        with open(self.data, 'w+') as f: 
            if not self.children in [None,False]:
                f.write('!%d/%d\n' \
                % (len(self.children),self.traits['n_followers']))
                
                for child in self.children:
                    f.write(child + '\n')
            elif self.children == False:
                f.write('$closed')
            else:
                f.write('$failed')
            f.close()
    
    def update_library(self,include_traits = False):
        for r, d, f in os.walk(self.parent):
            for file in f:
                p = os.path.join(r, file)
                
                if include_traits:
                    ignore = ['.']
                else:
                    ignore = ['.','%']
                if file[0] in ignore:
                    continue
                    
                with open(p) as txt:
                    status = ig_nx.get_entries(txt.read())[0]
                    if status == '$failed':
                        os.remove(p)
                    else:
                        self.library.append(p)
                    txt.close()
                    
    
    def reset_timer(self):
        self.timer = time.time()
                
    def repair_library(self):
        self.update_library(include_traits=True)
        for r,d,f in os.walk(self.parent):
            for file in f:
                if file[0] != '%':
                    continue
                
                path = get_p_from_trait_p(file)
                
                try:
                    data = open(path,'r')
                    data.close()
                except (FileNotFoundError):
                    print(path)
                    data = open(path,'w+')
                    data.write('$failed')
                    data.close()
                
                
                
def run_dolo(parent=None,deg=2,auth=()):
    
    #Allow user to login
    if parent == None:
        parent = os.path.join(os.getcwd(),'Instagiraffe')
    if not os.path.isdir(parent):
        os.mkdir(parent)
    
    browser = webdriver.Chrome(os.path.join(parent,'chromedriver'))
    status = -1
    while status != 200:
        print('not logged in')
        
        username=input('Instagiraffe: Enter Instagram username ')
        if username == '': 
            username,password = auth
            g = True
        else: 
            password=input('Instagiraffe: Enter Instagram key ')
        auth = (username,password)  

        browser,session = login.login(auth,browser)
        check_creds = session.get('https://instagram.com/%s/?__a=1'%username)
        status = check_creds.status_code
        if g: username = 'sloppy_boat'
    root_ig = Instagiraffe_account(
    username,session,parent,browser = browser
    )
    root_ig.scrape_as_root(deg)
    root_ig.update_library()
    browser.close()
    path = input('Enter your desired storage location for graph as a path.')
    G = ig_nx.create_graph(root_ig.library)


    
        
        
            
        
    
        
#download driver file
# source_url = \
# 'https://chromedriver.storage.googleapis.com/75.0.3770.90/chromedriver_mac64.zip'
# sink_path = os.path.join(dir,'chromedriver')
# r = requests.get(source_url, stream=True)
# if r.status_code == 200:
#     with open(sink_path, 'wb') as f:
#         for chunk in r:
#             f.write(chunk)

    
# initialize credentials
# username,password = 'sloppy_boys','Total_equ1librium'
# auth = tuple([username,password])
# 
# auth = (username,password)
# path = '/Users/basic/Documents/chromedriver'
# chrome_options = Options()
# chrome_options.add_argument("--headless")  
# browser = webdriver.Chrome(dir + '/chromedriver',options=chrome_options)
# 
# browser = webdriver.Chrome(dir + '/chromedriver')
# browser,session = login.login(auth,browser)

# sourcepath ='/Users/basic/Documents/gardens'
# root_ig  = Instagiraffe_account(username,browser,session,sourcepath)

# def make_ig(name,context=root_ig):
#     return Instagiraffe_account(name,root_ig.browser,
#     root_ig.session,root_ig.dir)
# edges = root_ig.scrape_as_root
# # 
# path = input('Enter your desired data storage location as a path.')
# with open(path,'w+') as f:
#     f.write(str(edges))
#test function for sequential scraping
# def scrape_list(lst):
#     tlist=[]
#     for i in range(len(lst)):
#         follower = lst[i]
#         if follower != '' and not exist_condition(follower,sourcepath):
#             print('writing:'+follower)
#             t0 = time.time()
#             current = Instagiraffe_account(follower,browser,session)
#             followers = ig.get_followers(current)
#             flwrs_txt = open(sourcepath + follower + '.txt','w+')
#             print(sourcepath + follower + '.txt')
#             if followers == False:
#                 flwrs_txt.write('$closed')
#             else:
#                 for name in followers:
#                     flwrs_txt.write(name + '\n')
#             t1 = time.time()
#             tlist.append( (t1-t0) / int(current.traits['n_followers']) )
#             print('time spent: ' + str(t1 - t0))
#             print('time spent by flwrs: ' + str(tlist[-1] ) )
#             print('current avg time: ' + str( ( t1 - t0) / i ))
#             print('current avg time by flwr: ' + str(sum(tlist)/i) )
#             print('finished:'+follower)
#             flwrs_txt.close()


            
            


            
        
    

