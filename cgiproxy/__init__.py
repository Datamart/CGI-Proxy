"""Simple HTTP Proxy.

See:
    https://google.github.io/styleguide/pyguide.html
    https://en.wikipedia.org/wiki/X-Forwarded-For
"""

import os
import platform
import socket
import sys

from datetime import datetime
from gzip import GzipFile
from io import BytesIO as StringIO

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


__version__ = '20.11.14'


def do_get(url, headers=None):
    """Performs GET request.

    Args:
        url: The request URL as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    headers = _get_request_headers(headers)
    return _get_content('GET', url, headers)


def do_post(url, data=None, headers=None):
    """Performs POST request. Converts query to POST params if data is None.

    Args:
        url: The request URL as string.
        data: Optional HTTP POST data as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    headers = _get_request_headers(headers)
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

    if data is None:
        urlobj = urlparse(url)
        data = urlencode(parse_qs(urlobj.query)).encode('utf-8')

    return _get_content('POST', url, headers, data)


def do_head(url, headers=None):
    """Performs HEAD request.

    Args:
        url: The request URL as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    headers = _get_request_headers(headers)
    return _get_content('HEAD', url, headers)


def get_http_status(url, headers=None):
    """Gets HTTP status code.

    Args:
        url: The request URL as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        An HTTP status code.
    """
    _, status, response_headers = do_head(url, headers)
    redirect = response_headers.get('location')

    if redirect:
        return get_http_status(redirect, headers)
    return status


def get_response_headers(url, headers=None):
    """Gets HTTP response headers.

    Args:
        url: The request URL as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        An HTTP response headers as dict.
    """
    response_headers = do_head(url, headers)[-1]
    return response_headers


def _error(message, error=None):
    """Prints error message to stderr.

    Args:
        message: The error message as string.
        error: Optional error object.
    """
    # pylint:disable=consider-using-f-string
    # pylint:disable=protected-access
    frame = sys._getframe(1)
    name = frame.f_globals['__name__']  # __name__
    func = frame.f_back.f_code.co_name
    today = datetime.now()
    sys.stderr.write('[%s] [%s] [%s.%s] %s\n' % (
        today, 'ERROR', name, func, message))
    # pylint:enable=protected-access

    if error:
        sys.stderr.write('[%s] [%s] [%s] %s\n' % (
            today, 'ERROR', error.__class__.__name__, error))
    # pylint:enable=consider-using-f-string


def _get_content(method, url, headers, data=None):
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
        response = _do_request(method, url, headers, data)
    except urllib2.HTTPError as error:
        _error('Could not load URL: %s' % url, error)
        response = error
    except urllib2.URLError as error:
        _error('Could not load URL: %s' % url, error)
        response = None

    if response is not None:
        headers = response.info()
        # headers = dict((key.lower(), value) for key, value in headers.items())
        headers = {key.lower(): value for key, value in headers.items()}
        status = response.getcode()
        content = _decode_content(response.read(), headers)
        response.close()
        return (content, status, headers)
    return ('', 500, None)


def _do_request(method, url, headers=None, data=None):
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


def _get_request_headers(headers=None):
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
        headers['User-Agent'] = _get_user_agent()

    if 'X-Forwarded-For' not in headers:
        user_ip = _get_user_ip_address()
        host_ip = _get_host_ip_address()
        if user_ip and host_ip:
            headers['X-Forwarded-For'] = user_ip + ', ' + host_ip

    return headers


def _get_user_agent():
    """Gets HTTP user agent."""
    module = os.path.basename(__file__).split('.')[0]
    if module == '__init__':
        module = os.path.dirname(os.path.abspath(__file__)).split(os.sep)[-1]

    user_agent = 'Mozilla/5.0 (compatible; %s/%s) %s/%s' % (
        platform.system(), platform.release(), module, __version__)

    return os.environ.get('HTTP_USER_AGENT') or user_agent


def _get_user_ip_address():
    """Gets user's IP address."""
    user_ip = os.environ.get('REMOTE_ADDR')
    x_proxy = os.environ.get('HTTP_X_FORWARDED_FOR')

    if x_proxy:
        user_ip = x_proxy.split(',')[0]

    return user_ip


def _get_host_ip_address():
    """Gets server' IP address."""
    # pylint:disable=broad-except
    host_ip = None

    try:
        host_ip = socket.gethostbyname(socket.gethostname())
    except Exception as error:
        _error('Could not get server IP address.', error)

    # pylint:enable=broad-except
    return host_ip


def _decode_content(content, headers):
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

    charset = _get_charset(headers)
    if charset is not None:
        try:
            content = content.decode(charset).encode('utf-8')
        except UnicodeDecodeError as ex:  # pylint: disable=unused-variable
            pass

    return content.decode('utf-8')


def _get_charset(headers):
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
