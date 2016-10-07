import urllib
import urllib.parse

def isAbsolute(url):
    '''
    :param url: string
    :return: boolean, True for absolute urls, even the url is protocol relative
    '''
    return bool(urllib.parse.urlparse(url).netloc)


def isProtocolRelative(url):
    try:
        if url.index(r'//') == 0:
            return True
    except:
        return False


def join(base, relative):
    return urllib.parse.urljoin(base, relative)


def getDomain(url, strict=True):
    if isAbsolute(url):
        uri = urllib.parse.urlparse(url)
        return uri.netloc
    else:
        if strict:
            raise Exception("absolute url expected")
        else:
            return ''

def removeSchema(url):
    return url.replace('http://','').replace('https://','')

def makeAbsolute(link, base, parentUrl=''):
    # TODO check base to be absolute
    if not isAbsolute(link):
        newLink = join(base, link)
    else:
        newLink = link

    if isProtocolRelative(newLink):
        parts = urllib.parse.urlparse(base)
        if parts.scheme == '':
            # GET scheme from parent absolute url, not from base
            if parentUrl:
                parentUrlParts = urllib.parse.urlparse(parentUrl)
                if parentUrlParts.scheme:
                    scheme = parentUrlParts.scheme
                else:
                    scheme = 'http'
            else:
                scheme = 'http'
        else:
            scheme = parts.scheme
        newLink = scheme + ":" + newLink
    return newLink


def isHttp(absoluteLink):
    return urllib.parse.urlparse(absoluteLink).scheme in ['http', 'https']


def validExtension(url):
    extensions = ['.jpg', '.jpeg', '.png', '.zip', '.doc', '.pdf']
    for extension in extensions:
        if url.endswith(extension):
            return False
    return True


def isInternalLink(link, absoluteUrlWithInitialDomain):
    initialDomain = getDomain(absoluteUrlWithInitialDomain)
    # FILTER ABSOLUTE URLs AND EXTERNAL URLs
    return isAbsolute(link) and getDomain(link) == initialDomain

if __name__ == '__main__':
    print(isAbsolute('//thewebminer.com'))
    print(isAbsolute('http://thewebminer.com'))
    print(isAbsolute('/thewebminer/'))