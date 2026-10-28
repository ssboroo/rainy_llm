import io
import json
import unittest
import urllib.error
from unittest.mock import patch
from scripts import collect_wikipedia as wiki

class Response(io.BytesIO):
    def __init__(self, data, headers=None):
        super().__init__(json.dumps(data).encode())
        self.headers = headers or {}

class RequestTests(unittest.TestCase):
    @patch.object(wiki.time, 'sleep')
    def test_maxlag_retry_and_parameter(self, sleep):
        with patch.object(wiki.urllib.request,'urlopen', side_effect=[
            Response({'error':{'code':'maxlag'}},{'Retry-After':'7'}),
            Response({'query':{}})]) as urlopen:
            self.assertEqual(wiki.request({'action':'query'}), {'query':{}})
            self.assertIn('maxlag=5',urlopen.call_args.args[0].full_url)
            sleep.assert_any_call(7.0)
    @patch.object(wiki.time, 'sleep')
    def test_http_429_retry(self, sleep):
        error=urllib.error.HTTPError('url',429,'busy',{'Retry-After':'8'},None)
        with patch.object(wiki.urllib.request,'urlopen',side_effect=[error,Response({'ok':True})]):
            self.assertTrue(wiki.request({'action':'query'})['ok'])
            sleep.assert_any_call(8.0)
    @patch.object(wiki.time, 'sleep')
    def test_bounded_retries_and_long_server_pause(self, sleep):
        with patch.object(wiki.urllib.request,'urlopen',side_effect=urllib.error.URLError('offline')) as call:
            with self.assertRaises(RuntimeError):
                wiki.request({'action':'query'})
            self.assertEqual(call.call_count,4)
        with patch.object(wiki.urllib.request,'urlopen',return_value=Response({'error':{'code':'maxlag'}},{'Retry-After':'600'})) as call:
            with self.assertRaises(RuntimeError):
                wiki.request({'action':'query'})
            self.assertEqual(call.call_count,1)
    @patch.object(wiki.time, 'sleep')
    def test_permanent_error_not_retried(self, sleep):
        with patch.object(wiki.urllib.request,'urlopen',return_value=Response({'error':{'code':'badvalue'}})) as call:
            with self.assertRaises(ValueError):
                wiki.request({'action':'query'})
            self.assertEqual(call.call_count,1)

