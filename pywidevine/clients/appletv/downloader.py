

import sys, os, shutil, requests, re
import subprocess, math, pathlib

from m3u8 import parse as m3u8parser

dlthreads = 24

class WvDownloader(object):
    def __init__(self, config):
        self.m3u8_url = config.m3u8
        self.output_file = config.output_file
        self.config = config

    def downloadM3u8(self, Link_List, Folder, file_name):
        TempFolder = file_name.replace('.mp4', '')
        if os.path.exists(TempFolder):
            shutil.rmtree(TempFolder)
        if not os.path.exists(TempFolder):
            os.makedirs(TempFolder)
        LinkList_txt = file_name.replace('.mp4', '_LinkList.txt')
        if os.path.isfile(LinkList_txt):
            os.remove(LinkList_txt)

        counter = 0
        with open(LinkList_txt, 'a', encoding='ansi') as (file):
            for link in Link_List:
                mp4_segment = re.split('(/)(?i)', link)[(-1)]
                seg_num = str(counter).zfill(5)
                seg_num = f"{seg_num}.mp4"
                file.write(f"{link}\n\tdir={TempFolder}\n\tout={seg_num}\n")
                counter = counter + 1

        aria_command = [
         'aria2c', '-i', LinkList_txt,
         '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"',
         '--async-dns=false',
         '--enable-color=false',
         '--allow-overwrite=true',
         '--download-result=hide',
         '--auto-file-renaming=false',
         '--file-allocation=none',
         '--summary-interval=0',
         '--retry-wait=5',
         '--uri-selector=inorder',
         '--console-log-level=warn',
         '-x16', '-j16', '-s16']
        if sys.version_info >= (3, 5):
            aria_out = subprocess.run(aria_command)
            aria_out.check_returncode()
            if os.path.isfile(LinkList_txt):
                os.remove(LinkList_txt)
            source_files = pathlib.Path(TempFolder).rglob('./*.mp4')
            with open(file_name, mode='wb') as (destination):
                for file in source_files:
                    with open(file, mode='rb') as (source):
                        shutil.copyfileobj(source, destination)

            if os.path.exists(TempFolder):
                shutil.rmtree(TempFolder)

        if os.path.exists(TempFolder):
            shutil.rmtree(TempFolder)


    
    def get_intro_m3u8(self):
        m3u8_json = m3u8parser(requests.get(self.m3u8_url).text)
        url_dict_list = []
        init_url_list = []

        for segment in m3u8_json['segments']:
            if not 'key' in segment:
                init_url_list.append(segment['init_section']['uri'])

        for init_mp4 in init_url_list:
            url_list = []
            
            for segment in m3u8_json['segments']:
                if not 'key' in segment:
                    init_id = 'INTRO'
                    url_list.append(init_mp4)
                    url_list.append(segment['uri'])
        
        url_dict_list.append({'id':init_id, 'url_list':url_list})

        return url_dict_list

    def get_segs_m3u8(self):
        m3u8_json = m3u8parser(requests.get(self.m3u8_url).text)
        url_dict_list = []
        init_url_list = []
        for segment in m3u8_json['segments']:
            if 'key' in segment:
                init_url_list.append(segment['init_section']['uri'])

        for init_mp4 in init_url_list:
            url_list = []
            
            for segment in m3u8_json['segments']:
                if 'key' in segment:
                    url_list.append(segment['init_section']['uri'])

        init = list(url_list)[0]
        seg_list = []
        for segment in m3u8_json['segments']:
            if init == segment['init_section']['uri']:
                init_id = 'MAIN'
                seg_list.append(segment['uri'])
        seg_list = [init] + seg_list
        
        url_dict_list.append({'id':init_id, 'url_list':seg_list})


        return url_dict_list

    def get_decon_m3u8(self):
        m3u8_json = m3u8parser(requests.get(self.m3u8_url).text)
        url_dict_list = []
        init_url_list = []
        for segment in m3u8_json['segments']:
            if 'key' in segment:
                init_url_list.append(segment['init_section']['uri'])

        for init_mp4 in init_url_list:
            url_list = []
            
            for segment in m3u8_json['segments']:
                if 'key' in segment:
                    url_list.append(segment['init_section']['uri'])

        init = list(url_list)[-1]
        seg_list = []
        for segment in m3u8_json['segments']:
            if init == segment['init_section']['uri']:
                init_id = 'EXTRAS'
                seg_list.append(segment['uri'])
        seg_list = [init] + seg_list
        
        url_dict_list.append({'id':init_id, 'url_list':seg_list})

        return url_dict_list

    def run(self):
        segment_list = []
        segment_list = self.get_segs_m3u8()
        print('\n' + self.output_file) 
        global temp_folder
        aria2c_infile = 'aria2c_infile.txt'
        if os.path.isfile(aria2c_infile): 
            os.remove(aria2c_infile)

        temp_folder = self.output_file.replace('.mp4', '')
        counter = 0
        for url_dic in segment_list:
            url_id = url_dic['id']
            count_id = str(counter).zfill(4)
            fileName = temp_folder + f'_{count_id}_{url_id}.mp4'
            self.downloadM3u8(Link_List=url_dic['url_list'], Folder=temp_folder, file_name=fileName)
            counter = counter + 1
        return segment_list
