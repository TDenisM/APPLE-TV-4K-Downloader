import re
import os
import platform

class WvDownloaderConfig(object):
    def __init__(self, xml, base_url, output_file, format_id, bandwidth, cookies, file_type, tqdm_mode):
        self.xml = xml
        self.output_file = output_file
        self.base_url = base_url
        self.format_id = format_id
        self.bandwidth = bandwidth
        self.cookies = cookies
        self.file_type = file_type
        self.tqdm_mode = tqdm_mode
