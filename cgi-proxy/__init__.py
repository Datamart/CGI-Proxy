"""Simple CGI HTTP Proxy.

See:
    https://google.github.io/styleguide/pyguide.html
    https://en.wikipedia.org/wiki/X-Forwarded-For
"""

import cgiproxy


__version__ = cgiproxy.__version__


def do_get(url, headers=None):
    """Deprecated. Performs GET request.

    Args:
        url: The request URL as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    return cgiproxy.do_get(url, headers=headers)


def do_post(url, data=None, headers=None):
    """Deprecated. Performs POST request. Converts query to POST params if data is None.

    Args:
        url: The request URL as string.
        data: Optional HTTP POST data as string.
        headers: Optional HTTP request headers as dict.

    Returns:
        A tuple of (content, status_code, response_headers)
    """
    return cgiproxy.do_get(url, data=data, headers=headers)
