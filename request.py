import requests
import time
# import magic
import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
from requests.compat import chardet
import config
import pprint
import re
from utils import crawlutils

connect_timeout = 6 # is the amount of time the client should wait to establish a connection to the server
read_timeout = 5 # is the amount of time it should wait between bytes from the server
chunk_size = 1024 * 128

# http://www.mobify.com/blog/http-requests-are-hard/
def getSource(url):
    headers = {'User-Agent':config.userAgent}
    r = requests.Response()
    try:
        r = requests.get(url, headers=headers, timeout=(connect_timeout, read_timeout), verify=False, stream=True, allow_redirects=True)
        r.raise_for_status()
        r.textencoding = ''
        r.textcontent = ''
        # reason is by default http status reason ('OK' in most cases)

        if r.headers.get('Content-Length') and int(r.headers.get('Content-Length')) > config.maxPageSize:
            r.reason = 'response too large'
            # raise ValueError(r.reason)
        size = 0
        start = time.time()
        contents = bytes()
        for chunk in r.iter_content(chunk_size):
            if time.time() - start > config.maxPageDownloadTime:
                r.reason = 'timeout riched'
                r.close()
                break
            size += len(chunk)
            if size > config.maxPageSize:
                r.reason = 'response too large'
                r.close()
                break
            contents += chunk

        # mime = magic.from_buffer(contents, mime=True)
        # if mime == "text/html":
        encoding = r.encoding
        if encoding is None:
            # detect encoding
            encoding = chardet.detect(contents)['encoding']
            r.encoding = encoding

        htmlEncoding = crawlutils.detectEncodingfromHTML(str(contents, encoding='UTF-8', errors='replace'))
        if htmlEncoding:
            encoding = htmlEncoding

        # Apply encoding
        try:
            textcontent = str(contents, encoding, errors='replace')
            # return textcontent
        except (LookupError, TypeError):
            textcontent = str(contents, errors='replace')
            # return textcontent
        r.textencoding = encoding
        r.textcontent = textcontent

    except requests.exceptions.ConnectTimeout as e:
        r.reason = 'exception connect timeout'
    except requests.exceptions.ReadTimeout as e:
        r.reason = 'exception read timeout'
    except requests.exceptions.ConnectionError as e:
        r.reason = 'exception connection error'
    except requests.exceptions.TooManyRedirects as e:
        r.reason = 'exception too many redirects'
    except Exception as e:
        if not r.reason or r.reason == 'OK':
            r.reason = 'exception requests'
        # raise e
    if not hasattr(r, 'textcontent'):
        r.textcontent = ''
    return r

def testEncoding():
    websites = [("http://www.b-idol.com/","shift_jis"),
                ("http://seo-vita.net/","windows-1251"),
                ("http://hotel-grantia.co.jp","UTF-8"),
                ("http://hotel-deli.com","UTF-8"),
                ("http://seo-tube.ru","UTF-8"),
                ("http://www.qnwz.cn/html/yinlegushihui/magazine/2013/0524/425731.html","gb2312"),
                ("http://books.rakuten.co.jp/event/e-book/accessories/?scid=wi_ich_lnk_top_genremenu_kobo","euc-jp"),
                ("http://taobao.com","gbk")
                ]
    for url, value in websites:
        try:
            r = getSource(url)
            if r.textencoding.lower()!=value.lower():
                print("Encoding problem at ",url)
                print("Encoding detected:",r.textencoding.lower(),'Encoding expected:',value.lower())
        except Exception as e:
            print(r.reason)



if __name__ == '__main__':
    # Encoding tests
    # http://stackoverflow.com/questions/436220/python-is-there-a-way-to-determine-the-encoding-of-text-file
    # https://en.wikipedia.org/wiki/Charset_detection
    testEncoding()