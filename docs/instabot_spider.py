import os
from instabot import Bot
import datetime
import instaloader
import requests
import time
import random
import logging
import shutil
import json
from func_timeout import func_set_timeout as timeout
from func_timeout import FunctionTimedOut
get_ts = lambda : datetime.datetime.fromtimestamp(time.time()).isoformat()   
FOLLOWERS = 'followers'
FOLLOWINGS = 'followings'
class InstabotTimeoutError(Exception):

    def __init__(self,username):
        self.username = username

class InstabotFeedbackError(Exception):
    
    pass

class ThrottleError(Exception):
    pass
        
creds_path = '/Users/basic/Documents/gardens/creds.txt'


def prompt_choice(*args):
    ui = '-1'
    while not ui in list(map(str,list(range(len(args))))):
        if ui != '-1':
            print('Bad input, prompting again')
        prompt = 'Choose '
        for i in range(len(args)):
            choice = args[i]
            prompt += '[{}] {}'.format(i,choice)
        ui = input(prompt)
    return ui
            
#             
# def get_args(args):
#     
#     try:
#         proxies = args['proxies']
#     except KeyError:
#         proxies = [None]
#         
#     creds = {}
#     is_creds = False
#     
#     try:
#         creds = args['creds']
#         if type(creds) != dict: 1/0
#         is_creds = True
#         
#     except ZeroDivisionError:
#         print('Credentials must be of dict type.')
#         while 1:
#             if input('Enter credentials manually? Y/N') in ['Y','Yes']: 
#                 break
#             elif input('Enter credentials manually? Y/N') in ['N','No']:
#                 print('Run again with correct input type.')
#                 return None
#                 
#     while not is_creds:
#         print('You need Instagram credentials to use Instagiraffe.')
#         user = input('username:')
#         creds[user] = input('key:')
#         if not (input('Enter more credentials? Y/N') in ['Y','Yes']) \
#         and type(user) == str and type(creds[user]) == str: 
#             is_creds = True
#             
#     return proxies, creds
#     
# def run(parent=None,deg=2,**kwargs):
#     try:
#         proxies,creds = get_args(kwargs)
#     except TypeError:
#         return
#     
#     if None in proxies or len(creds) == 1:
#         run_dolo(dir,deg)
#         
#     if parent == None:
#         parent = os.path.join(os.getcwd(),'Instagiraffe')
#     if not os.path.isdir(parent):
#         os.mkdir(parent)
#         # shutil.copy('/Users/basic/Documents/chromedriver',os.path.join(parent,'chromedriver'))
#     
#     spider = Instabot_spider(creds, proxies, parent)

