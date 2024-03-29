# OKTA MFA Check

White Knight Labs

Launch a authenticated spray against an OKTA instance to determine which users currently have MFA enabled or disabled. This script uses Python Selenium in headless mode with the Chrome driver to login to the OKTA instance. Once authentication is sucessful, the script targets an iframe to gather the current MFA options supported in OKTA.  

This tool was created to work after running a password sprayer (CredMaster). During engagments it is common to find users with weak passwords set such as "Summer2021" and "Winter2022". VPN is commonly deployed for remote users and can be abused in certain ways. One of the most common ways is to find users that have no MFA setup. This tool will allow you to determine which users have MFA not configured or disabled. During testing we have found that some clients use OKTA as the MFA option for VPN configurations, this is common to see with Cisco devices. When targeting users without MFA, it is very easy to login to the OKTA instance and configure MFA options for multiple users.

## Benefits
- Uses Python Selenium to authenticate to OKTA instance
- Authentication delay options
- Helps bypass OKTA API Rate-Limting 
- Runs as a single thread (Low Detection Rates)
- Works with fireprox and proxy servers
- Works against New/Old OKTA Dashboards


## Install ##
Script is currently based on Python3. This script has only been tested on OSX. Should work fine on Linux. Windows is an unknown.
<br/>
<br/>

**Installing Selenium:**
```
pip install selenium
```
Check [here](https://selenium-python.readthedocs.io/installation.html) for more info on Selenium install.
<br/>
<br/>

**ChromeDriver Download:**

Download the Chromedriver from the following URL: https://chromedriver.chromium.org/

Make sure to match your current chrome version to the driver or you will get an error. Just update Chrome and download newest driver.
<br/>
<br/>

## Quick Use ##
The tool assumes you have a valid login for OKTA. There is some error checking done to help prevent issues but its basic. Selenium will check if there is a bad login and report it back to you. The tool currently supports two (2) modes:

- Single-Mode - Attempts to authenticate with a single username and password
- Multi-Mode - Attempts to authenticate with a userfile and passwordfile

The Multi-mode userfile and password file must contain the same amount lines in each file. The script reads the username from the first line of the file and then the password from the first line of the password file. If your file is not formatted correctly you will have errors. I have included an example userfile and passwordfile as reference. 

**Example Use (Single-Mode User):**
```
python okta-mfa-check.py -u username -p password -d ./chromedriver -x "https://example.okta.com"
```

**Example Use (Multi-Mode User):**
```
python okta-mfa-check.py -P userfile -P passwordfile -d ./chromedriver -x "https://example.okta.com"
```

The tool requires a single username and password or a username list and a password list.
<br/>
<br/>

Example of Multi-Mode. Uses a username file and password file. These files have been uploaded as a base for you to start with. The screen recording shows three (3) users, 1 with MFA and 2 without MFA. This video has "headless" mode turned off to show you what the script really does.

https://user-images.githubusercontent.com/97109724/148791567-8ad34f3a-66a3-4546-8fcc-41f1886367a0.mov

## Password Spraying:
If your looking to password sprayer check out [CredMaster](https://github.com/knavesec/CredMaster)

This tool was created for post-exploitation to help determine if MFA was enabled/disabled for each compromised user. This tool can be turned into a password sprayer that uses Selenium but it is not currently supported. The goal is to get away from the OKTA API Rate Limit and detection that is very common when using tools like CredMaster.

## TODO:

- ~Add proxy support option~
- Add support for fireprox similar to how credmaster is setup
- Add option to enable MFA SMS automatically with Selenium
- Add support for password spraying
- ~Support for additional OKTA MFA options~
- Re-Write Muti-Mode to support 1 file instead of 2

## Credits
- Ellis Springe ([knavesec](https://twitter.com/knavesec)) - [CredMaster](https://github.com/knavesec/CredMaster)

