
import threading
import os, re
import requests
import math
import urllib.parse
import urllib.request
import shutil
import isodate
import pathlib, sys, subprocess

from urllib.error import HTTPError
from m3u8 import parse as m3u8parser
from tqdm import tqdm
from queue import Queue

dlthreads = 24

class WvDownloader(object):
    def __init__(self, config):
        self.xml = config.xml
        self.output_file = config.output_file
        self.tqdm_mode = config.tqdm_mode
        self.cookies = config.cookies
        self.config = config

    def download_track(self, aria_input, file_name):
        aria_command = ['aria2c', '-i', aria_input,
         '--enable-color=false',
         '--allow-overwrite=true',
         '--summary-interval=0',
         '--download-result=hide',
         '--async-dns=false',
         '--check-certificate=false',
         '--auto-file-renaming=false',
         '--file-allocation=none',
         '--console-log-level=warn',
         '-x16', '-j16', '-s16']
        if sys.version_info >= (3, 5):
            aria_out = subprocess.run(aria_command)
            aria_out.check_returncode()
        else:
            aria_out = subprocess.call(aria_command)
            if aria_out != 0:
                raise ValueError('aria failed with exit code {}'.format(aria_out))
                
        source_files = pathlib.Path(temp_folder).rglob(r'./*.mp4')
        with open(file_name, mode='wb') as (destination):
            for file in source_files:
                with open(file, mode='rb') as (source):
                    shutil.copyfileobj(source, destination)
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.remove(aria_input)
        print('\nDone!')

    ## MPD
    def process_url_templace(self, template, representation_id, bandwidth, time, number):
        if representation_id is not None: result = template.replace('$RepresentationID$', representation_id)
        if number is not None:
            nstart = result.find('$Number')
            if nstart >= 0:
                nend = result.find('$', nstart+1)
                if nend >= 0:
                    var = result[nstart+1 : nend]
                    if 'Number%' in var:
                        value = var[6:] % (int(number))
                    else:
                        value = number
                    result = result.replace('$'+var+'$', value)
        if bandwidth is not None:         result = result.replace('$Bandwidth$', bandwidth)
        if time is not None:              result = result.replace('$Time$', time)
        result = result.replace('$$', '$').replace('../', '')
        return result

    def generate_segments(self):
        segs = self.get_representation_number()
        if "$Time$" in segs.get('@media'):
            return self.alt_get_segments(segs)
        else:
            return self.get_segments(segs)

    def get_init_and_info(self):
        init_lv = self.get_representation_number()
        # get init segment url
        init = init_lv['@initialization']
        init = self.process_url_templace(init, representation_id=self.config.format_id, bandwidth=self.config.bandwidth, time=None, number=None)
        return init

    def get_segments(self, segment_level):
        try:
            media = segment_level['@media']
            current_number = 1
            current_time = 0
            for seg in segment_level['SegmentTimeline']['S']:
                if '@t' in seg:
                    current_time = seg['@t']
                for _ in range(int(seg.get('@r', 0)) + 1):
                    url = self.process_url_templace(media, representation_id=self.config.format_id, bandwidth=self.config.bandwidth, time=str(current_time), number=str(current_number))
                    current_number += 1
                    current_time += seg['@d']
                    yield url

        except KeyError:
            current_number = int(segment_level.get("@startNumber", 0))
            period_duration = self.get_duration()
            segment_duration = int(segment_level["@duration"]) / int(segment_level["@timescale"])
            total_segments = math.ceil(period_duration / segment_duration)
            media = segment_level['@media']
            for _ in range(current_number, current_number + total_segments):
                url = self.process_url_templace(media, representation_id=self.config.format_id, bandwidth=self.config.bandwidth, time="0", number=str(current_number))
                current_number += 1
                yield url
    
    def get_duration(self):
        media_duration = self.xml["MPD"]["@mediaPresentationDuration"]
        return isodate.parse_duration(media_duration).total_seconds()

    def alt_get_segments(self, segment_level):
        media = segment_level['@media']
        t = 0
        if isinstance(segment_level['SegmentTimeline']['S'], list):
            segment_level = segment_level['SegmentTimeline']['S']
        else:
            segment_level = [segment_level['SegmentTimeline']['S']]

        for seg in segment_level:
            if '@t' in seg:
                t = int(seg['@t'])
            for _ in range(int(seg.get('@r', 0)) + 1):
                url = self.process_url_templace(media, representation_id=self.config.format_id, bandwidth=self.config.bandwidth, time=str(t), number=None)
                t += int(seg['@d'])
                yield url

    def get_representation_number(self):
        x = []
        for [idx, item] in enumerate(self.xml['MPD']['Period']['AdaptationSet']):
            try:
                if self.config.file_type in item.get('@mimeType'):
                    x = idx
            except TypeError:
                if self.config.file_type in item.get('@contentType'):
                    x = idx

        y = []
        if 'video' in self.config.file_type: 
            for [number, rep] in enumerate(self.xml['MPD']['Period']['AdaptationSet'][x]['Representation']):
                if self.config.format_id == rep.get('@id'):
                    y = number

        mpd = self.xml['MPD']['Period']
        try:
            if 'video' in self.config.file_type:
                stream_index = mpd['AdaptationSet'][x]['Representation'][y]
            else:
                stream_index = mpd['AdaptationSet'][x]['Representation']
            
            segment_level = stream_index['SegmentTemplate']

        except KeyError:
            segment_level = mpd['AdaptationSet'][x]['SegmentTemplate']

        return segment_level

    def open_url(self, url):
        return urllib.request.urlopen(url), url
    
    ## M3U8
    def get_m3u8_segments(self):
        base_url = re.split('(/)(?i)', self.xml)
        del base_url[-1]
        base_url = ''.join(base_url)
        m3u8_request = requests.get(self.xml).text
        m3u8_json = m3u8parser(m3u8_request)
        segment_urls = []
        
        for segment in m3u8_json['segments']:
            if 'https://' not in segment['uri']:
                segment_url = base_url + segment['uri']
            segment_urls.append(segment_url)

        seg_url = list(filter(lambda k: 'MAIN' in k, segment_urls))
        init_url = seg_url[0].replace('00/00/00_000', 'map')
        segment_urls = []
        segment_urls = [init_url] + seg_url

        return segment_urls

    def run(self):
        if 'm3u8' in self.xml:
            urls = self.get_m3u8_segments()
        if 'MPD' in self.xml:
            segment_list = self.generate_segments()
            init = self.get_init_and_info()
            urls = []
            url = self.config.base_url + '/' + init
            urls.append(url)
            for seg_url in segment_list:
                url = self.config.base_url + '/' + seg_url
                urls.append(url)

        print('\n' + self.output_file) 
        # download por aria2c
        if not self.tqdm_mode:
            global temp_folder
            aria2c_infile = 'aria2c_infile.txt'
            if os.path.isfile(aria2c_infile): 
                os.remove(aria2c_infile)
            temp_folder = self.output_file.replace('.mp4', '')
            if os.path.exists(temp_folder): 
                shutil.rmtree(temp_folder)
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)

            if len(urls) > 1:
                num_segments = int(math.log10(len(urls))) + 1
            with open(aria2c_infile, 'a', encoding='utf8') as (file):
                for (i, url) in enumerate(urls[:-1]):
                    file.write(f'{url}\n')
                    file.write(f'\tout={temp_folder}.{i:0{num_segments}d}.mp4\n')
                    file.write(f'\tdir={temp_folder}\n')
                    file.flush()
            self.download_track(aria2c_infile, self.output_file)
        else:
            # download por thread
            work_q = Queue()
            result_q = Queue()

            pool = [WorkerThread(work_q=work_q, result_q=result_q, cookies=self.cookies) for i in range(dlthreads)]
            for thread in pool:
                thread.start()

            work_count = 0
            for seg_url in urls:
                url = seg_url
                work_q.put((work_count, url, self.cookies))
                work_count += 1
            results = []
            
            for _ in tqdm(range(work_count)):
                results.append(result_q.get())
            outfile = open(self.output_file , 'wb+')
            sortedr = sorted(results, key=lambda v: v[0])
            for r in sortedr:
                outfile.write(r[1])
            outfile.close()
            del results
            print('Done!')

class Downloader:
    def __init__(self):
        self.session = requests.Session()

    def DownloadSegment(self, url, cookies):
        resp = self.session.get(url, cookies=cookies, stream=True)
        resp.raw.decode_content = True
        data = resp.raw.read()
        return data

class WorkerThread(threading.Thread):
    def __init__(self, work_q, result_q, cookies):
        super(WorkerThread, self).__init__()
        self.work_q = work_q
        self.result_q = result_q
        self.cookies = cookies
        self.stoprequest = threading.Event()
        self.downloader = Downloader()

    def run(self):
        while not self.stoprequest.isSet():
            try:
                (seq, url, cookies) = self.work_q.get(True, 0.05)
                self.result_q.put((seq, self.downloader.DownloadSegment(url, cookies)))
            except:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(WorkerThread, self).join(timeout)
