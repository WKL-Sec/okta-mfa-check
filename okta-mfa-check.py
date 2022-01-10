from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time, os, sys, re, argparse, datetime
from datetime import datetime
from itertools import zip_longest

# Create log file
now = datetime.now()
log_string = now.strftime("%Y-%m-%d-%H-%M-%S")
outfile = "okta_mfa_check_" + log_string + ".log"

parser = argparse.ArgumentParser()
usergroup = parser.add_mutually_exclusive_group()
passgroup = parser.add_mutually_exclusive_group()

usergroup.add_argument("-U", "--usernamefile", type=str, help="Text file containing list of usernames")
passgroup.add_argument("-P", "--passwordfile", type=str, help="Text file containing list of passwords to match each line of usernames in file")
usergroup.add_argument("-u", "--username", type=str, help="Username to test for MFA")
passgroup.add_argument("-p", "--password",  type=str, help="Password for Username to test MFA")
parser.add_argument("-d", "--chromedriverpath", type=str, required=True, help="Chromedriver path to use with selenium")
parser.add_argument("-x", "--url", type=str, required=True, help="OKTA URL to be tested against: https://stigs.okta.com")
parser.add_argument("-o", "--outfile", type=str, help="Outfile to Log file. Default log file set in current dir.", nargs='?', const=outfile, default=outfile)
parser.add_argument("-t", "--timedelay", help="Set time delay for OKTA /user/settings/account page to load. Default is 7 seconds", nargs='?', type=int, const=7, default=7)
parser.add_argument("--proxy", type=str, help="Set proxy server for selenium. Ex: 11.456.448.110:8080")
parser.add_argument("--usernamefield", type=str, help="Set username ID HTML field for Selenium. Only use if target OKTA page is not using ID: okta-signin-username")
parser.add_argument("--passwordfield", type=str, help="Set password ID HTML field for Selenium. Only use if target OKTA page is not using ID: okta-signin-password")
parser.add_argument("--submitfield", type=str, help="Set Selenium to find the submit field by searching for 'Sign In' value. Only use if target OKTA page is not using ID: okta-signin-submit")
args = parser.parse_args()

#Set log file by user or by default
outfile = args.outfile

#Set Username Field for Selenium
if args.usernamefield:
  EMAILFIELD = (By.ID, args.usernamefield)
else:
  EMAILFIELD = (By.ID, "okta-signin-username")

#Set Password Field for Selenium
if args.passwordfield:
  PASSWORDFIELD = (By.ID, args.passwordfield)
else:
  PASSWORDFIELD = (By.ID, "okta-signin-password")

#Set Submit Field for Selenium
if args.submitfield:
  SIGNIN = (By.XPATH, "//input[@value='Sign in']")
else:
  SIGNIN = (By.ID, "okta-signin-submit")


#Setup List for MFA Disabled Users
mfa_disabled = []

#Chrome Args
options = Options()


def log_entry(entry):

  now = datetime.now()
  ts = now.strftime("%Y-%m-%d %H:%M:%S.%f")
  #ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
  print('[{}] {}'.format(ts, entry))

  if outfile is not None:
    with open(outfile, 'a+') as file:
      file.write('[{}] {}'.format(ts, entry))
      file.write('\n')
      file.close()



#Single User Mode Function
def single_mode(username, password):

  log_entry("Execution started")

  #Set Chrome Driver Path
  CHROMEDRIVER_PATH = args.chromedriverpath
  log_entry("Chrome Driver Path: {}".format(CHROMEDRIVER_PATH))

  #OKTA URL
  log_entry("OKTA URL Set: {}".format(args.url))
  okta_url = args.url + '/user/settings/account'
  log_entry("Final OKTA URL Set: {}".format(okta_url))

  #Time Delay
  log_entry("Time Delay Set To: {} Seconds".format(args.timedelay))

  #Chrome Args
  #options = Options()
  options.add_argument("--headless") # Runs Chrome in headless mode.
  options.add_argument("--no-sandbox") # Runs Chrome in sandbox mode allowing root to run Chrome

  #Setup proxy for selenium
  if args.proxy:
    options.add_argument('--proxy-server=%s' % args.proxy)
    log_entry("Proxy Server set to: {}".format(args.proxy))

  log_entry("Using credentials {} with password {}".format(username, password))

  # driver initialization
  browser = webdriver.Chrome(chrome_options=options, executable_path=CHROMEDRIVER_PATH)

  #Set Browser URL
  browser.get(okta_url)

  # wait for email field and enter email
  WebDriverWait(browser, 15).until(EC.element_to_be_clickable(EMAILFIELD)).send_keys(username)
  
  # wait for password field and enter password
  WebDriverWait(browser, 15).until(EC.element_to_be_clickable(PASSWORDFIELD)).send_keys(password)
  
  # Click Sign-In
  WebDriverWait(browser, 15).until(EC.element_to_be_clickable(SIGNIN)).click()
  time.sleep(4)

  # Checking for bad login
  try:
    error = browser.find_element_by_xpath("//p[contains(text(),'Unable to sign in')]")
    log_entry("Error: Unsuccessful login for {}".format(username))
    log_entry("Exitting.")
    browser.quit()
    sys.exit(1)
  except NoSuchElementException:
    log_entry("Successful login for {}".format(username))


  #New dashboard requires this GET to get to the proper page
  browser.get(okta_url)
  # Ensure page is located before locating element or we wont get data back correctly 
  time.sleep(args.timedelay)



  #Setup try method to check for element not found on new dashboard and old dashboard. Common on slow internet connections
  try:
    content6 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "extra-verification-section-authenticators-container")))
    #content6 = browser.find_element_by_id('extra-verification-section-authenticators-container').text 
    mfa_verify = content6.text

  except NoSuchElementException:

    try:
      content6 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "extra-verification-section-container")))
      #content6 = browser.find_element_by_id('extra-verification-section-container').text
      mfa_verify = content6.text
      
    except NoSuchElementException:
      log_entry("Error: Increase time delay past {} seconds. seconds. Use '-t' parameter".format(args.timedelay))
      browser.quit()
      sys.exit(1)


  if re.search("Remove", mfa_verify) or re.search("Enabled", mfa_verify) or re.search("Set up another", mfa_verify):
    log_entry("MFA enabled for {}:{}".format(username,password))
  else:
    log_entry("MFA disabled for {}:{}".format(username,password))
    mfa_disabled.append(username) 

  browser.quit()



