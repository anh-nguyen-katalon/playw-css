from playwright.sync_api import sync_playwright
import queue
import re
import os
import json

def preprocess_href(href, home_page):
    # turn relative urls into absolute urls
    if href.startswith("/"):
        href = home_page[:-1] + href
    # remove query parameters
    query_index = href.find("?")
    href = href[:query_index] if query_index != -1 else href
    # remove trailing slash
    href = re.sub(r'/+$', '', href)
    return href

with open("bundle.js", "r") as f:
    playw_css_script = f.read()

with open("test.js", "r") as f:
    get_page_features_script = f.read()

print ("bundle.js script:", playw_css_script[:100])
print ("test.js script", get_page_features_script[:100])

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    home_page = "https://kobu.co"

    discovered_urls = set()
    num_visited = 0
    q = queue.Queue()

    q.put(home_page)

    discovered_urls.add(home_page)
    while not q.empty() and num_visited < 5:
        url = q.get()
        page.goto(url, wait_until="networkidle")
        print (url)
        num_visited += 1

        # get page features
        page.add_script_tag(content=playw_css_script)
        pf = page.evaluate(get_page_features_script + "getPageFeatures();")
        
        # write pf to file
        dir_path = url.replace(home_page, "")
        dir_path = re.sub(r'^/+|/+$', '', dir_path)
        os.makedirs(os.path.join("output", dir_path), exist_ok=True)
        with open(f"output/{dir_path}/features.json", "w") as f:
            f.write(json.dumps(pf, indent=2))

        # discover child urls
        for a in page.locator("a").all():
            href = a.get_attribute("href")
            if href is not None:
                href = preprocess_href(href, home_page)
                if href.startswith(home_page) and href not in discovered_urls:
                    discovered_urls.add(href)
                    q.put(href)
    browser.close()