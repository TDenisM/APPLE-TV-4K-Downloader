import requests, json, os, re
import pywidevine.clients.appletv.config as aptv_cfg
import urllib.parse

currentFile = 'appletv'
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
cookies_file = dirPath + '/cookies/' + 'cookies_aptv.txt'

def get_auth_headers(content_url):

    def urldecode(str):
        return urllib.parse.unquote(str)

    def parseCookieFile(cookiefile):
        cookies = {}
        with open (cookies_file, 'r') as fp:
            for line in fp:
                if not re.match(r'^\#', line):
                    lineFields = line.strip().split('\t')
                    cookies[lineFields[5]] = lineFields[6]
        return cookies

    COOKIES = parseCookieFile(dirPath + '/cookies/' + cookies_file)
    COMMOM_HEADERS = aptv_cfg.COMMOM_HEADERS
    COMMOM_HEADERS["media-user-token"] = COOKIES["media-user-token"]

    while 1:
        html_data = requests.get(url=content_url, headers=COMMOM_HEADERS)
        if html_data.ok:
            break

    html_data = html_data.text.replace('\r\n', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('  ', '')
    html_data_list = re.split('(</div>)(?i)', html_data)

    json_web = []
    for div in html_data_list:
        rg = re.compile('(<meta name="web-tv-app/config/environment" content=")(.*)("><!-- EMBER_CLI_FASTBOOT_TITLE --)')
        m = rg.search(div)
        if m:
            AUTH_TOKEN = json.loads(urldecode(m[2]))["MEDIA_API"]["token"]

    COMMOM_HEADERS["authorization"] = "Bearer %s" % (AUTH_TOKEN)

    return {"wvHeaders": COMMOM_HEADERS}, COOKIES