from playwright.sync_api import sync_playwright
import queue
import re
import os
import json

def preprocess_href(href, home_page):
    # turn relative urls into absolute urls
    home_page = re.sub(r'/+$', '', home_page) # remove trailing slash
    if href.startswith("/"):
        href = home_page + href
    # remove query parameters
    query_index = href.find("?")
    href = href[:query_index] if query_index != -1 else href
    # remove trailing slash
    href = re.sub(r'/+$', '', href)
    return href

with open("bundle.js", "r") as f:
    playw_css_script = f.read()

with open("test.js", "r") as f:
    role_tree_script = f.read()

print ("bundle.js script:", playw_css_script[:100])
print ("test.js script", role_tree_script[:100])

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    home_page = "https://kobu.co"

    discovered_urls = set()
    num_visited = 0
    q = queue.Queue()

    q.put(home_page)

    discovered_urls.add(home_page)
    while not q.empty() and num_visited < 3:
        try:
            url = q.get()
            print (url)

            print ("Going to page")
            page.goto(url, wait_until="networkidle")

            num_visited += 1

            # get role tree
            page.add_script_tag(content=playw_css_script)
            print ("Getting role tree")
            role_tree = page.evaluate(role_tree_script + "getRoleTree();")
            
            # write role tree to file
            dir_path = re.sub(r'^https?://', '', url) # remove protocol
            dir_path = re.sub(r'/+$', '', dir_path) # remove trailing slash
            os.makedirs(os.path.join("output", dir_path), exist_ok=True)
            with open(f"output/{dir_path}/role_tree.json", "w") as f:
                f.write(json.dumps(role_tree, indent=2))

            # discover child urls
            for a in page.locator("a").all():
                href = a.get_attribute("href")
                if href is not None:
                    href = preprocess_href(href, home_page)
                    if href.startswith(home_page) and href not in discovered_urls:
                        discovered_urls.add(href)
                        q.put(href)
        except Exception as e:
            print (url, e)
    browser.close()