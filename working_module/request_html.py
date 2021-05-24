
import urllib.parse
import urllib.request
import logging


def request_page(url:str):
    try:
        req = urllib.request.Request(url)
        req.add_header("Cache-Control", "no-cache")
        req.add_header("Pragma", "no-cache")
        req.add_header("Expires", "01 Jan 1970 00:00:00 GMT")
        req.add_header('User-Agent', 'Mozilla/5.0')
        content = urllib.request.urlopen(req).read().decode()
        return content
    except Exception as e:
        logging.warning(f"request_page() failed to retrieve website")
        logging.warning(e)
        return ''

if __name__ == '__main__':
    print(request_page('http://127.0.0.1:8080'))
    print(request_page('https://raw.githubusercontent.com/Machine-builder/py-authentication/main/identifiers_ec.ids'))