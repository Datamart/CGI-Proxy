"""Simple HTTP Proxy.

See:
    https://google.github.io/styleguide/pyguide.html
    https://en.wikipedia.org/wiki/X-Forwarded-For
"""

import os.path
import platform
import socket
import sys

from datetime import datetime
from gzip import GzipFile
from io import BytesIO as StringIO
from os import environ

try:  # Python 2.x
    import urllib2
    from urlparse import parse_qs
    from urlparse import urlparse
    from urllib import urlencode
except ImportError:  # Python 3.x
    import urllib.request as urllib2
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
    from urllib.parse import urlencode


__version__ = '10.30'


def do_get(url, headers=None):
    """Performs GET request.

    Args:
        url: The request URL as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    headers = __get_request_headers(headers)
    return __get_content('GET', url, headers)


def do_post(url, data=None, headers=None):
    """Performs POST request. Converts query to POST params if data is None.

    Args:
        url: The request URL as string.
        data: Optional HTTP POST data as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    headers = __get_request_headers(headers)
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

    if data is None:
        urlobj = urlparse(url)
        data = urlencode(parse_qs(urlobj.query)).encode('utf-8')

    return __get_content('POST', url, headers, data)


def __error(message, error=None):
    """Prints error message to stderr.

    Args:
        message: The error message as string.
        error: Optional error object.
    """
    frame = sys._getframe(1)
    name = frame.f_globals['__name__']  # __name__
    func = frame.f_back.f_code.co_name
    today = datetime.now()
    sys.stderr.write('[%s] [%s] [%s.%s] %s\n' % (
        today, 'ERROR', name, func, message))

    if error:
        sys.stderr.write('[%s] [%s] [%s] %s\n' % (
            today, 'ERROR', error.__class__.__name__, error))


def __get_content(method, url, headers, data=None):
    """Gets a content, status code and response headers.

    Args:
        method: The HTTP method as string.
        url: The request URL as string.
        headers: The HTTP request headers as dict.
        data: Optional HTTP POST data as string.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    try:
        response = __do_request(method, url, headers, data)
    except urllib2.HTTPError as error:
        __error('Could not load URL: %s' % url, error)
        response = error
    except urllib2.URLError as error:
        __error('Could not load URL: %s' % url, error)
        response = None

    if response is not None:
        headers = response.info()
        headers = dict((key.lower(), value) for key, value in headers.items())
        status = response.getcode()
        content = __decode_content(response.read(), headers)
        response.close()
        return (content, status, headers)
    return ('', 500, None)


def __do_request(method, url, headers=None, data=None):
    """Gets a file-like object containing the data.

    Args:
        method: The HTTP method as string.
        url: The request URL as string.
        headers: Optional HTTP request headers as dict.
        data: Optional HTTP POST data as string.

    Returns:
        A file-like object containing the data.
    """
    if url[:5] == 'http:':
        handler = urllib2.HTTPHandler
    else:
        handler = urllib2.HTTPSHandler

    opener = urllib2.build_opener(handler)
    request = urllib2.Request(url, data=data)

    for header in headers:
        request.add_header(header, headers[header])

    request.get_method = lambda: '%s' % method
    return opener.open(request)


def __get_request_headers(headers=None):
    """Gets default HTTP request headers.

    Args:
        headers: Optional initial HTTP request headers as dict.

    Returns:
        A default HTTP request headers as dict.
    """
    if headers is None:
        headers = {}

    if 'Accept-Encoding' not in headers:
        headers['Accept-Encoding'] = 'gzip, deflate'

    if 'User-Agent' not in headers:
        headers['User-Agent'] = __get_user_agent()

    if 'X-Forwarded-For' not in headers:
        user_ip = __get_user_ip_address()
        host_ip = __get_host_ip_address()
        if user_ip and host_ip:
            headers['X-Forwarded-For'] = user_ip + ', ' + host_ip

    return headers


def __get_user_agent():
    """Gets HTTP user agent."""
    agent_name = os.path.basename(__file__).split('.')[0].capitalize()
    user_agent = 'Mozilla/5.0 (compatible; %s/%s) %s/%s' % (
        platform.system(), platform.release(), agent_name, __version__)

    return environ.get('HTTP_USER_AGENT') or user_agent


def __get_user_ip_address():
    """Gets user's IP address."""
    user_ip = environ.get('REMOTE_ADDR')
    x_proxy = environ.get('HTTP_X_FORWARDED_FOR')

    if x_proxy:
        user_ip = x_proxy.split(',')[0]

    return user_ip


def __get_host_ip_address():
    """Gets server' IP address."""
    host_ip = None

    try:
        host_ip = socket.gethostbyname(socket.gethostname())
    except Exception as error:
        __error('Could not get server IP address.', error)

    return host_ip


def __decode_content(content, headers):
    """Decodes content."""
    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
    encodings = headers.get('content-encoding', '').split(',')

    # If multiple encodings have been applied to an entity, the content
    # codings MUST be listed in the order in which they were applied.
    if 'gzip' in encodings:
        try:
            content = GzipFile(fileobj=StringIO(content)).read()
        except IOError:
            # pylint:disable=protected-access
            # Decompressing partial content by skipping checksum comparison.
            GzipFile._read_eof = lambda *args, **kwargs: None
            # pylint:enable=protected-access
            content = GzipFile(fileobj=StringIO(content)).read()
    # elif 'compress' in encodings: pass
    # elif 'deflate' in encodings: pass

    charset = __get_charset(headers)
    if charset is not None:
        content = content.decode(charset).encode('utf-8')

    return content.decode('utf-8')


def __get_charset(headers):
    """Gets response charset.

    Args:
        headers: The HTTP response headers as dict.

    Returns:
        A response charset or None.
    """
    content_type = headers.get('content-type')
    charset = None

    if content_type is not None:
        parts = content_type.split('charset=')
        if len(parts) == 2:
            charset = parts[-1]

    return charset


if __name__ == '__main__':
    # pylint:disable=superfluous-parens
    print(do_get('https://www.dtm.io'))
    print(__get_user_agent())
    print(__get_user_ip_address())
    print(__get_host_ip_address())
