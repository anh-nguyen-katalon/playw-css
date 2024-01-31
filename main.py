from playwright.sync_api import sync_playwright
import queue
import re
import os
import json

### BEGIN INPUTS ###
# HOME_PAGE = "https://katalon.com"
HOME_PAGE = "https://testops.katalon.io"
MAX_NUM_PAGES = 100
### END INPUTS ###

with open("bundle.js", "r") as f:
    playw_css_script = f.read()

with open("test.js", "r") as f:
    role_tree_script = f.read()

def get_absolute_href(href, domain):
    # remove trailing slash from domain
    domain = re.sub(r'/+$', '', domain)
    # turn relative urls into absolute urls
    if href.startswith("/"):
        href = domain + href

    # remove trailing slash
    href = re.sub(r'/+$', '', href)
    return href

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # # HARDCODE only for Katalon.com: go to home page and accept cookies before crawling
    # page.goto(HOME_PAGE, wait_until="networkidle")
    # page.get_by_role("button", name="Accept All Cookies").click()

    discovered_urls = set()
    num_visited = 0
    q = queue.Queue()

    q.put(HOME_PAGE)
    discovered_urls.add(HOME_PAGE)

    while not q.empty() and num_visited < MAX_NUM_PAGES:
        try:
            url = q.get()
            num_visited += 1
            print (num_visited)
            print (url)

            # go to page
            print ("Going to page")
            page.goto(url, wait_until="networkidle")

            # get the current url
            url = page.url
            discovered_urls.add(url)

            # get role tree
            page.add_script_tag(content=playw_css_script)
            print ("Getting role tree")
            role_tree = page.evaluate(role_tree_script + "getRoleTree();")
        
            # create file path to save role tree
            dir_path = re.sub(r'^https?://', '', url) # remove protocol
            dir_path = re.sub(r'/+$', '', dir_path) # remove trailing slash
            file_path = f"output/{dir_path}/role_tree.json"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # save role tree to file
            with open(file_path, "w") as f:
                f.write(json.dumps(role_tree, indent=2))

            # discover child urls
            domain = re.search(r'https?://[^/]+', url).group(0)
            for a in page.locator("a").all():
                href = a.get_attribute("href")
                if href is not None:
                    href = get_absolute_href(href, domain)
                    if href not in discovered_urls:
                        discovered_urls.add(href)
                        q.put(href)
        except Exception as e:
            print (url, e)
    browser.close()