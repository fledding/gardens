import time
from selenium import webdriver
# https://seleniumhq.github.io/selenium/docs/api/py/index.html
# selenium docs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import selenium.common.exceptions as ceptions
#https://devhints.io/xpath (main resource for xpath)
elems_to_flwrs = lambda elem_list : {elem.text \
                                        for elem in elem_list}

# def get_following(ig_acc,browser):
#     username = ig_acc.username 
#     is_private = ig_acc.traits['is_private']
#     followed_by_viewer = ig_acc.traits['followed_by_viewer']
#     n_following = ig_acc.traits['n_followers']
#     
#     if is_private and not followed_by_viewer:
#         return False
#     elif n_following == 0:
#         return set()
#     
#     if browser.current_url != 'https://www.instagram.com/' + username:
#         browser.get('https://instagram.com/' + username)
# 
#     link = '/' + username + '/following/'
#     
#     following = WebDriverWait(browser,10).until(
#     EC.presence_of_element_located(
#     (By.XPATH,'//a[@href=%s]' % link)
#     )
#     )
#     following.click()
#     
#     followings,ERRORertainty = scroll_and_scrape(browser,n_following)
#     
#     return (followings,ERRORertainty)

def get_followers(ig_acc,trys=0,l_trys=0):
    #get acc attrs from Instagiraffe object
    if trys > 3:
        print('timed out on acc page')
        return (None,0)
    if l_trys > 1:
        # try:
        #     browser.find_element(By.XPATH,
        #     '//div[text()="You\'ll see all the people who follow you here."]')
        #     return False
        # except ceptions.NoSuchElementException:
        #     pass
        print('timed out on follower list')
        
        return (None,0)
    else:
        print('try #%d (followerlist)' % max(trys,l_trys))
        
    #You'll see all the people who follow you here.
    if ig_acc.traits == {}:
        return (False,0)
        
    username = ig_acc.username 
    
    is_private = ig_acc.traits['is_private']
    followed_by_viewer = ig_acc.traits['followed_by_viewer']
    n_followers = ig_acc.traits['n_followers']
    browser = ig_acc.browser
    

    print(username,n_followers)

    #cannot scrape, return false
    
    if is_private and not followed_by_viewer:
        return (False,0)
    
    #no data to scrape, return empty set
    elif n_followers == 0:
        return (set(),0)
        
    #go to user's acc page
    browser.get(ig_acc.acc_page)
    #find follower list button
    link = '/' + username + '/followers/'
    
    try:
        followers = WebDriverWait(browser,10,0.25).until(
        EC.presence_of_element_located(
        (By.XPATH,'//a[@href="%s"]' % link)
        )
        )
    except:
    
        print('try #%d (acc page)' % l_trys)
        return get_followers(ig_acc,trys+1,l_trys)            
        
    # followers = WebDriverWait(browser,10).until(
    # EC.presence_of_element_located(
    # (By.XPATH, '//a[@href="%s"]' % link)
    # )
    # )
    followers.click()
    
    # if ig_acc.traits['is_root']:
    #     return slow_scrape(browser,n_followers)
    #     
    #wait until first follower elements can be retrieved
    followers,ERROR = scroll_and_scrape(browser, n_followers)
    
    if followers is False:
        return get_followers(ig_acc,trys,l_trys+1) 
        
    return (followers,ERROR)


def scroll_and_scrape(browser,n,l_trys=0,
                      s_trys=0,seen=set(),W=-1,timer=time.time()): 

    if s_trys >= 5:
        print('timed out on scrape')
        if seen != set():
            return (seen,len(seen)/n) 
        else:
            return (False,1)
    
    print('try %d' % s_trys)
    
    #for explicit waits
    CHRONO_LIMIT = 4
    
    # element locators
    t = 'a'
    flwr_loc = '[contains(@class, "notranslate")]'
    root = '/html/body/div/div/div/ul/div/li'
    
    if l_trys == 0 and s_trys == 0:
        seen = set()
        
    if seen != set():
        count = len(seen)
        skip = '[position()>%d]' % count
        flowers = seen
    else:
        count = 0
        skip = ''
        flowers = set()

    target = None
    t1 = t0 = time.time()
    while t1 - t0 < CHRONO_LIMIT:
        time.sleep(0.25)
        lines = browser.find_elements(By.XPATH,root)
        if lines != []: print('\twindow loaded'); break
        t1 = time.time()
    if lines == []:
        return (False,1)
    
    time.sleep(0.25)
    while True:
        if count >= 300: break
        
        try:
            elem = browser.find_element(By.XPATH,
            root + skip + '//' + t + flwr_loc)
            flowers.add(elem.text) 
            count += 1
            skip = '[position()>%d]' % count
        except (ceptions.StaleElementReferenceException):
            print(0)
            return scroll_and_scrape(browser,n,
                                    l_trys,s_trys+1,
                                    flowers,W)
        
        except (ceptions.NoSuchElementException):
            
            # try:
            #     loading = browser.find_element(By.XPATH,
            #     '//li/div[count(*)=0]')
            #     return (None, flowers), 1 - (count / n )
            # except ceptions.NoSuchElementException:
            #     pass
            
            if target == None and W == -1:
                W = count // 2
                
            if count + W >= n or count > 800:
                break
    
            t1 = t0 = time.time(); lines = []            
            while t1 - t0 < CHRONO_LIMIT \
            and len(lines) < count: 
                lines = browser.find_elements(By.XPATH, 
                root + '//' + t + flwr_loc)
                time.sleep(0.1)
                t1 = time.time()
            
                
            if len(lines) > count or \
            (len(lines) >= count and count != 0): 
                target = lines[-1]
                try:
                    browser.execute_script(
                    "arguments[0].scrollIntoView();", target
                    )
                except ceptions.StaleElementReferenceException:
                    print(1)
                    scroll_and_scrape(browser,n,
                                    l_trys,s_trys+1,
                                    flowers,W,time.time())
            else:
                print(2)
                return scroll_and_scrape(browser,n,
                                        l_trys,s_trys+1,
                                        flowers,W,time.time())

            t1 = t0 = time.time()
            while t1 - t0 < CHRONO_LIMIT:
                time.sleep(0.25)
                loaded_new = len(
                browser.find_elements(By.XPATH,root) 
                )
                if loaded_new > count: break
                t1 = time.time()
            
            # if (count == 0 and loaded_new > count):
            #     continue
            # elif (count > 0 and loaded_new > count + 1):
            #     continue
            # else:
            #     print(3)
            #     return scroll_and_scrape(browser,n,
            #                             l_trys,s_trys+1,
            #                             flowers,W)
        except (KeyboardInterrupt):
            browser.close()
            return flowers, 1 - len(flowers) / n 
        
    
    ERROR = 1 - len(flowers) / n
    return flowers, ERROR


def get_root_user(browser):
    home = browser.find_element(By.XPATH,
    '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[4]/a')
    link = home.get_attribute('href')
    name = link[:-1].split('/')[-1]
    return name
