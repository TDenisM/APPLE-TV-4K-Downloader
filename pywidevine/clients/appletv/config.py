from shutil import which
from os.path import dirname, realpath, join
from os import pathsep, environ

APTV_ENDPOINTS = {
    'SERIES': 'https://tv.apple.com/api/uts/v2/view/show/umc.cmc.%s/episodes',
    'PRODUCT': 'https://tv.apple.com/api/uts/v2/view/product/%s',
    'CONTENT_DATA': 'https://tv.apple.com/api/uts/v2/view/product/%s/personalized',
    'WV_LICENSE': 'https://play.itunes.apple.com/WebObjects/MZPlay.woa/web/video/subscription/license',
    'WV_CERT': 'https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert'
}

APTV_PARAMS = {'utscf': 'OjAAAAAAAAA~', 'utsk': '6e3013c6d6fae3c2::::::9724ac949afa4bb2', 'caller': 'web', 'sf': '143468', 'v': '40', 'pfm': 'web', 'locale': 'en-US'}

SCRIPT_PATH = dirname(realpath('appletv'))

BINARIES_FOLDER = join(SCRIPT_PATH, 'binaries')

SHAKA_PACKAGER_BINARY = 'packager-win'
MEDIAINFO_BINARY = 'mediainfo'
MP4DUMP_BINARY = 'mp4dump'
MKVMERGE_BINARY = 'mkvmerge'
FFMPEG_BINARY = 'ffmpeg'
ARIA2C_BINARY = 'aria2c'
SUBTITLE_EDIT_BINARY = 'subtitleedit'

# Add binaries folder to PATH as the first item
environ['PATH'] = pathsep.join([BINARIES_FOLDER, environ['PATH']])

SHAKA_PACKAGER = which(SHAKA_PACKAGER_BINARY)
MEDIAINFO = which(MEDIAINFO_BINARY)
MP4DUMP = which(MP4DUMP_BINARY)
MKVMERGE = which(MKVMERGE_BINARY)
FFMPEG = which(FFMPEG_BINARY)
ARIA2C = which(ARIA2C_BINARY)
SUBTITLE_EDIT = which(SUBTITLE_EDIT_BINARY)

class WvDownloaderConfig(object):
    def __init__(self, m3u8, output_file):
        self.m3u8 = m3u8
        self.output_file = output_file

COMMOM_HEADERS = {
    'Connection': 'keep-alive',
    'User-Agent': 'AppleCoreMedia/1.0.0.12B466 (Apple TV; U; CPU OS 8_1_3 like Mac OS X; en_us)',
    'Content-Type': 'application/json',
    'Origin': 'https://tv.apple.com',
    'Referer': 'https://tv.apple.com/',
}
