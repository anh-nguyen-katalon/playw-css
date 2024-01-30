# PLAYW-CSS

## Overview
This script crawls a website and saves the role tree of each page to a json file.


## Setup
- Open terminal at root directory
- Create virtual environment: 
```
python3 -m venv env
```
- Activate virtual environment:
```
source env/bin/activate
```
- Install dependencies:
```
pip install -r requirements.txt
```
- Install playwright browsers:
```
playwright install
```
- Go to main.py and change the inputs at the top of the file
```
### BEGIN INPUTS ###
HOME_PAGE = "https://katalon.com"
MAX_NUM_PAGES = 100
### END INPUTS ###
```

`HOME_PAGE`: the url of the website to crawl

`MAX_NUM_PAGES`: the maximum number of pages to crawl


Note: The section of code below is only hardcoded for Katalon.com to Accept cookies before crawling.
```
### BEGIN HARDCODE ###
# HARDCODE only for Katalon.com: go to home page and accept cookies
page.goto(HOME_PAGE, wait_until="networkidle")
page.get_by_role("button", name="Accept All Cookies").click()
### END HARDCODE ###
```

-  Run the script:
```
python main.py
```
- Output will be saved in the `output` folder
