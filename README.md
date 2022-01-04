# OKTA MFA Check

Launch a authenticated spray against an OKTA instance to determine which users currently have MFA enabled or disabled. This script uses Python Selenium in headless mode with the Chrome driver to login to the OKTA instance. Once authentication is sucessful, the script targets an iframe to gather the current MFA options supported in OKTA.  

This tool was created to work after running a password sprayer (CredMaster). During engagments it is common to find users with weak passwords set such as "Summer2021" and "Winter2022". VPN is commonly deployed for remote users and can be abused in certain ways. One of the most common ways is to find users that have no MFA setup. This tool will allow you to determine which users have MFA not configured or disabled. 


##Benefits
- Uses Python Selenium to authenticate to OKTA instance
- Authentication delay options
-  





TODO:

- Add proxy support
- support for fireprox similar to credmaster
- 
