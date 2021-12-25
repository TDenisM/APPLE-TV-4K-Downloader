# -*- coding: utf-8 -*-
# Module: AppleTV+ Downloader
# Created on: 20-12-2020
# Authors: JUNi
# Version: 1.0

import sys, os, time
import urllib.parse
import re, io, base64, requests, math
import subprocess, pathlib, glob
import ffmpy, json, html, http
import shutil

from unidecode import unidecode
from m3u8 import parse as m3u8parser
from os.path import isfile, join

import pywidevine.clients.appletv.client as APTVCLient
import pywidevine.clients.appletv.config as APTVConfig

from pywidevine.clients.appletv.downloader import WvDownloader
from pywidevine.clients.appletv.config import WvDownloaderConfig
from pywidevine.muxer.muxer import Muxer

currentFile = 'appletv'
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
session = requests.Session()

def main(args):

    if not os.path.exists(dirPath + '/KEYS'):
        os.makedirs(dirPath + '/KEYS')
    else:
        keys_file = dirPath + '/KEYS/APPLETVPLUS.txt'
        try:
            keys_file_apple = open(keys_file, 'r', encoding='utf8')
            keys_file_txt = keys_file_apple.readlines()
        except Exception:
            with open(keys_file, 'a', encoding='utf8') as (file):
                file.write('##### One KEY per line. #####\n')
            keys_file_apple = open(keys_file, 'r', encoding='utf8')
            keys_file_txt = keys_file_apple.readlines()

    def replace_words(x):
        x = re.sub(r'[]¡!"#$%\'()*+,:;<=>¿?@\\^_`{|}~[-]', '', x)
        x = x.replace('\\', '').replace('/', ' & ')
        return unidecode(x)

    def ReplaceCodeLanguages(X):
        X = X.lower()
        X = X.replace('_subtitle_dialog_0', '').replace('_narrative_dialog_0', '').replace('_caption_dialog_0', '').replace('_dialog_0', '').replace('_descriptive_0', '_descriptive').replace('_descriptive', '_descriptive').replace('_sdh', '-sdh').replace('es-es', 'es').replace('en-es', 'es').replace('kn-in', 'kn').replace('gu-in', 'gu').replace('ja-jp', 'ja').replace('mni-in', 'mni').replace('si-in', 'si').replace('as-in', 'as').replace('ml-in', 'ml').replace('sv-se', 'sv').replace('hy-hy', 'hy').replace('sv-sv', 'sv').replace('da-da', 'da').replace('fi-fi', 'fi').replace('nb-nb', 'nb').replace('is-is', 'is').replace('uk-uk', 'uk').replace('hu-hu', 'hu').replace('bg-bg', 'bg').replace('hr-hr', 'hr').replace('lt-lt', 'lt').replace('et-et', 'et').replace('el-el', 'el').replace('he-he', 'he').replace('ar-ar', 'ar').replace('fa-fa', 'fa').replace('ro-ro', 'ro').replace('sr-sr', 'sr').replace('cs-cs', 'cs').replace('sk-sk', 'sk').replace('mk-mk', 'mk').replace('hi-hi', 'hi').replace('bn-bn', 'bn').replace('ur-ur', 'ur').replace('pa-pa', 'pa').replace('ta-ta', 'ta').replace('te-te', 'te').replace('mr-mr', 'mr').replace('kn-kn', 'kn').replace('gu-gu', 'gu').replace('ml-ml', 'ml').replace('si-si', 'si').replace('as-as', 'as').replace('mni-mni', 'mni').replace('tl-tl', 'tl').replace('id-id', 'id').replace('ms-ms', 'ms').replace('vi-vi', 'vi').replace('th-th', 'th').replace('km-km', 'km').replace('ko-ko', 'ko').replace('zh-zh', 'zh').replace('ja-ja', 'ja').replace('ru-ru', 'ru').replace('tr-tr', 'tr').replace('it-it', 'it').replace('es-mx', 'es-la').replace('ar-sa', 'ar').replace('zh-cn', 'zh').replace('nl-nl', 'nl').replace('pl-pl', 'pl').replace('pt-pt', 'pt').replace('hi-in', 'hi').replace('mr-in', 'mr').replace('bn-in', 'bn').replace('te-in', 'te').replace('cmn-hans', 'zh-hans').replace('cmn-hant', 'zh-hant').replace('ko-kr', 'ko').replace('en-au', 'en').replace('es-419', 'es-la').replace('es-us', 'es-la').replace('en-us', 'en').replace('en-gb', 'en').replace('fr-fr', 'fr').replace('de-de', 'de').replace('las-419', 'es-la').replace('ar-ae', 'ar').replace('da-dk', 'da').replace('yue-hant', 'yue').replace('bn-in', 'bn').replace('ur-in', 'ur').replace('ta-in', 'ta').replace('sl-si', 'sl').replace('cs-cz', 'cs').replace('hi-jp', 'hi').replace('-001', '').replace('en-US', 'en').replace('deu', 'de').replace('eng', 'en').replace('ca-es', 'cat').replace('fil-ph', 'fil').replace('en-ca', 'en').replace('eu-es', 'eu').replace('ar-eg', 'ar').replace('he-il', 'he').replace('el-gr', 'he').replace('nb-no', 'nb').replace('es-ar', 'es-la').replace('en-ph', 'en').replace('sq-al', 'sq').replace('bs-ba', 'bs').replace('pt-BR', 'pt-br')
        return X

    def ReplaceSubs1(X):
        pattern1 = re.compile('(?!<i>|<b>|<u>|<\\/i>|<\\/b>|<\\/u>)(<)(?:[A-Za-z0-9_ -=]*)(>)')
        pattern2 = re.compile('(?!<\\/i>|<\\/b>|<\\/u>)(<\\/)(?:[A-Za-z0-9_ -=]*)(>)')
        X = X.replace('&rlm;', '').replace('{\\an1}', '').replace('{\\an2}', '').replace('{\\an3}', '').replace('{\\an4}', '').replace('{\\an5}', '').replace('{\\an6}', '').replace('{\\an7}', '').replace('{\\an8}', '').replace('{\\an9}', '').replace('&lrm;', '')
        X = pattern1.sub('', X)
        X = pattern2.sub('', X)
        return X

    def mediainfo_(file):
        mediainfo_output = subprocess.Popen([APTVConfig.MEDIAINFO, '--Output=JSON', '-f', file], stdout=(subprocess.PIPE))
        mediainfo_json = json.load(mediainfo_output.stdout)
        return mediainfo_json

    def alphanumericSort(l):
        def convert(text):
            if text.isdigit():
                return int(text)
            else:
                return text

        def alphanum_key(key):
            return [convert(c) for c in re.split('([0-9]+)', key)]

        return sorted(l, key=alphanum_key)

    def convert_size(size_bytes):
        if size_bytes == 0:
            return '0bps'
        else:
            s = round(size_bytes / 1000, 0)
            return '%ikbps' % s

    def get_size(size):
        power = 1024
        n = 0
        Dic_powerN = {0:'',  1:'K',  2:'M',  3:'G',  4:'T'}
        while size > power:
            size /= power
            n += 1
        return str(round(size, 2)) + Dic_powerN[n] + 'B'

    def getKeyId(name):
        mp4dump = subprocess.Popen([APTVConfig.MP4DUMP, name], stdout=(subprocess.PIPE))
        mp4dump = str(mp4dump.stdout.read())
        A = find_str(mp4dump, 'default_KID')
        KEY_ID_ORI = ''
        KEY_ID_ORI = mp4dump[A:A + 63].replace('default_KID = ', '').replace('[', '').replace(']', '').replace(' ', '')
        if KEY_ID_ORI == '' or KEY_ID_ORI == "'":
            KEY_ID_ORI = 'nothing'
        return KEY_ID_ORI

    def find_str(s, char):
        index = 0
        if char in s:
            c = char[0]
            for ch in s:
                if ch == c:
                    if s[index:index + len(char)] == char:
                        return index
                index += 1

        return -1

    AUTH_HEADERS, COOKIES = APTVCLient.get_auth_headers(args.url_season)

    def get_pssh(x):
        urlm3u8_request = requests.get(x).text
        m3u8_json = m3u8parser(urlm3u8_request)

        pssh = ''
        for typekey in m3u8_json['keys']:
            try:
                if typekey['keyformat'] == 'urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed':
                    pssh = typekey['uri'].replace('data:text/plain;base64,', '')
            except Exception:
                continue
        return pssh

    def download_subs(filename, sub_url):
        m3u8_json = m3u8parser(requests.get(sub_url).text)

        urls = []
        for segment in m3u8_json['segments']:
            urls.append(segment['uri'])

        print('\n' + filename)
        aria2c_infile = ""
        num_segments = len(urls)
        digits = math.floor(math.log10(num_segments)) + 1
        for (i, url) in enumerate(urls):
            aria2c_infile += f"{url}\n"
            aria2c_infile += f"\tout={filename}.{i:0{digits}d}.webvtt\n"
            aria2c_infile += f"\tdir={filename}\n"
        subprocess.run([APTVConfig.ARIA2C, "--allow-overwrite=true", "-q", "--file-allocation=none",
                        "--console-log-level=warn", "--download-result=hide", "--summary-interval=0",
                        "-x16", "-j16", "-s1", "-i-"],
                    input=aria2c_infile.encode("utf-8"))

        source_files = pathlib.Path(filename).rglob(r'./*.webvtt')
        with open(filename + '.webvtt', mode='wb') as (destination):
            for vtt in source_files:
                with open(vtt, mode='rb') as (source):
                    shutil.copyfileobj(source, destination)

        if os.path.exists(filename):
            shutil.rmtree(filename)
        
        print('Converting subtitles...')
        for f in glob.glob(f'{filename}*.webvtt'):
            with open(f, 'r+', encoding='utf-8-sig') as (x):
                old = x.read().replace('STYLE\n::cue() {\nfont-family: Arial, Helvetica, sans-serif;\n}', '').replace('WEBVTT', '').replace('X-TIMESTAMP-MAP=LOCAL:00:00:00.000,MPEGTS:9000', '').replace('X-TIMESTAMP-MAP=MPEGTS:900000,LOCAL:00:00:00.000', '').replace('\n\n\n', '\n')
            with open(f, 'w+', encoding='utf-8-sig') as (x):
                    x.write(ReplaceSubs1(old))
        SubtitleEdit_process = subprocess.Popen([APTVConfig.SUBTITLE_EDIT, '/convert', filename + ".webvtt", "srt"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        for f in glob.glob(f'{filename}*.webvtt'):
            os.remove(f)

        print('Done!')

    def m3u8_parsing(m3u8_url):
        master_base_url = re.split('(/)(?i)', m3u8_url)
        del master_base_url[-1]
        master_base_url = ''.join(master_base_url)
        urlm3u8_master_request = requests.get(m3u8_url, headers=AUTH_HEADERS["wvHeaders"]).text
        m3u8_master_json = m3u8parser(urlm3u8_master_request)
        audio_List = []
        audio_dict = {}
        subs_list = []
        for media in m3u8_master_json['media']:
            if media['type'] == 'AUDIO':
                isAD = False
                try:
                    if 'public.accessibility.' in media['characteristics']:
                        isAD = True
                except Exception:
                    isAD = False

                group_id = media['group_id'].replace('HE-stereo', 'aac').replace('stereo', 'aac')

                m = re.search(r"&g=(.+?)&", media['uri'])
                mx = re.search(r"audio-(.+?)(-|_)", group_id)
                Bitrate = m[1]
                Codec = mx[1]

                if int(Bitrate) > 2000:
                    Bitrate = Bitrate[1:]

                if isAD:
                    LanguageID = ReplaceCodeLanguages(media['language']) + '-ad'
                else:
                    LanguageID = ReplaceCodeLanguages(media['language'])

                if isAD:
                    trackType = 'NARRATION'
                else:
                    trackType = 'PRIMARY'

                if 'https://' not in media['uri']:
                    full_url = master_base_url + media['uri']
                    Full_URL_Type = False

                else:
                    full_url = media['uri']
                    Full_URL_Type = True

                audio_dict = {
                    'trackType':trackType, 
                    'Language':media['name'], 
                    'LanguageID':LanguageID, 
                    'Profile':group_id, 
                    'Codec':Codec, 
                    'Channels':media['channels'].replace('"', '').replace('/JOC', ''), 
                    'isAD':isAD, 
                    'url':full_url, 
                    'Bitrate':Bitrate}
                if args.audiocodec:
                    if audio_dict['Codec'] == str(args.audiocodec):
                        if '-ap' in audio_dict['Profile']:
                            audio_List.append(audio_dict)
                else:
                    audio_List.append(audio_dict)
            if media['type'] == 'SUBTITLES':
                isCC = False
                try:
                    if 'public.accessibility.' in media['characteristics']:
                        isCC = True
                except Exception:
                    isCC = False

                if '_NORMAL_' in media['uri']:
                    isCC = False
                isNormal = False
                if isCC:
                    LanguageID = ReplaceCodeLanguages(media['language']) + '-sdh'
                    trackType = 'SDH'
                else:
                    trackType = 'NORMAL'
                    isNormal = True
                    LanguageID = ReplaceCodeLanguages(media['language'])
                isForced = False
                if media['forced'] == 'YES':
                    isForced = True
                    isNormal = False
                    trackType = 'FORCED'
                    media['name'] = media['name'].replace('--forced--', '-forced')
                    LanguageID = ReplaceCodeLanguages(media['language']) + '-forced'
                if 'https://' not in media['uri']:
                    full_url = master_base_url + media['uri']
                    Full_URL_Type = False
                else:
                    full_url = media['uri']
                    Full_URL_Type = True
                subs_dict = {
                 'trackType':trackType, 
                 'Language':media['name'], 
                 'LanguageID':LanguageID, 
                 'Profile':media['group_id'], 
                 'isCC':isCC, 
                 'isForced':isForced, 
                 'isNormal':isNormal, 
                 'url':full_url}
                subs_list.append(subs_dict)

        video_list = []
        for playlist in m3u8_master_json['playlists']:
            def get_height(width, height):
                if width == '1920':
                    return '1920', '1080'
                if width == '1356':
                    return '1280', '720'
                elif width == '864':
                    return '640', '480'
                elif width == '3840':
                    return '4096', '2160'

                else:
                    return width, height
            video_range = playlist['stream_info']['video_range'].replace('"', '')
            resolution = re.split('x', playlist['stream_info']['resolution'])
            width, height = get_height(resolution[0], resolution[-1])

            codecs = None
            codecs = re.search(r',(avc.+?|dvh1.+?|hvc1.+?)$', playlist['stream_info']['codecs'])
            if codecs == None:
                codecs = re.search(r'(avc.+?|dvh1.+?|hvc1.+?),', playlist['stream_info']['codecs'])

            if 'https://' not in playlist['uri']:
                full_url = master_base_url + playlist['uri']
                Full_URL_Type = False
            else:
                full_url = playlist['uri']
                Full_URL_Type = True
            video_dict = {
                 'Video_Range':video_range, 
                 'Width':width, 
                 'Height':height, 
                 'Codec':codecs[1], 
                 'frame_rate':playlist['stream_info']['frame_rate'], 
                 'url':full_url, 
                 'Bitrate':playlist['stream_info']['bandwidth'], 
                 'Average_Bandwidth':playlist['stream_info']['average_bandwidth']}
            video_list.append(video_dict)

        if args.videocodec:
            if args.videocodec == 'h264':
                codec_s = 'avc1'
            if args.videocodec == 'hevc':
                codec_s = 'hvc1'
            if args.videocodec == 'hdr':
                codec_s = 'dvh1'
            
            video_list_tmp = []
            for x in video_list:
                if codec_s in x['Codec']:
                    video_list_tmp.append(x)
            video_list = video_list_tmp

        # AUDIO LIST #
        audio_List = sorted(audio_List, key=(lambda k: (str(k['Profile']), str(k['LanguageID']))), reverse=True)

        if args.only_2ch_audio:
            audioList_new = []
            for x in audio_List:
                if int(x['Channels']) == 2:
                    audioList_new.append(x)

            audio_List = audioList_new
            
        BitrateList = []
        AudioLanguageList = []
        for x in audio_List:
            BitrateList.append(str(x['Profile']))
            AudioLanguageList.append(x['LanguageID'])

        BitrateList = alphanumericSort(list(set(BitrateList)))
        AudioLanguageList = alphanumericSort(list(set(AudioLanguageList)))
        audioList_new = []
        audio_Dict_new = {}
        for y in AudioLanguageList:
            counter = 0
            for x in audio_List:
                if x['LanguageID'] == y and counter == 0:
                    audio_Dict_new = {
                     'trackType':x['trackType'], 
                     'Language':x['Language'], 
                     'LanguageID':x['LanguageID'], 
                     'Profile':x['Profile'], 
                     'Codec':x['Codec'], 
                     'Channels':x['Channels'], 
                     'isAD':x['isAD'], 
                     'url':x['url'], 
                     'Bitrate':x['Bitrate']}
                    audioList_new.append(audio_Dict_new)
                    counter = counter + 1

        audio_List = audioList_new
        audio_List = sorted(audio_List, key=(lambda k: (str(k['Profile']), str(k['LanguageID']))))

        if args.desc_audio:
            c = 0
            while c != len(audio_List):
                if not audio_List[c]['isAD']:
                    audio_List.remove(audio_List[c])
                else:
                    c += 1
        else:
            c = 0
            while c != len(audio_List):
                if audio_List[c]['isAD']:
                    audio_List.remove(audio_List[c])
                else:
                    c += 1

        audioList_new = []
        if args.audiolang:
            for x in audio_List:
                langAbbrev = x['LanguageID']
                if langAbbrev in list(args.audiolang):
                    audioList_new.append(x)

            audio_List = audioList_new
        audio_List = audio_List

        # SUBTITLE LIST #
        SubsLanguageList = []
        for x in subs_list:
            SubsLanguageList.append(x['LanguageID'])

        SubsLanguageList = alphanumericSort(list(set(SubsLanguageList)))
        subList_new = []
        for y in SubsLanguageList:
            counter = 0
            for x in subs_list:
                if x['LanguageID'] == y and counter == 0:
                    subs_Dict_new = {
                     'trackType':x['trackType'], 
                     'Language':x['Language'], 
                     'LanguageID':x['LanguageID'], 
                     'Profile':x['Profile'], 
                     'isCC':x['isCC'], 
                     'isForced':x['isForced'], 
                     'isNormal':x['isNormal'], 
                     'url':x['url']}
                    subList_new.append(subs_Dict_new)
                    counter = counter + 1

        subs_list = subList_new

        subs_list_new = []
        subs_for_list_new = []
        for subs in subs_list:
            isForced = subs['isForced']
            if isForced:
                subs_for_list_new.append(subs)
            else:
                subs_list_new.append(subs)

        subs_for_list = []
        for subs in subs_for_list_new:
            lang = subs['LanguageID']
            if args.forcedlang:
                if lang in args.forcedlang:
                    subs_for_list.append(subs)
            else:
                subs_for_list.append(subs)

        subs_list = []
        for subs in subs_list_new:
            lang = subs['LanguageID']
            if args.sublang:
                if lang in args.sublang:
                    subs_list.append(subs)
            else:
                subs_list.append(subs)

        subs_list_new = []
        subs_list_new = subs_list + subs_for_list
        subs_list = subs_list_new

        # VIDEO LIST #
        video_list = sorted(video_list, key=(lambda k: int(k['Bitrate'])))
        video_List_temp = video_list
        height_all = []
        for x in video_list:
            height_all.append(x['Height'])

        height_all_ord = alphanumericSort(list(set(height_all)))
        while args.customquality != [] and int(video_list[(-1)]['Height']) > int(args.customquality[0]):
            video_list.pop(-1)

        video_list_tmp = []
        video_list_tmp.append(video_list[(-1)])
        video_list = video_list_tmp

        return audio_List, video_list, subs_list

    def m3u8_parser_alt(m3u8_url):
        master_base_url = re.split('(/)(?i)', m3u8_url)
        del master_base_url[-1]
        master_base_url = ''.join(master_base_url)
        m3u8_master_json = m3u8parser(requests.get(m3u8_url, headers=AUTH_HEADERS["wvHeaders"]).text)
        for media in m3u8_master_json['media']:
            audio_List = []
            if media['type'] == 'AUDIO':
                isAD = False
                try:
                    if 'public.accessibility.' in media['characteristics']:
                        isAD = True
                except Exception:
                    isAD = False
                
                group_id = media['group_id'].replace('HE-stereo', 'aac').replace('stereo', 'aac')
                
                m = re.search(r"audio_gr(.+?)_", media['uri'])
                mx = re.search(r"audio-(.+?)(-|_)", group_id)

                Bitrate = m[1]
                Codec = mx[1]
                if int(Bitrate) > 2000:
                    Bitrate = Bitrate[1:]

                if isAD:
                    LanguageID = ReplaceCodeLanguages(media['language']) + '-ad'
                else:
                    LanguageID = ReplaceCodeLanguages(media['language'])

                if isAD:
                    trackType = 'NARRATION'
                else:
                    trackType = 'PRIMARY'

                if 'https://' not in media['uri']:
                    full_url = master_base_url + media['uri']
                    Full_URL_Type = False

                else:
                    full_url = media['uri']
                    Full_URL_Type = True

                audio_dict = {
                    'trackType':trackType, 
                    'Language':media['name'], 
                    'LanguageID':LanguageID, 
                    'Profile':group_id, 
                    'Codec':Codec, 
                    'Channels':media['channels'].replace('"', '').replace('/JOC', ''), 
                    'isAD':isAD, 
                    'url':full_url, 
                    'Bitrate':Bitrate}
                audio_List.append(audio_dict)
            
            subs_list = []
            if media['type'] == 'SUBTITLES':
                isCC = False
                try:
                    if 'public.accessibility.' in media['characteristics']:
                        isCC = True
                except Exception:
                    isCC = False

                if '_NORMAL_' in media['uri']:
                    isCC = False
                isNormal = False
                if isCC:
                    LanguageID = ReplaceCodeLanguages(media['language']) + '-sdh'
                    trackType = 'SDH'
                else:
                    trackType = 'NORMAL'
                    isNormal = True
                    LanguageID = ReplaceCodeLanguages(media['language'])
                isForced = False
                if media['forced'] == 'YES':
                    isForced = True
                    isNormal = False
                    trackType = 'FORCED'
                    media['name'] = media['name'].replace('--forced--', '-forced')
                    LanguageID = ReplaceCodeLanguages(media['language']) + '-forced'
                if 'https://' not in media['uri']:
                    full_url = master_base_url + media['uri']
                    Full_URL_Type = False
                else:
                    full_url = media['uri']
                    Full_URL_Type = True
                subs_dict = {
                 'trackType':trackType, 
                 'Language':media['name'], 
                 'LanguageID':LanguageID, 
                 'Profile':media['group_id'], 
                 'isCC':isCC, 
                 'isForced':isForced, 
                 'isNormal':isNormal, 
                 'url':full_url}
                subs_list.append(subs_dict)

        video_list = []
        for playlist in m3u8_master_json['playlists']:
            def get_height(width, height):
                if width == '1920':
                    return '1920', '1080'
                if width == '1356':
                    return '1280', '720'
                elif width == '864':
                    return '640', '480'
                elif width == '3840':
                    return '4096', '2160'

                else:
                    return width, height
            video_range = playlist['stream_info']['video_range'].replace('"', '')
            resolution = re.split('x', playlist['stream_info']['resolution'])
            width, height = get_height(resolution[0], resolution[-1])

            codecs = None
            codecs = re.search(r',(avc.+?|dvh1.+?|hvc1.+?)$', playlist['stream_info']['codecs'])
            if codecs == None:
                codecs = re.search(r'(avc.+?|dvh1.+?|hvc1.+?),', playlist['stream_info']['codecs'])

            if 'https://' not in playlist['uri']:
                full_url = master_base_url + playlist['uri']
                Full_URL_Type = False
            else:
                full_url = playlist['uri']
                Full_URL_Type = True
            video_dict = {
                 'Video_Range':video_range, 
                 'Width':width, 
                 'Height':height, 
                 'Codec':codecs[1], 
                 'frame_rate':playlist['stream_info']['frame_rate'], 
                 'url':full_url, 
                 'Bitrate':playlist['stream_info']['bandwidth'], 
                 'Average_Bandwidth':playlist['stream_info']['average_bandwidth']}
            video_list.append(video_dict)

        if args.videocodec:
            if args.videocodec == 'h264':
                codec_s = 'avc1'
            if args.videocodec == 'hevc':
                codec_s = 'hvc1'
            if args.videocodec == 'hdr':
                codec_s = 'dvh1'
            
            video_list_tmp = []
            for x in video_list:
                if codec_s in x['Codec']:
                    video_list_tmp.append(x)
            video_list = video_list_tmp

        # AUDIO LIST #
        audio_List = sorted(audio_List, key=(lambda k: (str(k['Profile']), str(k['LanguageID']))), reverse=True)

        if args.only_2ch_audio:
            audioList_new = []
            for x in audio_List:
                if int(x['Channels']) == 2:
                    audioList_new.append(x)

            audio_List = audioList_new
            
        BitrateList = []
        AudioLanguageList = []
        for x in audio_List:
            BitrateList.append(str(x['Profile']))
            AudioLanguageList.append(x['LanguageID'])

        BitrateList = alphanumericSort(list(set(BitrateList)))
        AudioLanguageList = alphanumericSort(list(set(AudioLanguageList)))
        audioList_new = []
        audio_Dict_new = {}
        for y in AudioLanguageList:
            counter = 0
            for x in audio_List:
                if x['LanguageID'] == y and counter == 0:
                    audio_Dict_new = {
                     'trackType':x['trackType'], 
                     'Language':x['Language'], 
                     'LanguageID':x['LanguageID'], 
                     'Profile':x['Profile'], 
                     'Codec':x['Codec'], 
                     'Channels':x['Channels'], 
                     'isAD':x['isAD'], 
                     'url':x['url'], 
                     'Bitrate':x['Bitrate']}
                    audioList_new.append(audio_Dict_new)
                    counter = counter + 1

        audio_List = audioList_new
        audio_List = sorted(audio_List, key=(lambda k: (str(k['Profile']), str(k['LanguageID']))))

        if args.desc_audio:
            c = 0
            while c != len(audio_List):
                if not audio_List[c]['isAD']:
                    audio_List.remove(audio_List[c])
                else:
                    c += 1
        else:
            c = 0
            while c != len(audio_List):
                if audio_List[c]['isAD']:
                    audio_List.remove(audio_List[c])
                else:
                    c += 1

        audioList_new = []
        if args.audiolang:
            for x in audio_List:
                langAbbrev = x['LanguageID']
                if langAbbrev in list(args.audiolang):
                    audioList_new.append(x)

            audio_List = audioList_new
        audio_List = audio_List

        # SUBTITLE LIST #
        SubsLanguageList = []
        for x in subs_list:
            SubsLanguageList.append(x['LanguageID'])

        SubsLanguageList = alphanumericSort(list(set(SubsLanguageList)))
        subList_new = []
        for y in SubsLanguageList:
            counter = 0
            for x in subs_list:
                if x['LanguageID'] == y and counter == 0:
                    subs_Dict_new = {
                     'trackType':x['trackType'], 
                     'Language':x['Language'], 
                     'LanguageID':x['LanguageID'], 
                     'Profile':x['Profile'], 
                     'isCC':x['isCC'], 
                     'isForced':x['isForced'], 
                     'isNormal':x['isNormal'], 
                     'url':x['url']}
                    subList_new.append(subs_Dict_new)
                    counter = counter + 1

        subs_list = subList_new

        subs_list_new = []
        subs_for_list_new = []
        for subs in subs_list:
            isForced = subs['isForced']
            if isForced:
                subs_for_list_new.append(subs)
            else:
                subs_list_new.append(subs)

        subs_for_list = []
        for subs in subs_for_list_new:
            lang = subs['LanguageID']
            if args.forcedlang:
                if lang in args.forcedlang:
                    subs_for_list.append(subs)
            else:
                subs_for_list.append(subs)

        subs_list = []
        for subs in subs_list_new:
            lang = subs['LanguageID']
            if args.sublang:
                if lang in args.sublang:
                    subs_list.append(subs)
            else:
                subs_list.append(subs)

        subs_list_new = []
        subs_list_new = subs_list + subs_for_list
        subs_list = subs_list_new

        # VIDEO LIST #
        video_list = sorted(video_list, key=(lambda k: int(k['Bitrate'])))
        video_List_temp = video_list
        height_all = []
        for x in video_list:
            height_all.append(x['Height'])

        height_all_ord = alphanumericSort(list(set(height_all)))
        while args.customquality != [] and int(video_list[(-1)]['Height']) > int(args.customquality[0]):
            video_list.pop(-1)

        video_list_tmp = []
        video_list_tmp.append(video_list[(-1)])
        video_list = video_list_tmp

        return audio_List, video_list, subs_list

    def get_episodes(ep_str, num_eps):
        eps = ep_str.split(',')
        eps_final = []

        for ep in eps:
            if '-' in ep:
                (start, end) = ep.split('-')
                start = int(start)
                end = int(end or num_eps)
                eps_final += list(range(start, end + 1))
            else:
                eps_final.append(int(ep))

        return eps_final

    def get_seasons(series_id):
        APTVConfig.APTV_PARAMS["skip"] = "0"
        APTVConfig.APTV_PARAMS["count"] = "100"
        resp = requests.get(url=APTVConfig.APTV_ENDPOINTS["SERIES"] % (series_id), params=APTVConfig.APTV_PARAMS, cookies=COOKIES).json()

        if not args.season:
            args.season = 'all'

        seasons = []
        if args.season:
            if args.season == 'all':
                seasons = 'all'
            elif ',' in args.season:
                seasons = [int(x) for x in args.season.split(',')]
            elif '-' in args.season:
                (start, end) = args.season.split('-')
                seasons = list(range(int(start), int(end) + 1))
            else:
                seasons = [int(args.season)]

        if 'Episode' in resp['data']['episodes'][0]['type']:
            if seasons == 'all':
                seasons_list = [x['seasonNumber'] for x in resp['data']['episodes']]
                seasons = sorted(set(seasons_list))

            for season_num in seasons:
                for x in resp['data']['episodes']:
                    episodes_list = []
                    episodes_dict = {}
                    if x['seasonNumber'] == int(season_num):
                        episodes_dict = {
                            'id':x['id'],
                            'episode_num':x['episodeNumber']}
                        episodes_list.append(episodes_dict)

                    if args.episodeStart:
                        eps = get_episodes(args.episodeStart, len(episodes_list))
                        episodes_list = [x for x in episodes_list if x['episode_num'] in eps]

                    for episode in episodes_list:
                        get_metadata(content_id=episode['id'])

    global folderdownloader
    if args.output:
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        os.chdir(args.output)
        if ":" in str(args.output):
            folderdownloader = str(args.output).replace('/','\\').replace('.\\','\\')
        else:
            folderdownloader = dirPath + str(args.output).replace('/','\\').replace('.\\','\\')
    else:
        folderdownloader = dirPath.replace('/','\\').replace('.\\','\\')

    def get_metadata(content_id):
        resp = requests.get(url=APTVConfig.APTV_ENDPOINTS["PRODUCT"] % (content_id), params=APTVConfig.APTV_PARAMS, cookies=COOKIES)#.json()
        if int(resp.status_code) == 404:
            print(resp.text)
            exit()
        resp = resp.json()

        if 'Episode' in resp['data']['content']['type']:
            aptv_type = "show"
            seriesTitles = resp['data']['content']['showTitle']
            seasonNumber = resp['data']['content']['seasonNumber']
            episodeNumber = resp['data']['content']['episodeNumber']
            episodeTitle = resp['data']['content']['title']

        if 'Movie' in resp['data']['content']['type']:
            aptv_type = "movie"
            seriesTitles = resp['data']['content']['title']

        if aptv_type=="movie":
            seriesName = replace_words(seriesTitles)
            folderName = None

        if aptv_type=="show":
            seriesName = f'{replace_words(seriesTitles)} S{seasonNumber:02}E{episodeNumber:02} - {replace_words(episodeTitle)}'
            folderName = f'{replace_words(seriesTitles)} S{seasonNumber:02}'

        start_process(seriesName, folderName, aptv_type, get_drm_info(content_id, seriesName))

    def start_process(seriesName, folderName, aptv_type, drm_info):
        try:
            audio_List, video_list, subs_list = m3u8_parsing(drm_info["manifest"])
        except (KeyError, TypeError):
            audio_List, video_list, subs_list = m3u8_parser_alt(drm_info["manifest"])
        video_bandwidth = dict(video_list[(-1)])['Average_Bandwidth']
        video_height = str(dict(video_list[(-1)])['Height'])
        video_width = str(dict(video_list[(-1)])['Width'])
        video_codec = str(dict(video_list[(-1)])['Codec'])
        if not args.license:
            if not args.novideo:
                print('\nVIDEO - Bitrate: ' + convert_size(int(video_bandwidth)) + ' - Profile: ' + video_codec.split('=')[0] + ' - Dimensions: ' + video_width + 'x' + video_height)
            print()

            if not args.noaudio:
                if audio_List != []:
                    for x in audio_List:
                        audio_bandwidth = x['Bitrate']
                        audio_lang = x['LanguageID']
                        audio_codec = x['Codec']
                        audio_channels = x['Channels']
                        print('AUDIO - Bitrate: ' + audio_bandwidth + 'kbps - Profile: ' + audio_codec + ' - Channels: ' + audio_channels + ' - Language: ' + audio_lang)
                    print()

            if not args.nosubs:
                if subs_list != []:
                    for z in subs_list:
                        trackType = z['trackType']
                        subs_lang = z['LanguageID']
                        print('SUBTITLE - Profile: '+ trackType +' - Language: ' + subs_lang)
                    print()
            print('Name: ' + seriesName)

        if args.info:
            pass
        else:

            if args.license:
                keys_video = []
                keys_audio = []

                try:
                    keys_video = get_keys(get_pssh(video_list[(-1)]['url']), drm_info["license_params"])
                except KeyError:
                    print('License request failed, using keys from txt')
                    keys_video = keys_file_txt
                else:
                    with open(keys_file, "a", encoding="utf8") as file:
                        file.write(seriesName + " (video)" + "\n")
                        print("\n" + seriesName + " (video) " )
                    for key in keys_video:
                        with open(keys_file, "a", encoding="utf8") as file:
                            file.write(key + "\n")
                            print(key)

                try:
                    keys_audio = get_keys(get_pssh(audio_List[(-1)]['url']), drm_info["license_params"])
                except KeyError:
                    print('License request failed, using keys from txt')
                    keys_audio = keys_file_txt
                else:
                    with open(keys_file, "a", encoding="utf8") as file:
                        file.write(seriesName + " (audio)" + "\n")
                        print("\n" + seriesName + " (audio)")
                    for key in keys_audio:
                        with open(keys_file, "a", encoding="utf8") as file:
                            file.write(key + "\n")
                            print(key)

            else:

                print("\nGetting KEYS...")
                keys_video = []
                keys_audio = []

                try:
                    keys_video = get_keys(get_pssh(video_list[(-1)]['url']), drm_info["license_params"])
                except KeyError:
                    print('License request failed, using keys from txt')
                    keys_video = keys_file_txt
                else:
                    with open(keys_file, "a", encoding="utf8") as file:
                        file.write(seriesName + "\n")
                    for key in keys_video:
                        with open(keys_file, "a", encoding="utf8") as file:
                            file.write(key + "\n")

                try:
                    keys_audio = get_keys(get_pssh(audio_List[(-1)]['url']), drm_info["license_params"])
                except KeyError:
                    print('License request failed, using keys from txt')
                    keys_audio = keys_file_txt
                else:
                    with open(keys_file, "a", encoding="utf8") as file:
                        file.write(seriesName + "\n")
                    for key in keys_audio:
                        with open(keys_file, "a", encoding="utf8") as file:
                            file.write(key + "\n")
                print("Done!")

                if aptv_type == 'show':
                    CurrentName = seriesName
                    CurrentHeigh = str(video_height)
                    VideoOutputName = folderdownloader + '\\' + str(folderName) + str(CurrentName) + ' [' + str(CurrentHeigh) + 'p].mkv'
                else:
                    CurrentName = seriesName
                    CurrentHeigh = str(video_height)
                    VideoOutputName = folderdownloader + str(CurrentName) + ' [' + str(CurrentHeigh) + 'p].mkv'

                if not os.path.isfile(VideoOutputName):

                    if not args.novideo:
                        inputVideo = CurrentName + ' [' + str(CurrentHeigh) + 'p].mp4'
                        if os.path.isfile(inputVideo):
                            print('\n' + inputVideo + '\nFile has already been successfully downloaded previously.\n')
                        else:
                            for m3u8_video in video_list:
                                video_m3u8_url = m3u8_video['url']
                            wvdl_cfg = WvDownloaderConfig(video_m3u8_url, inputVideo)
                            wvdownloader = WvDownloader(wvdl_cfg)
                            url_list = wvdownloader.run()
                        
                            CorrectDecryptVideo = False

                            counter = 0
                            for url_dic in url_list:
                                url_id = url_dic['id']
                                count_id = str(counter).zfill(4)
                                inputVideoAria = CurrentName + f' [{CurrentHeigh}p]_{count_id}_{url_id}.mp4'
                                CorrectDecryptVideo = DecryptVideo(inputVideo=inputVideoAria, keys_video=keys_video)
                                counter = counter + 1


                            counter = 0

                            for url_dic in url_list:
                                url_id = url_dic['id']
                                url_list = url_dic['url_list']
                                count_id = str(counter).zfill(4)
                                inputVideoAria = CurrentName + f' [{CurrentHeigh}p]_{count_id}_{url_id}.mp4'
                            
                            os.rename(inputVideoAria, inputVideo)


                    if not args.noaudio:
                        for x in audio_List:
                            audio_m3u8_url = x['url']
                            langAbbrev = x['LanguageID']
                            inputAudio = CurrentName + ' ' + '(' + langAbbrev + ').mp4'
                            inputAudiomka = CurrentName + ' ' + '(' + langAbbrev + ').mka'
                            if os.path.isfile(inputAudio) or os.path.isfile(inputAudiomka):
                                print('\n' + inputAudio + '\nFile has already been successfully downloaded previously.\n')
                            else:
                                wvdl_cfg = WvDownloaderConfig(audio_m3u8_url, inputAudio)
                                wvdownloader = WvDownloader(wvdl_cfg)
                                url_list = wvdownloader.run()
                        
                                CorrectDecryptAudio = False

                                counter = 0
                                for url_dic in url_list:
                                    url_id = url_dic['id']
                                    count_id = str(counter).zfill(4)
                                    inputAudioAria = CurrentName + f' ({langAbbrev})_{count_id}_{url_id}.mp4'
                                    CorrectDecryptAudio = DecryptAudio(inputAudio=inputAudioAria, keys_audio=keys_audio)
                                    counter = counter + 1
                                inputAudioAria = inputAudioAria.replace('.mp4', '.mka')
                                os.rename(inputAudioAria, inputAudiomka)

                    if not args.nosubs:
                        if subs_list != []:
                            for z in subs_list:
                                sub_m3u8_url = z['url']
                                langAbbrev = z['LanguageID']
                                inputSubtitle = CurrentName + ' ' + '(' + langAbbrev + ')' 
                                if os.path.isfile(inputSubtitle + '.webvtt') or os.path.isfile(inputSubtitle + '.srt'):
                                    print('\n' + inputSubtitle + '\nFile has already been successfully downloaded previously.\n')
                                else:
                                    download_subs(inputSubtitle, sub_m3u8_url)

                    if not args.novideo or (not args.noaudio):
                        if not args.nomux:
                            if not args.novideo:
                                if not args.noaudio:
                                    if CorrectDecryptVideo == True:
                                        if CorrectDecryptAudio == True:
                                            print('\nMuxing...')

                                            do_muxer(CurrentName, 
                                                    folderName,
                                                    aptv_type,
                                                    CurrentHeigh,
                                                    audio_List,
                                                    subs_list)

                                            if args.tag:
                                                inputName = CurrentName + ' [' + CurrentHeigh + 'p].mkv'
                                                release_group(base_filename=inputName,
                                                            default_filename=CurrentName,
                                                            folder_name=folderName,
                                                            type=aptv_type,
                                                            video_height=CurrentHeigh)

                                            if not args.keep:
                                                for f in os.listdir():
                                                    if re.fullmatch(re.escape(CurrentName) + r'.*\.(mp4|m4a|h264|h265|eac3|ac3|srt|txt|avs|lwi|mka)', f):
                                                        os.remove(f)
                                            print("Done!")
                else:
                    print("\nFile '" + str(VideoOutputName) + "' already exists.")

    def do_muxer(filename, foldername, contentype, video_height, audio_list, subs_list):

        inputVideo = filename + ' [' + video_height + 'p].mp4'

        if isfile(inputVideo):
            video_filename = inputVideo
            if contentype == 'show':
                muxed_filename = join(foldername, inputVideo[:-4])
            else:
                muxed_filename = inputVideo[:-4]
        
        mkvmerge_command = [
            APTVConfig.MKVMERGE,
            '-o', muxed_filename + '.mkv',
        ]

        mkvmerge_command += [
            '--language', '0:und',
            '(', video_filename, ')',
        ]

        AudioExtensionsList = [
            ".mka",
            ".eac3",
            ".m4a",
            ".dts",
            ".mp3",
            ".aac"
        ]

        for audio_track in audio_list:
            for audio_extension in AudioExtensionsList:
                audio_filename = filename + ' ' + '(' + audio_track["LanguageID"] + ')' + audio_extension
                if isfile(audio_filename):
                    lang = '0:{}'.format(audio_track["LanguageID"])
                    lang_name = '0:{}'.format(audio_track["Language"])

                    if lang == '0:es-la':
                        default = 'yes'
                    else:
                        default = 'no'

                    mkvmerge_command += ["--language",
                                        lang,
                                        "--track-name",
                                        lang_name,
                                        "--default-track",
                                        f"0:{default}",
                                        "(",
                                        audio_filename,
                                        ")"]

        for subtitle_track in subs_list:
            subs_filename = filename + ' ' + '(' + subtitle_track["LanguageID"] + ').srt'
            if isfile(subs_filename):
                lang = '0:{}'.format(subtitle_track["LanguageID"])
                lang_name = '0:{}'.format(subtitle_track["Language"])
                if '-' in lang:
                    newlang = lang.split('-')[0]
                    lang = newlang

                forced = "yes" if "forced" in lang else "no"
                mkvmerge_command = mkvmerge_command + ["--language",
                                                        lang,
                                                        #"--sync",
                                                        #"0:-9800",
                                                        "--sub-charset",
                                                        "0:UTF-8",
                                                        "--track-name",
                                                        lang_name,
                                                        "--default-track",
                                                        "0:no",
                                                        "--forced-track",
                                                        f"0:{forced}",
                                                        "(",
                                                        subs_filename,
                                                        ")"]
        mkvmerge_process = subprocess.run(mkvmerge_command)

    def get_drm_info(id, titleName):
        resp = requests.get(url=APTVConfig.APTV_ENDPOINTS["CONTENT_DATA"] % (id), params=APTVConfig.APTV_PARAMS, headers=AUTH_HEADERS["wvHeaders"], cookies=COOKIES).json()['data']['content']
        if "isComingSoon" in resp["playables"][0]:
            print('\n' + titleName)
            print("Release Date " + resp["playables"][0]["comingSoonDate"])
            exit()
        
        hlsUrl = []
        license_params = []
        for x in resp["playables"]:
            if 'assets' in x:
                hlsUrl = x['assets']['hlsUrl']
                license_params = x['assets']['fpsKeyServerQueryParameters']
        return {"manifest": hlsUrl, "license_params": license_params}

    def release_group(base_filename, default_filename, folder_name, type, video_height):
        if type=='show':
            video_mkv = os.path.join(folder_name, base_filename)
        else:
            video_mkv = base_filename
        
        mediainfo = mediainfo_(video_mkv)
        for v in mediainfo['media']['track']: # mediainfo do video
            if v['@type'] == 'Video':
                video_format = v['Format']

        video_codec = ''
        if video_format == "AVC":
            video_codec = 'H.264'
        elif video_format == "HEVC":
            video_codec = 'H.265'

        for m in mediainfo['media']['track']: # mediainfo do audio
            if m['@type'] == 'Audio':
                codec_name = m['Format']
                channels_number = m['Channels']

        audio_codec = ''
        audio_channels = ''
        if codec_name == "AAC":
            audio_codec = 'AAC'
        elif codec_name == "AC-3":
            audio_codec = "DD"
        elif codec_name == "E-AC-3":
            audio_codec = "DDP"
        elif codec_name == "E-AC-3 JOC":
            audio_codec = "Atmos"
            
        if channels_number == "2":
            audio_channels = "2.0"
        elif channels_number == "6":
            audio_channels = "5.1"

        audio_ = audio_codec + audio_channels

        # renomear arquivo
        default_filename = default_filename.replace('&', '.and.')
        default_filename = re.sub(r'[]!"#$%\'()*+,:;<=>?@\\^_`{|}~[-]', '', default_filename)
        default_filename = default_filename.replace(' ', '.')
        default_filename = re.sub(r'\.{2,}', '.', default_filename)

        output_name = '{}.{}p.ATVP.WEB-DL.{}.{}-{}'.format(default_filename, video_height, audio_, video_codec, args.tag)
        if type=='show':
            outputName = os.path.join(folder_name, output_name + '.mkv')
        else:
            outputName = output_name + '.mkv'

        os.rename(video_mkv, outputName)
        print("{} -> {}".format(base_filename, output_name))

    def DecryptVideo(inputVideo, keys_video):
        key_video_id_original = getKeyId(inputVideo)
        inputVideo = inputVideo
        outputVideoTemp = inputVideo.replace('.mp4', '_dec.mp4')
        outputVideo = inputVideo
        if key_video_id_original != 'nothing':
            command_line = [APTVConfig.SHAKA_PACKAGER]
            command_line.append("-quiet")
            command_line.append("in={input},stream={stream},output={output},drm_label={drm_label}".format(
                input=inputVideo,
                stream="video",
                output=outputVideoTemp,
                drm_label="UHD1"))
            command_line.append("--enable_raw_key_decryption")
            for key in keys_video:
                print('\nDecrypting video...')
                #print('Using KEY: ' + key)
                command_line.append("--keys")
                command_line.append("label=UHD1:key_id={key_id}:key={key}".format(key_id="00000000000000000000000000000000", key=key.split(":")[1]))
                wvdecrypt_process = subprocess.run(command_line)
                print('\nRemuxing video...')
                ff = ffmpy.FFmpeg(executable=APTVConfig.FFMPEG, inputs={outputVideoTemp: None}, outputs={outputVideo: '-c copy'}, global_options='-y -hide_banner -loglevel quiet')
                ff.run()
                time.sleep(0.05)
                os.remove(outputVideoTemp)
                print('Done!')
                return True

    def DecryptAudio(inputAudio, keys_audio):
        key_audio_id_original = getKeyId(inputAudio)
        outputAudioTemp = inputAudio.replace(".mp4", "_dec.mp4")
        if key_audio_id_original != 'nothing':
            command_line = [APTVConfig.SHAKA_PACKAGER]
            command_line.append("-quiet")
            command_line.append("in={input},stream={stream},output={output},drm_label={drm_label}".format(
                input=inputAudio,
                stream="audio",
                output=outputAudioTemp,
                drm_label="HD"))
            command_line.append("--enable_raw_key_decryption")
            for key in keys_audio:
                print('\nDecrypting audio...')
                #print('Using KEY: ' + key)
                command_line.append("--keys")
                command_line.append("label=UHD1:key_id={key_id}:key={key}".format(key_id="00000000000000000000000000000000", key=key.split(":")[1]))
                wvdecrypt_process = subprocess.run(command_line)
                time.sleep(0.05)
                os.remove(inputAudio)
                print('\nDemuxing audio...')
                outputAudio = outputAudioTemp.replace('_dec.mp4', '.mka')
                print('{} -> {}'.format(outputAudioTemp, outputAudio))
                ff = ffmpy.FFmpeg(executable=APTVConfig.FFMPEG, inputs={outputAudioTemp: None}, outputs={outputAudio: '-c copy'}, global_options='-y -hide_banner -loglevel warning')
                ff.run()
                time.sleep(0.05)
                os.remove(outputAudioTemp)
                print('Done!')
                return True

        elif key_audio_id_original == 'nothing':
            return True
            
    from pywidevine.decrypt.wvdecryptcustom import WvDecrypt
    from pywidevine.cdm import cdm, deviceconfig

    def get_keys(pssh, content_info):
        cert_b64 = base64.b64encode(requests.post(url=APTVConfig.APTV_ENDPOINTS["WV_CERT"], headers=AUTH_HEADERS["wvHeaders"]).content)
        wvdecrypt = WvDecrypt(init_data_b64=bytes(pssh.encode()), cert_data_b64=None, device=deviceconfig.device_asus_x00dd)
        
        licese_payload = {}
        licese_payload["challenge"] = base64.b64encode(wvdecrypt.get_challenge()).decode('utf-8')
        licese_payload["extra-server-parameters"] = content_info
        licese_payload["key-system"] = "com.widevine.alpha"
        licese_payload["license-action"] = "start"
        licese_payload["uri"] = 'data:text/plain;base64,%s' % (pssh)

        license_rep = requests.post(url=APTVConfig.APTV_ENDPOINTS["WV_LICENSE"], json=licese_payload, headers=AUTH_HEADERS["wvHeaders"])
        license_b64 = license_rep.json()['license']

        wvdecrypt.update_license(license_b64)
        status, keys = wvdecrypt.start_process()
        return keys

    if not args.url_season:
        url_season = input('Enter the AppleTV+ url (with https): ')
    else:
        url_season = str(args.url_season)

    m = re.search(r'(umc.cmc.)(.+?)$', url_season)
    if '/show/' in url_season:
        get_seasons(m[2])
    elif '/movie/' in url_season:
        get_metadata(m[1] + m[2])
