
config = {
    'proxies': {
        'none': None
    },
}

class ProxyConfig(object):
    def __init__(self, proxies):
        self.config = config
        self.config['proxies'] = proxies

    def get_proxy(self, proxy):
        return self.config['proxies'].get(proxy)

