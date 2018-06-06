"""Cookie Monster - Main CLI File"""
import os
import requests
import time
import sys
import csv
import json
from cookie_monster.args import Args
from bs4 import BeautifulSoup

# parse command line arguments
ARGS = Args()

# Gloabl Variables
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Token %s' % ARGS.key
}

def read_sitemap(url):
    """Read the sitemap and return a list of URLs"""
    urls = []
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; WebCookies/1.1; +https://webcookies.org/doc/webcookies-robot)'
    })
    soup = BeautifulSoup(response.content, 'lxml')

    # Grab URLs from sitemap index file (if they exist)
    sitemap_tags = soup.find_all("sitemap")
    for sitemap in sitemap_tags:
        urls += read_sitemap(sitemap.findNext("loc").text)

    # Add URLs to list
    url_tags = soup.find_all("url")
    for url_tag in url_tags:
        urls.append(url_tag.findNext("loc").text)

    return urls

def scan_url(url):
    """Scans a URL for cookies or returns existing ID of previous scan"""
    r = requests.post('https://webcookies.org/api2/urls/', headers=headers, json={'url': url})

    # 409 - the URL is already in the database
    if r.status_code == 409:
        if ARGS.force:
            r = requests.post("https://webcookies.org/api2/urls/?rescan=True",
                              headers=headers, json={'url': url})
        else:
            url_id = r.json().get('url_id')

    # 201 - the URL was added to database
    if r.status_code == 201:
        task_id = r.json().get('task_id')
        url_id = r.json().get('url_id')

        # wait for completion
        while True:
            r = requests.get('https://webcookies.org/api2/task-status/%s' % task_id,
                                headers=headers)
            status = r.json().get('status')
            if status == 'PENDING':
                print('[PENDING] %s' % url)
                time.sleep(60)
            if status == 'FAILED':
                print('[ERROR] %s' % url)
                break
            if status == 'SUCCESS':
                print('[SUCCESS] %s' % url)
                break

    if r.status_code not in[200, 201, 409]:
        print(r.json())
        print('[%s ERROR] Scanning: %s' % (r.status_code, url))
        return False
    else:
        return url_id

def get_results(url_id):
    """Get the scanned results of a URL"""
    r = requests.get('https://webcookies.org/api2/urls/%s' % url_id, headers=headers)
    return r.json()

def get_cookie(url):
    """Get the scanned results of a cookie/storage item"""
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()

def read_cookie(type, id, data):
    """Output the data of the cookie into an organized list"""
    l = [type, id]

    if 'name_ref' in data:
        l.append(data['name_ref']['name'])
    else:
        l.append('')

    if 'domain_ref' in data:
        l.append(data['domain_ref']['domain'])
    else:
        l.append('')

    if 'reference' in data:
        if data['reference']:
            l.append(data['reference']['name'])
        else:
            l.append('')
    else:
        l.append('')

    return l

def main():
    """Main Function"""
    # main variables
    filename = ARGS.output
    output = []

    # create any directories needed for the CSV
    path = os.path.dirname(filename)
    if path:
        os.makedirs(path, exist_ok=True)

    # all the cookie ids
    cookies = {
        'http': [],
        'flash': [],
        'local': [],
        'session': []
    }

    # read the sitemap
    urls = read_sitemap(ARGS.sitemap)

    # get all the url_ids
    for url in urls:
        uid = scan_url(url)
        if uid:
            data = get_results(uid)
            try:
                for cid in data['httpcookie_set']:
                    if cid not in cookies['http']:
                        cookies['http'].append(cid)
                for cid in data['flashcookie_set']:
                    if cid not in cookies['flash']:
                        cookies['flash'].append(cid)
                for cid in data['localstoragecookie_set']:
                    if cid not in cookies['local']:
                        cookies['local'].append(cid)
                for cid in data['sessionstoragecookie_set']:
                    if cid not in cookies['session']:
                        cookies['session'].append(cid)
            except:
                print('ERROR!')
                print(data)
        time.sleep(1)

    # debug
    print('[INFO] Finished Scanning Pages')
    print('[INFO] HTTP Cookies: %i' % len(cookies['http']))
    print('[INFO] Flash Cookies: %i' % len(cookies['flash']))
    print('[INFO] Local Cookies: %i' % len(cookies['local']))
    print('[INFO] Session Cookies: %i' % len(cookies['session']))

    with open('cookies.tmp.json', 'w') as temp:
        json.dump(cookies, temp)
    print('[INFO] Saved Temporary JSON File')

    # get the HTTP cookies
    for cid in cookies['http']:
        url = 'https://webcookies.org/api2/http-cookie/%s' % cid
        print('[INFO] %s' % url)
        data = get_cookie(url)
        output.append(read_cookie('http', cid, data))

    # get the flash cookies
    for cid in cookies['flash']:
        url = 'https://webcookies.org/api2/flash-cookie/%s' % cid
        print('[INFO] %s' % url)
        data = get_cookie(url)
        output.append(read_cookie('flash', cid, data))

    # get the local storage
    for cid in cookies['local']:
        url = 'https://webcookies.org/api2/localstorage-cookie/%s' % cid
        print('[INFO] %s' % url)
        data = get_cookie(url)
        output.append(read_cookie('local', cid, data))

    # get the session storage
    for cid in cookies['session']:
        url = 'https://webcookies.org/api2/sessionstorage-cookie/%s' % cid
        print('[INFO] %s' % url)
        data = get_cookie(url)
        output.append(read_cookie('session', cid, data))

    # debug
    print('[INFO] Finished Retrieving Cookies')

    # save the output as a CSV
    with open(filename, 'w') as outfile:
        wr = csv.writer(outfile, quoting=csv.QUOTE_ALL)
        wr.writerows(output)

    sys.exit(0)

if __name__ == '__main__':
    main()
