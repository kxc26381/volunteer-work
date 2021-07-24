# CampusLabs University Health-Related Student Organizations Contact Information Webscraper

## Description
This is an automated script that:
1. scrapes the contact information of every health-related student organization on any university's CampusLabs organization's website
2. writes the contact information to Google Sheets via the Google Sheets API

## Technologies Used
This script was written in Python using the selenium, BeautifulSoup, pandas, gspread, and oauth2client modules.

## Run
*Note: remove quotation marks when running the commands listed below*

### Prerequisites
1. Download the latest version of Python from https://www.python.org/downloads/ 
2. Open command prompt
3. Run 'git clone https://github.com/kxc26381/volunteer-work.git' in command prompt
4. Run 'pip install jupyterlab' in command prompt
5. Run 'pip install -r requirements.txt' in command prompt
    - If you run into an error with some packages not installing, go through each package that didn't install and run 'pip install --user package-name' in command prompt
        - i.e. 'pip install --user selenium'
        - It will usually tell you which packages didn't install, but if it is not obvious, you should install each package listed in the 'requirements.txt' file as instructed above to be safe

### Option 1
1. Run 'jupyter lab' in command prompt
    - Jupyter Lab should automatically open in browser
2. Open 'final_volunteer_work.ipynb' in Jupyter Lab
3. Run all cells and follow instructions when prompted in 'final_volunteer_work.ipynb' notebook

### Option 2
1. Run 'python final_volunteer_work.ipynb' in command prompt
2. Follow instructions when prompted