# #run_lite('/Users/basic/venv/',
# def run_lite(dir=None,deg=2,**kwargs):
#     spider = Instabot_spider(creds, None, dir)
#     
class Instabot_spider(object):
    #class that manages instagram scrape using instabot
    def __init__(self, creds_path, proxies, parent, name = 'Instaspider', limit = 1000):
        #creds : list of tuples with username, password
        creds = self.get_creds(creds_path)
        temp_creds = []
        for user in creds:
            temp_creds.append({'username':user,'password':creds[user]})
        self.creds = tuple(temp_creds)
        self.cindex = self.pindex = -1
        #proxy for scraping
        self.proxies = proxies
        #name displayed in error logs
        self.name = name
        #limit for branch count
        self.limit = limit
        self.curr_depth = 0
        #instaloader for metadata
        self.loader = instaloader.Instaloader()
                
        # self.verify_creds(self.creds)
        #bots is a list of instabot instances
        self.bot = None
        #inits bots
        self.cycle_login()
        self.library = set()
        '''
        main_dir _
                  \_json_dir: contains profile jsons
                  |
                  |_data_dir: contains unstructured followers / followings .txt's
                  |
                  |_debug: contains debug logs
        '''
        self.main_dir = os.path.join(parent,self.name)
        self.json_dir = os.path.join(self.main_dir, 'JSONs')
        self.data_dir = os.path.join(self.main_dir,'data')
        
        
        
        self.debug = os.path.join(self.main_dir,'debug')
        self.master_debug = os.path.join(self.debug,'master.log')
        
        #logging handler
        logging.basicConfig(filename=self.master_debug, level=logging.DEBUG)
        
        #logs is a dictionary with callables that output messages
        self.logs = {}
        self.init_logs()
        self.log('init')
        
        #make dirs 
        self.dirs = [self.main_dir,self.debug,self.json_dir,self.data_dir]
        for dir in self.dirs:
            if not os.path.isdir(dir):
                os.mkdir(dir)
                self.log('directory','make',input=dir)
        
        #avoid redundancy
        self.scraped = {}
        self.scraped_raw = os.listdir(self.data_dir)
    
    def get_creds(self,creds_path):
        self.creds_path = creds_path
        creds = {}
        with open(creds_path,'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                if line == '' or line[0] == '*':
                    continue
                if ':' in line:
                    vals = line.split(':')
                    creds[vals[0]] = vals[1]
        return creds
                       
    def update_library(self):
        self.scrape_dirs = []
        for item in os.listdir(self.main_dir):
            if os.path.isdir(os.path.join(self.main_dir,item)) and 'scrape' in item:
                self.scrape_dirs.append(item)
        for scrape_dir in self.scrape_dirs:
            for r,d,f in os.walk(os.path.join(self.main_dir,scrape_dir)):
                for file in f:
                    if file[0] == '.': continue
                    path = os.path.join(r,file)
                    self.library.add(path)
     
    def cycle_login2(self):
        if self.bot:
            self.bot.logout()
            if self.bot.api.is_logged_in:
                del self.bot
                self.bot = None
        while not (self.bot and self.bot.api.is_logged_in):
            self.cindex += 1
            self.cindex %= len(self.creds)
            self.curr_creds = self.creds[self.cindex]
            if self.proxies != None:
                self.pindex += 1
                self.pindex %= len(self.proxies)
                self.curr_proxy = self.proxies[self.pindex]
            else:
                self.curr_proxy = None
            if not self.bot: self.bot = Bot()
            
            self.bot.login(username=self.curr_creds['username'],
                           password=self.curr_creds['password'],
                           proxy=self.curr_proxy)
            
            if not self.bot.api.is_logged_in:
                # try:
                response = self.bot.api.last_response
                to_deprecate = self.bot.api.username 
                if response != None and response.status_code == '400':
                    self.deprecate_creds(to_deprecate)
        
    def cycle_login(self):
        self.cindex += 1
        self.cindex %= len(self.creds)
        self.curr_creds = self.creds[self.cindex]
        if self.proxies != None:
            self.pindex += 1
            self.pindex %= len(self.proxies)
            self.curr_proxy = self.proxies[self.pindex]
        else:
            self.curr_proxy = None
        if self.bot is None: self.bot = Bot()
        
        self.bot.login(username=self.curr_creds['username'],
                        password=self.curr_creds['password'],
                        proxy=self.curr_proxy)
        
        if not self.bot.api.is_logged_in:
            # try:
            response = self.bot.api.last_response
            to_deprecate = self.bot.api.username 
            if response != None and response.status_code == '400':
                self.deprecate_creds(to_deprecate)
    
                            
    
    
    def __del__(self):
        if self.bot:
            self.bot.logout()
        self.update_library()
        for dir in self.scrape_dirs:
            temp_file = os.path.join(dir,'temp.txt')
            if os.path.isfile(temp_file):
                os.remove(temp_file)
        
    def deprecate_creds(self,to_deprecate):
        with open(self.creds_path) as f:
            creds_raw = f.read()
        entries = [l for l in creds_raw.split('\n') if l != '' and l[0] != '*']
        index = [items[0] for items in [
        entry.split(':') for entry in entries
        ]].index(to_deprecate)
        entries[index] = '*' + entries[index]
        new_creds = '\n'.join(entries)
        with open(self.creds_path,'w') as f:
            f.write(new_creds)    
    
    def init_logs(self):
        if not os.path.isfile(self.master_debug):
            open(self.master_debug,'w+').close()
        
        lf = lambda : '\t' * self.curr_depth + '{} {}:'.format(get_ts(),self.name)
        
        self.logs['init'] = lambda : '{} OPEN {}'.format(get_ts(),self.name)    
        
        for main in ['directory','scrape','write']:
            self.logs[main] = {}
        
    
        self.logs['directory']['make'] = lambda path \
        : '{} making directory ({})'.format(lf(), path)
        
        for level in ['root','branch']:
            self.logs['scrape'][level] = {}
            for which in [FOLLOWERS,FOLLOWINGS]:
                self.logs['scrape'][level][which] = \
                lambda id : '{}scraping from {} {} ({})'.format(
                lf(), level, id, which
                )
        self.logs['scrape']['acc'] = lambda id,mode \
        : '{} scraping {} of {}'.format(lf(),id,mode)
        for ftype in ['json','txt']:
            self.logs['write'][ftype] = lambda path \
            : '{} writing {} {}'.format(lf(), ftype,path)
        
        self.logs['delete'] = lambda path : '{} deleting {}'.format(lf(),path)
        self.logs['use_data'] = lambda \
        : '{} using previous data'.format(lf())
        self.logs['cycle'] = lambda user:'{} cycling from {}'.format(lf(), user)
        self.logs['skip'] = lambda user:'{} skipping {}'.format(lf(),user)
        
    def log(self,*args,**kwargs):
    
        call = self.logs
        for arg in args:
            call = call[arg]
        if len(kwargs) == 0:
            message = call()
        else:
            call_args = []
            for kwarg in kwargs:
                call_args.append(kwargs[kwarg])
            message = call(*call_args)
        if 'init' in args or self.working:
            print(message)
        logging.info(message)
    
    
        
    def update(self):
        self.scraped[FOLLOWINGS] = self.scraped[FOLLOWERS] = set()
        
        #for if incomplete scrape has begun
        #goes through all files in data_dir
        for file in self.scraped_raw:
            #absolute path
            try:
                #file := {id}_{mode}.txt => returns mode
                file_mode = file.split('.')[0].split('_')[1]
                #scraped is a dict, divided by scrape mode 
                self.scraped[file_mode].add(file)
            except IndexError:
                print('Invalid path {} found'.format(file))
                os.remove(os.path.join(self.data_dir,file))    
    
    def init_root(self,root_id,mode,dir):
        level = 'root'
        self.working = False

        self.log('scrape',level,mode,input=root_id) 
        print(self.logs['scrape'][level][mode](root_id))
        newdirname = 'scrape{}_{}'.format(root_id,mode)
        self.scrape_dir = os.path.join(dir, newdirname)
        if not os.path.isdir(self.scrape_dir):
            os.mkdir(self.scrape_dir)
            self.log('directory','make',input=self.scrape_dir)

        self.update()
            
        
    def scrape(self, root_id, deg=2, mode='',dir=''):
        '''generate a follower tree of deg degrees of separation with id as root
        let mode = flwr
        main-dir_                                                       ....
                 \_{id}-{mode}_                 __{flwr(flwr(root))}__/
                               \_{flwr(root)}__/                      \ ....    
                               |               \__{flwr(flwr(root))}__
                               |
                               |
                               |_{flwr/flwng}
                               
                               #continues until ...__{flwr**deg(root)}
        '''
        #init recursion vals
        
        self.curr_depth = 0; self.max = deg
        if dir == '':
            dir = self.main_dir
        #inits scrape_dir, already scraped files
        self.init_root(root_id,mode,dir)
        
        
        #init root ig
        root_ig = Account(self,root_id)
        #store root edges in original dir (default to project dir)
        
        while 1:
            try:
                self.scrape_acc(root_ig, mode, dir)
                break
    
            except (InstabotTimeoutError,FunctionTimedOut) as e:
                self.cycle_login()
                self.log('cycle',input=e.username)
            except InstabotFeedbackError as e:
                self.log('skip',input=acc_id)
                
        children = root_ig.edges[mode]

        self._cycle(*children, mode=mode)
        
    
    def _cycle(self,*children,**kwargs):
        for child_id in children:
            prev = self.bot.api.username
            while not self.scrape_branch(child_id, **kwargs):                
                self.cycle_login()
                if self.bot.api.username == prev:
                    raise ThrottleError
                time.sleep(2 * random.random())
                
    def scrape_branch(self, acc_id, mode = FOLLOWERS, dir = ''):
        if dir == '':
            dir = self.scrape_dir
        
        self.curr_depth = len(dir.split('/')) - len(self.main_dir.split('/'))
        level = 'branch'
        self.log('scrape', level, mode, input=acc_id)
        
        ig = Account(self, acc_id)
        
        try: 
            self.scrape_acc(ig, mode, dir)
            
        except FunctionTimedOut as e:
            self.pass_meta(ig,mode,deprecated=True)
            self.log('cycle',input=self.bot.api.username)
            self.cycle_login()
            return True
        
        except InstabotTimeoutError as e:
            self.log('cycle',input=self.bot.api.username)
            return False
            
        except InstabotFeedbackError as e:
            self.log('skip',input=acc_id)
            return True
            
        else:
            if self.curr_depth < self.max:
                ig.dirname = '{}_{}'.format(ig.id, mode)
                new_dir = os.path.join(dir, ig.dirname)
                children = ig.edges[mode]
            
                if not os.path.isdir(new_dir):
                    os.mkdir(new_dir)
                    self.log('directory','make',input=new_dir)
                
                self._cycle(*children,mode=mode,dir=new_dir)
                        
            return True
    
    @timeout(5)
    def scrape_acc(self, ig, mode, dir):
        #account class stores flwrs/flwngs of given account,
        #also account.dir for files
        #to file stores mode also
        
        self.log('scrape','acc',id=ig.id,which=mode)
        ig.filename = '{}_{}.txt'.format(ig.id,mode)
        ig.to_file = os.path.join(dir, ig.filename)
        #if already scraped
        try:
            scraped = self.scraped[mode]
        except KeyError:
            scraped = set()
    
        if ig.filename in scraped:
            path = os.path.join(self.data_dir, ig.filename)
            with open(path) as f:
                #get children, add to edges dict
                ig.edges[mode] = [flwr for flwr in f.read().split('\n') \
                                if flwr != '' and flwr[0] != '$']
            #add to dir
            shutil.copy(path, ig.to_file)     
        else:
            #write children to file (temp file)
            if not self.working:
                self.working = True
            status = self.bot.api.get_total_followers_or_followings(
            ig.id, amount=self.limit, which=mode, 
            to_file=ig.temp, overwrite=True
            )
            time.sleep(2 * random.random())
            
            if status == False:
                raise InstabotFeedbackError 
            if not os.path.isfile(ig.temp):
                raise InstabotTimeoutError(self.bot.api.username)
            
            self.pass_meta(ig,mode)
            
    def pass_meta(self,ig,mode,deprecated=False):
            meta = {}
            #private or public
            ig.status = ig.get_status()
            #followers or followings
            meta['mode'] = mode
            #limit on scrape
            meta['limit'] = self.limit
            meta['status'] = ig.status
            if not deprecated:
                meta['username'] = self.bot.get_username_from_user_id(ig.id)
            #write to actual file location, with metadata
            ig.update(meta)
            try:
                if ig.is_file:
                    shutil.copy(ig.to_file,os.path.join(self.data_dir,ig.filename))
                    self.scraped[mode].add(ig.filename)
            except FileNotFoundError:
                pass    
    
class Account(object):
    
    
    def __init__(self, spider, acc_id, structure=None):
        
        self.spider = spider
        self.id = acc_id
        self.temp = os.path.join(spider.scrape_dir,'temp.txt')
    
        #     
        # if structure is None:
        #     self.profile = instaloader.Profile.from_id(spider.loader.context, self.id)
        # else:
        #     self.profile = structure
            
        self.edges = {}
        self.edges[FOLLOWERS] = self.edges[FOLLOWINGS] = set()
        
        
    def write_json(self):

        json = os.path.join(self.spider.json_dir,str(self.id)+'.json')
        print('writing ' + json)
        instaloader.save_structure_to_file(self.profile, json)
        
        message = self.spider.logs['write']['json'](json)
        print(message); logging.info(message)
        
    def update(self,meta):
        try:
            key = meta['mode']

            with open(self.temp,'r') as data:
                self.edges[key] = [flwr for flwr in data.read().split('\n') \
                                    if flwr != '']
                
            os.remove(self.temp)
                
            with open(self.to_file,'a') as f:
                f.write('${}\n'.format(json.dumps(meta)))
                f.write('\n'.join(self.edges[key]))  
                self.is_file = True
        except FileNotFoundError:
            self.is_file = False
            print('can\'t update, no data')
            return 
        except KeyError:
            print('can\'t update, no meta')
            return

    def get_status(self):
        #meant to be called when ig.temp exists
        try:
            #if temp file has nothing, no followers scraped => private acc
            with open(self.temp) as f:
                if f.read() == '':
                    return 'closed'
                else:
                    return 'open'
        except:
            print('TEMP DNE')

    # def verify_creds(creds):
    #     all_good = True
    #     bad_creds = []
    #     for user in creds:
    #         key = creds[user]
    #         if not self.bot.login(username=user,password=key):
    #             print('Authentication failed for ' + user + ',' + key)
    #             
    #             while True:
    #                 ui = input('Try different password: 0\nRemove account: 1')
    #                 if ui in ['0','1']: 
    #                     break
    #                 print('Bad input')
    #             if ui == 0:
    #                 while True:
    #                     temp_key = input('Enter new password')
    #                     status = self.bot.login(username=user,password=key)
    #                     if status == True:
    #                         break
    #                     print('Failed')
    #                     
    #         else:
    #             self.bot.logout()
    #     self.bot.logout()
        #         
        # if all_good: return
        # for i in range(len(bad_creds)):
        #     badseed = bad_creds[i]
        #     print('Authentication failed for %s (%d/%d)' \
        #     % (str(badseed),i,len(bad_creds))
        #     while True:
        #         ui = input('Try different password: 0\nRemove account: 1')
        #         if ui in ['0','1']: 
        #             break
        #         print('Bad input')
        #     if ui == 0:
        #         while True:
        #             user = badseed[0]
        #             key = input('Enter new password')
        #             status = self.bot.login
        
        # json = os.path.join(self.json_dir,str(id)+'.json')
        # try:
        #     profile = instaloader.load_structure_from_file(self.loader.context,json)
        #     ig = Account(self,id,profile)
        # except FileNotFoundError:
        #     ig = Account(self, id)
        #     # ig.write_json()
        #     



if __name__ == '__main__':
    creds_path = '/Users/basic/Documents/gardens/creds.txt'
    spider = Instabot_spider(creds_path,None,'/Users/basic/venv')     
    Pr = instaloader.Profile.from_username(spider.loader.context, 'sloppy_coop')
    spider.scrape(Pr.userid, deg=1, mode='followers')
    
    # 