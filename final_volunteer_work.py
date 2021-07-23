#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Importing necessary libraries
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import math
import os
import requests
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# In[4]:


#  Clicks the load more button so that entries can load
def getButton(browser):
    browser.execute_script("document.getElementsByTagName('button')[0].click()")

#  Scrolls the page down so most recent entries can be viewed
def scrollDown(browser):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
#  Main method involved with parsing. Gets all urls from main webpage
def parse(url):
    try:
        print("Running...")
        inputEntered = 0;
        osDriver = None;
        while inputEntered == 0:
            os = input("Enter Operating System to use (MS Edge, Chrome, Opera, and Firefox): ").lower().replace(" ", "")
            if os == "msedge":
                osDriver = "./msedgedriver"
                inputEntered = 1;
            elif os == "chrome":
                osDriver = "./chromedriver"
                inputEntered = 1;
            elif os == "opera":
                osDriver = "./operadriver"
                inputEntered = 1;
            elif os == "firefox":
                osDriver = "./geckodriver"
                inputEntered = 1;
            else:
                print("Input not accepted. Please enter either: MS Edge, Chrome, Opera, or Firefox")

        #  driver that loads Chrome
        driver = webdriver.Chrome(executable_path=osDriver)
        
        # used to store all organization urls as strings
        child_list = []
        
        # list of queries to add on to org url
        query_list = ["health", "mental", "medical"]

        for query in query_list:
            url_query = ""
            
            url_query = url + "?query=" + query + "/"
        
            # requests access to uga organizations webpage
            driver.get(url)

            # Waits 2 seconds for website to load to avoid loading issues
            time.sleep(2)

            #  clubs variable is extracted from the webpage and is the total number of webpages that are listed on the website
            clubs = math.ceil((int(driver.find_element_by_xpath("//div[@id='org-search-results']/following-sibling::div").find_element_by_xpath(".//*").text.rsplit(None, 1)[1][:-1]) - 10)/10)

            # adds 5 to clubs
            clubs += 5

            #  This loop clicks the "Load More" button club number of times until all entires have been loaded
            while clubs != 0:

                #  sleeps for 0.5 to avoid loading error
                time.sleep(0.5)
    
                #  scrolls the window down so user can see most recent entries
                scrollDown(driver)
            
                try:
                    #  clicks button and if all entries are loaded
                    #  error for clicking the button is caught and loop is broken out of
                    getButton(driver)
                except:
                    break

                #  club decrements every time loop goes through
                clubs -= 1

            #  gets all links to club websites and appends them to list
            for child in BeautifulSoup(driver.page_source, "html.parser").find('div', {'id': 'org-search-results'}).find_all('a'):
                child_list.append(child['href'])

        print("Finished!")
    
        return list(set(child_list))
    except:
        pass
        print("Error Occurred while running. Program Stopped.")

# Asking user to input organization hub url
university_org_hub_url = input("Enter the organization hub url (Make sure to add an url with a '/' at the end - i.e. https://utrgv.campuslabs.com/engage/organizations/): ")

# Returning url extensions of list of clubs for all queries
club_list = parse(university_org_hub_url)


# In[5]:


