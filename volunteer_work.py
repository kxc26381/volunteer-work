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


# In[2]:


#  Clicks the load more button so that entries can load
def getButton(browser):
    browser.find_element_by_css_selector(".outlinedButton button").click()
    
#  Scrolls the page down so most recent entries can be viewed
def scrollDown(browser):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")


# In[11]:


def parse(input_url):
    inputEntered = 0;
    osDriver = None;
    while inputEntered == 0:
        os = input("Enter browser to use (MS Edge, Chrome, Opera, and Firefox): ").lower().replace(" ", "")
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

    child_list = []
    final_list = []
    
    query_list = ["health", "mental%20health", "medical"]
    
    for query in query_list:
        url_query = ""

        if input_url[-1] == "/":
            input_url = input_url[:-1]

        url_query = input_url + "?query=" + query + "/"

        # driver.get("https://uh.campuslabs.com/engage/organizations?query=health")
        driver.get(url_query)

        # Waits 2 seconds for website to load to avoid loading issues
        time.sleep(2)
        
        try:
            elem = driver.find_element_by_css_selector("#org-search-results + div div")
            clubs = int((int(elem.text[17:][:-1]) - 10) / 10)

            # adds 5 to clubs
            clubs += 5

            #  This loop clicks the "Load More" button club number of times until all entires have been loaded
            while clubs != 0:

                #  sleeps for 0.5 to avoid loading error
                time.sleep(1)

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

            for child in BeautifulSoup(driver.page_source, "html5lib").find('div', {'id': 'org-search-results'}).find_all('a'):
                child_list.append(child['href'])
        except:
            pass
        
        elems = driver.find_elements_by_css_selector("ul a[href]")
        links = [elem.get_attribute('href') for elem in elems]

        final_list = final_list + links
    
    university_url = input_url.replace("/engage/organizations", "")

    for extension in child_list:
        url = university_url + extension[:-1]
        final_list.append(url)

    final_list = list(set(final_list))
    
    return final_list


# In[12]:


university_org_hub_url = input("Enter the organization hub url (Must have an 'https://'' as the beginning of the url and not include '/' at the end of the url - i.e. https://uh.campuslabs.com/engage/organizations): ")
club_list = parse(university_org_hub_url)


# In[17]:


def return_club_info(url_list):        
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
    
    for url in url_list:
        page = requests.get(url)
        
        #  creates soup of html
        soup = BeautifulSoup(page.content, "html5lib")
                
        if soup is None:
            continue
        else:
            content = soup.find('div', {'class':"engage-application"})
            
            if content is None:
                continue
            else:
                try:
                    content = content.find('script')
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

                    fields = fields + email + primary_contact + contact_info + [url] + social_media

                    for index in range(len(fields)):
                        if fields[index] == None:
                            fields[index] = ''

                    contact_us_form_url = ''

                    if url[-1] != '/':
                        contact_us_form_url = url + '/contact'
                    else:
                        contact_us_form_url = url + 'contact'

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
                except:
                    pass
                
    values = main_df.values.tolist()
    
    if values:
        sh.values_append(sheetName, {'valueInputOption': 'USER_ENTERED'}, {'values': values})


# In[18]:


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'env/service_account.json', scope)

spreadsheetId = '1qsAF7EmTnFiiDc9Wamkm54dAy4SAjIVvk2DzR7JQbA4'  
sheetName = 'Master' 

gc = gspread.authorize(credentials)
sh = gc.open_by_key(spreadsheetId)

return_club_info(club_list)