#Multi User Mode Function
def multi_mode(usernamefile, passwordfile):

  log_entry("Execution started")

  #Set Chrome Driver Path
  CHROMEDRIVER_PATH = args.chromedriverpath
  log_entry("Chrome Driver Path: {}".format(CHROMEDRIVER_PATH))

  #OKTA URL
  log_entry("OKTA URL Set: {}".format(args.url))
  okta_url = args.url + '/user/settings/account'
  log_entry("Final OKTA URL Set: {}".format(okta_url))

  #Time Delay
  log_entry("Time Delay Set To: {} Seconds".format(args.timedelay))

  #Chrome Args
  #options = Options()
  options.add_argument("--headless") # Runs Chrome in headless mode.
  options.add_argument("--no-sandbox") # Runs Chrome in sandbox mode allowing root to run Chrome

  #Setup proxy for selenium
  if args.proxy:
    options.add_argument('--proxy-server=%s' % args.proxy)
    log_entry("Proxy Server set to: {}".format(args.proxy))

  
  with open(usernamefile) as file1, open(passwordfile) as file2:
    for username, password in zip(file1, file2):
      #print(username, password)
      username = username.replace('\n','')
      password = password.replace('\n','')
      log_entry("Using credentials {} with password {}".format(username, password))

      # driver initialization
      browser = webdriver.Chrome(chrome_options=options, executable_path=CHROMEDRIVER_PATH)

      #Set Browser URL
      browser.get(okta_url)

      # wait for email field and enter email
      WebDriverWait(browser, 15).until(EC.element_to_be_clickable(EMAILFIELD)).send_keys(username)
  
      # wait for password field and enter password
      WebDriverWait(browser, 15).until(EC.element_to_be_clickable(PASSWORDFIELD)).send_keys(password)
  
      # Click Sign-In
      WebDriverWait(browser, 15).until(EC.element_to_be_clickable(SIGNIN)).click()
      time.sleep(4)

        # Checking for bad login using try method - Looking for no such element
      try:
        error = browser.find_element_by_xpath("//p[contains(text(),'Unable to sign in')]")
        log_entry("Error: Unsuccessful login for {}".format(username))
        log_entry("Moving to next set of creds.")
        browser.quit()
        continue
      except NoSuchElementException:
        log_entry("Successful login for {}".format(username))
  

      #New dashboard requires this GET to get to the proper page
      browser.get(okta_url)
      time.sleep(args.timedelay)



  #Setup try method to check for element not found on new dashboard and old dashboard. Common on slow internet connections
      try:
        content6 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "extra-verification-section-authenticators-container")))
        #content6 = browser.find_element_by_id('extra-verification-section-authenticators-container').text 
        mfa_verify = content6.text
        #print(mfa_verify)

      except NoSuchElementException:

        try:
          content6 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "extra-verification-section-container")))
          #content6 = browser.find_element_by_id('extra-verification-section-container').text
          mfa_verify = content6
      
        except NoSuchElementException:
          log_entry("Error: Increase time delay past {} seconds. seconds. Use '-t' parameter".format(args.timedelay))
          browser.quit()
          args.timedelay = args.timedelay + 7
          log_entry("Script Save: Incresing time delay for next iteration to {} seconds".format(args.timedelay))
          continue

  
      if re.search("Remove", mfa_verify) or re.search("Enabled", mfa_verify) or re.search("Set up another", mfa_verify):
        log_entry("MFA enabled for {}:{}".format(username,password))
      else:
        log_entry("MFA disabled for {}:{}".format(username,password))
        mfa_disabled.append(username) 

      browser.quit()
      mfa_verify = None


#Main Logic
if args.username and args.password:
  log_entry("Running Script in Single User Mode")
  single_mode(args.username, args.password)
elif args.usernamefile and args.passwordfile:
  log_entry("Running Script in Multi-User Mode")
  multi_mode(args.usernamefile, args.passwordfile)
else:
  parser.print_help(sys.stderr)
  log_entry("Error: Not input found for username/usernamefile or password/passwordfile")
  sys.exit(1)


#List out MFA Disabled users
for x in mfa_disabled:
  log_entry("MFA [DISABLED]: {}".format(x))

# End Execution
log_entry("Execution Done.")

