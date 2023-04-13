import requests #https://2.python-requests.org//en/master/
from selenium import webdriver

def login(auth,browser):
    #init session
    s = requests.Session()
    username, key = auth
    
    #goto login page
    url = 'https://www.instagram.com/accounts/login/'
    url_main = url + 'ajax/'
    get_login = s.get(url)
    #https://stackoverflow.com/questions/48835661/instagram-authentification-with-python-and-requests
    #idea of using a session to maintain data
    
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
    return browser,s

def login_deprecated(auth):
    #init session
    s = requests.Session()
    username, key = auth
    
    #goto login page
    url = 'https://www.instagram.com/accounts/login/'
    url_main = url + 'ajax/'
    get_login = s.get(url)
    #https://stackoverflow.com/questions/48835661/instagram-authentification-with-python-and-requests
    #idea of using a session to maintain data
    
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
    return s
