import requests
import selenium
import json
import sys
sys.path.append('/Users/basic/Documents/gardens/docs')
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from ig_functions import create_instagiraffe_edges as instagiraffe
class Instagiraffe_account(object):
    def __init__(self,username,browser,session):
        self.browser = browser
        self.session = session
        self.username = username
        self.url = 'https://www.instagram.com'
        self.acc_page = self.url + '/' + self.username
        self.shared_data_response = self.session.get(self.acc_page + '/?__a=1')
        if self.shared_data_response.status_code != 200:
            print('Your session\'s not logged in !')
        self.shared_data = json.loads(self.shared_data_response.text)
        self.traits = self.scrape_traits()
        self.traits['is_root'] = ( self.username == instagiraffe.get_root_user(self.browser) )
    
    def scrape_traits(self):
        traits = dict()
        sub_dict = self.shared_data['graphql']['user']
        traits['is_private'] = bool(sub_dict['is_private'])
        traits['followed_by_viewer'] = bool(sub_dict['followed_by_viewer'])
        traits['n_followers'] = int(sub_dict['edge_followed_by']['count'])
        traits['n_following'] = int(sub_dict['edge_follow']['count'])
        return traits
    
        
def login(auth,browser,session):
    #init session
    s = session
    username, key = auth
    
    #goto login page
    url = 'https://www.instagram.com/accounts/login/'
    url_main = url + 'ajax/'
    get_login = s.get(url)
    
    #login form content
    packet = {'username': username, 'password': key}
    
    #headers give session info (current session headers, taken from stack)
    headers = {
        'x-csrftoken': get_login.cookies['csrftoken'],
        'referer': "https://www.instagram.com/accounts/login/",
        'cookie': "fbm_124024574287414=base_domain=.instagram.com; ig_or=landscape-primary; ig_pr=1; ig_vw=1920; mid=Wcp3vAALAAGjSka8GEnPwijnia6-; rur=FTW; ig_vh=949; csrftoken="+get_login.cookies['csrftoken']+"; fbsr_124024574287414=jSVsTpoGuOgZQB0vEP_X70hrO2-LlfD9EnUz9nwGTXo.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUMyM1FOT2ZwQU1oRVVudldzeGp1dHpwckEyODBLbUZseVo4VjVMMVVRVkJYbUVadHFyd25nekdtdzg2ejFTajRIYzVSWVRISHlvTjZXU29ScEdDZXB5RnRTMDloRXlLT3dXbU5uTTloQV9PTFE2VUI2ZFhPWW5Qa3pBNlNSZkFpSWZiU2N2anEyRFZna2FMdkdDWkRBQklCbElhYVAya2JNZzJBQW9fU0lzS3Z5NDhHRXB2RjFwQmdKOHNrdjltZWtYbFF1Z1dib040UXlzM2lwUTVfRUsxTjJUaHBpb3g1QUF2SDNpSVE2Qm1fdTFSeTZTVHFZMWR1M2NCSU5FRHpiZXRaRjFvSXY1MGJzLWFWQk4tcmFsVHY1dGE2VS13ajZCUXE0UlFEQjVHZEdqeDZpZkdlc0JsYnZvQUNlVFFJQ3pVSl9id1F1eGpyc0UxbEFzalRWZCIsImlzc3VlZF9hdCI6MTUxODg4NDA1MCwidXNlcl9pZCI6IjEwMDAyMzcyMDI5NTQyNyJ9",
    }
    
    #post credentials to login page
    post_credentials = s.post(url_main,data=packet,headers=headers)
    browser.get(url)

    #transfer auth cookies to webdriver
    for cookie in s.cookies:
        browser.add_cookie({
            'name': cookie.name, 
            'value': cookie.value,
            'domain': cookie.domain
        })
    
    #goto acc page
    url = 'https://instagram.com/' + username
    browser.get(url)
    return browser

username,password = 'trickbrowser','arcticbanana'
auth = tuple([username,password])
driver_path = '/Users/basic/Documents/chromedriver'
browser = webdriver.Chrome(driver_path)
chrome_options = Options()
chrome_options.add_argument("--headless") 
session = requests.Session()
browser = login(auth,browser,session)

            

def get_followers(ig_account,SLEEP_TIME=0.5):
    #create followers txt at source dir
    #get data from Instagiraffe_account instance
    username = ig_account.username
    is_private = ig_account.traits['is_private']
    followed_by_viewer = ig_account.traits['followed_by_viewer']
    n_followers = ig_account.traits['n_followers']
    # file = open(sourcepath + username + '.txt/','w+')
    browser = ig_account.browser
    #go to user's acc page
    if browser.current_url != 'https://www.instagram.com/' + username:
        browser.get('https://instagram.com/' + username)
    if is_private and not followed_by_viewer:
        return False
    if n_followers == 0:
        return ''
    time.sleep(SLEEP_TIME)
    print(n_followers)
    link = '/' + username + '/followers/'
    followers = browser.find_element(By.XPATH,'//a[@href="%s"]' % link)
    followers.click()
    #wait to load
    time.sleep(SLEEP_TIME)
    
    t0 = time.time()

    followers = scroll_and_scrape(browser,n_followers)
    #create txt file containing followers
    t1 = time.time()
    print(t1-t0)
    return followers
        
    
def scroll_and_scrape(browser,n):
    #create BS file for scraping
    soup = BeautifulSoup(browser.page_source,features="lxml")
    #list containing tags that represent followers in list
    lines_initial = soup.find_all(has_notranslate_in_classname)
    #in case has_notranslate_in_classname fails
    # for line in lines_initial:
    #     if not 'notranslate' in str(line):
    #         lines_initial.remove(line)
    next = len(lines_initial) - 1
    followers = set()
    #loops until scrolling has completed
    while True:
        for line in lines_initial:
            #use set for redundancy
            followers.add(line.string)
        #scroll using javascript
        target = browser.find_elements(By.TAG_NAME,'li')[-1]        
        browser.execute_script("arguments[0].scrollIntoView();", target)
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source,'lxml')
        #redef lines list after scroll
        lines_initial = soup.find_all(has_notranslate_in_classname)
        next = len(lines_initial) - 1
        #n is number of followers from acc page
        if n > 1000:
            m = 1000
        else: m = n
        if len(followers) >= m:
            return followers


def has_access(browser):
    try:
        browser.find_element(By.XPATH,'//main/div/div[2]/article')
        return False
    except selenium.common.exceptions.NoSuchElementException:
        return True

def get_root_user(browser):
    home = browser.find_element(By.XPATH,\
    '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[3]/a')
    name = home.get_attribute('href')
    return name
#returns true for the tags that contain usernames in the follower list
def has_notranslate_in_classname(tag):
    return  tag.name == 'a' and tag.has_attr('title') and tag.has_attr('href') and tag.has_attr('class') 








