import os
import sys
import unittest

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(cwd, '..')))

from cgiproxy import (_get_host_ip_address, _get_user_agent,
                      _get_user_ip_address, do_get, do_head, get_http_status,
                      get_response_headers)  # noqa: E402


class TestProxy(unittest.TestCase):
    """Unittest test case."""
    TEST_URL = 'https://komito.net/'
    PRINT_OUTPUT = False

    def test_get_http_status(self):
        """Tests 'get_http_status' method."""
        status = get_http_status(self.TEST_URL)
        self.assertEqual(200, status)
        if self.PRINT_OUTPUT:
            print('get_http_status: %s' % status)

    def test_get_response_headers(self):
        """Tests 'get_response_headers' method."""
        headers = get_response_headers(self.TEST_URL)
        self.assertEqual(dict, type(headers))
        if self.PRINT_OUTPUT:
            print('get_response_headers: %s' % str(headers))

    def test_do_head(self):
        """Tests 'do_head' method."""
        content, status, headers = do_head(self.TEST_URL)
        self.assertEqual('', content)
        self.assertEqual(int, type(status))
        self.assertEqual(dict, type(headers))
        if self.PRINT_OUTPUT:
            print('do_head: %s' % str((content, status, headers)))

    def test_do_get(self):
        """Tests 'do_get' method."""
        content, status, headers = do_get(self.TEST_URL)
        self.assertNotEqual('', content)
        self.assertEqual(int, type(status))
        self.assertGreaterEqual(status, 200)
        self.assertEqual(dict, type(headers))

    def test_get_user_agent(self):
        """Tests '_get_user_agent' method."""
        user_agent = _get_user_agent()
        self.assertNotEqual('', user_agent)
        if self.PRINT_OUTPUT:
            print('_get_user_agent: %s' % user_agent)

    def test_get_user_ip_address(self):
        """Tests '_get_user_ip_address' method."""
        ip_address = _get_user_ip_address()
        self.assertNotEqual('', ip_address)
        if self.PRINT_OUTPUT:
            print('_get_user_ip_address: %s' % ip_address)

    def test_get_host_ip_address(self):
        """Tests '_get_host_ip_address' method."""
        ip_address = _get_host_ip_address()
        self.assertNotEqual('', ip_address)
        if self.PRINT_OUTPUT:
            print('_get_host_ip_address: %s' % ip_address)


if __name__ == '__main__':
    unittest.main()