# Returning info about all clubs
def return_club_info(university_org_list_url, url_extension_list):        
    main_df = pd.DataFrame({
            'State':'',
            'Volunteer':'',
            'University':'',
            'Department/Club Name':'',
            'Department/Club Email':'',
            'Contact Name':'',
            'Contact Email':'',
            'Contact Phone Number':'',
            'Comments':[]
        })
    
    for url in url_extension_list:
        org_url = university_org_list_url + url

        page = requests.get(org_url)
        
        #  creates soup of html
        soup = BeautifulSoup(page.content, "html5lib")
        
        content = soup.find('div', {'class':"engage-application"}).find('script')
        json_raw = content.text
        json_raw = json_raw[25:-1]

        club_info = json.loads(json_raw)
                
        email = []
        
        if 'email' in club_info['preFetchedData']['organization'].keys():
            email.append(club_info['preFetchedData']['organization']['email'])
        else:
            email.append('')
            
        primary_contact = []
        
        if 'primaryContact' in club_info['preFetchedData']['organization'].keys():
            if club_info['preFetchedData']['organization']['primaryContact'] is None:
                email = [''] * 3
            else:
                if 'firstName' in club_info['preFetchedData']['organization']['primaryContact'].keys():
                    email.append(club_info['preFetchedData']['organization']['primaryContact']['firstName'])
                else:
                    email.append('')

                if 'lastName' in club_info['preFetchedData']['organization']['primaryContact'].keys():
                    email.append(club_info['preFetchedData']['organization']['primaryContact']['lastName'])
                else:
                    email.append('')

                if 'primaryEmailAddress' in club_info['preFetchedData']['organization']['primaryContact'].keys():
                    email.append(club_info['preFetchedData']['organization']['primaryContact']['primaryEmailAddress'])
                else:
                    email.append('')
        else:
            email = [''] * 3
        
        contact_info = []
        
        if 'contactInfo' in club_info['preFetchedData']['organization'].keys():
            if len(club_info['preFetchedData']['organization']['contactInfo']) == 0:
                contact_info.append('')
            else:
                if club_info['preFetchedData']['organization']['contactInfo'][0] is None:
                    contact_info.append('')
                else:
                    if 'phoneNumber' in club_info['preFetchedData']['organization']['contactInfo'][0].keys():
                        contact_info.append(club_info['preFetchedData']['organization']['contactInfo'][0]['phoneNumber'])
                    else:
                        contact_info.append('')
        else:
            contact_info.append('')
        
        social_media = []
        
        if 'socialMedia' in club_info['preFetchedData']['organization'].keys():
            if club_info['preFetchedData']['organization']['socialMedia']['externalWebsite'] is None:
                social_media.append('')
            else:
                if 'externalWebsite' in club_info['preFetchedData']['organization']['socialMedia'].keys():
                    if 'chat' in club_info['preFetchedData']['organization']['socialMedia']['externalWebsite']:
                        social_media.append('')
                    else:
                        social_media.append(club_info['preFetchedData']['organization']['socialMedia']['externalWebsite'])
                else:
                    social_media.append('')
            
            if club_info['preFetchedData']['organization']['socialMedia']['tumblrUrl'] is None:
                social_media.append('')
            else:
                if 'tumblrUrl' in club_info['preFetchedData']['organization']['socialMedia'].keys():
                    social_media.append(club_info['preFetchedData']['organization']['socialMedia']['tumblrUrl'])
                else:
                    social_media.append('')
                    
            if club_info['preFetchedData']['organization']['socialMedia']['facebookUrl'] is None:
                social_media.append('')
            else:
                if 'facebookUrl' in club_info['preFetchedData']['organization']['socialMedia'].keys():
                    social_media.append(club_info['preFetchedData']['organization']['socialMedia']['facebookUrl'])
                else:
                    social_media.append('')
            
            if club_info['preFetchedData']['organization']['socialMedia']['instagramUrl'] is None:
                social_media.append('')
            else:
                if 'instagramUrl' in club_info['preFetchedData']['organization']['socialMedia'].keys():
                    social_media.append(club_info['preFetchedData']['organization']['socialMedia']['instagramUrl'])
                else:
                    social_media.append('')
            
            if club_info['preFetchedData']['organization']['socialMedia']['twitterUrl'] is None:
                social_media.append('')
            else:
                if 'twitterUrl' in club_info['preFetchedData']['organization']['socialMedia'].keys():
                    social_media.append(club_info['preFetchedData']['organization']['socialMedia']['twitterUrl'])
                else:
                    social_media.append('')
            
            if club_info['preFetchedData']['organization']['socialMedia']['twitterUserName'] is None:
                social_media.append('')
            else:
                if 'twitterUserName' in club_info['preFetchedData']['organization']['socialMedia'].keys():
                    social_media.append(club_info['preFetchedData']['organization']['socialMedia']['twitterUserName'])
                else:
                    social_media.append('')
        else:
            social_media = [''] * 6
        
        fields = [club_info['preFetchedData']['organization']['name']]
        
        fields = fields + email + primary_contact + contact_info + [org_url] + social_media
        
        for index in range(len(fields)):
            if fields[index] == None:
                fields[index] = ''

        contact_us_form_url = ''

        if org_url[-1] != '/':
            contact_us_form_url = org_url + '/contact'
        else:
            contact_us_form_url = org_url + 'contact'

        data = {
            'State':'',
            'Volunteer':'',
            'University':'',
            'Department/Club Name':[fields[0]],
            'Department/Club Email':[fields[1]],
            'Contact Name':[fields[2] + ' ' + fields[3]],
            'Contact Email':[fields[4]],
            'Contact Phone Number':[fields[5]],
            'Comments':[contact_us_form_url]
        }

        df = pd.DataFrame(data)

        if fields[-1] != '' and fields[-1] != None:
            fields[-1] = 'https://twitter.com/' + fields[-1]

        for index in range(-6, 0):
            if fields[index] == '' or fields[index] == None:
                fields.pop(index)

        for social_media_contact in fields[6:]:
            df_row = df.iloc[0,:].copy()
            df_row['Comments'] = social_media_contact
            df = df.append([df_row], ignore_index=True)
        
        main_df = main_df.append([df], ignore_index=True)        
        
    values = main_df.values.tolist()
    sh.values_append(sheetName, {'valueInputOption': 'USER_ENTERED'}, {'values': values})
        
def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

university_url = remove_suffix(university_org_hub_url, '/engage/organizations/')

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'service_account.json', scope)

spreadsheetId = '1qsAF7EmTnFiiDc9Wamkm54dAy4SAjIVvk2DzR7JQbA4'  
sheetName = 'Master' 

gc = gspread.authorize(credentials)
sh = gc.open_by_key(spreadsheetId)

return_club_info(university_url, club_list)

