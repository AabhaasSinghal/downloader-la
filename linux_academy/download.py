# inspired by my answer to a question at https://github.com/rg3/youtube-dl/issues/12207
# script uses selenium together with youtube-dl and curl to download videos from Linuxacademy.com
# copy the script into a file and run it as python script.py username password URL
# the URL should be to the course homepage such as https://linuxacademy.com/cp/modules/view/id/140

from __future__ import unicode_literals
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import sys, time
import youtube_dl
import os


username = sys.argv[1]
pwd = sys.argv[2]
url = sys.argv[3] 
cookie_file = 'cookies.txt'

print("Welcome, I'm excited to have you here")

# remove cookie file if it exists
if os.path.exists( cookie_file ):
   os.remove( cookie_file )

# recreate file and open in append mode
f = open( cookie_file, 'a+')

# cookie function
def get_cookies():
  expiry = 0
  for i in driver.get_cookies():
    if not i.get('expiry'):
        expiry = 0
    else:
        expiry = i.get('expiry')
    cookie = '{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format( i['domain'], str( i['httpOnly'] ).upper(), i['path'], str( i['secure'] ).upper(), expiry, i['name'], i['value'] )
    f.write( cookie )

# chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")

# initiate browser 
driver = webdriver.Chrome( options=options )

# navigate to Linux Academy
driver.get("https://linuxacademy.com/")

# click login link
link = driver.find_element_by_partial_link_text('Log In')
link.click()

# get cookies from login.linuxacademy.com
print("Getting cookies from login.linuxacademy.com")
get_cookies()

# wait until login screen appears 
print("Sleeping for 5 seconds..")
time.sleep(5)

print("Attempting to login..")
user = driver.find_element_by_name('username')
user.send_keys( username )
password = driver.find_element_by_name('password')
password.send_keys( pwd )
password.send_keys(Keys.RETURN)

# check login
time.sleep(30)
try:
    lname = driver.find_element_by_id('navigationUsername')
    if lname:
      print("Login successful..")
except:
    print("Login failed..exiting")
    exit()

# get cookies from .linuxacademy.com
print('Getting cookies from .linuxacademy.com')
get_cookies()

# get lesson links 
print("Getting lesson links..")
driver.get( url )
time.sleep(5)
lessons = driver.find_elements_by_tag_name('a')
urls = []

for i in lessons:
    try:
       lesson  =  i.get_attribute('href')
       if '/course/' in lesson:
          urls.append( lesson )
    except:
      print('ignoring URL')

print( urls )

# close file handle
f.close()

# convert cookie using curl
print("Converting cookie using curl..")
cleaned_file = 'curlcookies.txt'
os.system('curl -b {} --cookie-jar {} {}'.format( cookie_file, cleaned_file, url  ) )

# call youtube-dl
print("Starting download..")
ydl_opts = { 'cookiefile': cleaned_file, 'force_generic_extractor': True , 'outtmpl':   '%(autonumber)s-%(title)s.%(ext)s', 'restrictfilenames': True , 'sleep_interval': 30 }

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download( urls  )

# quit
print("ALL DONE")
driver.quit()
