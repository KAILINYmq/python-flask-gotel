import base64
import time
import hashlib
import datetime

import requests
from requests.auth import HTTPBasicAuth
from multiprocessing import Process, Queue


class IpZoo:
    def __init__(self, proxy_type='vip', protocol='fast'):
        assert proxy_type in ['normal', 'fast', 'vip', 'china', 'oversee']
        host = "http://proxy.57km.cc"
        self.url = f'{host}/api/proxy/{proxy_type}'
        self.queue = Queue()
        self.protocol = protocol
        self.refresh_pool()

    def refresh_pool(self):
        rsp = requests.get(self.url, auth=HTTPBasicAuth('cmi', '123456'))
        for each in rsp.json():
            if each['type'] == 'all' or each['type'] == self.protocol:
                self.queue.put_nowait(each['addr'])

    def pop(self):
        if self.queue.empty():
            self.refresh_pool()
        return self.queue.get(timeout=5)
