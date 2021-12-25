# -*- coding: utf-8 -*-
# Module: BAD Project
# Created on: 01-06-2021
# Authors: JUNi
# Version: 1.0

import argparse
import os
import sys


parser = argparse.ArgumentParser()
#Common:
parser.add_argument("content", nargs="?", help="Content URL or ID")
parser.add_argument("--url", dest="url_season", help="If set, it will download all assets from the season provided.")
parser.add_argument("--tqdm", dest="tqmd_mode", help="If set, will download with threading", action="store_true")
parser.add_argument("--nv", "--no-video", dest="novideo", help="If set, don't download video", action="store_true")
parser.add_argument("--na", "--no-audio", dest="noaudio", help="If set, don't download audio", action="store_true")
parser.add_argument("--ns", "--no-subs", dest="nosubs", help="If set, don't download subs", action="store_true")
parser.add_argument("--all-season", dest="all_season", help="If set, active download mode.", action="store_true")
parser.add_argument("-e", "--episode", dest="episodeStart", help="If set, it will start downloading the season from that episode.")
parser.add_argument("-s", dest="season", help="If set, it will download all assets from the season provided.")
parser.add_argument("--tag", type=str, required=False, help="Release group tag to use for filenames")
parser.add_argument("-q", "--quality", dest="customquality", type=lambda x: [x.rstrip('p')], help="For configure quality of video.", default=[])
parser.add_argument("-o", "--output", dest="output", default="downloads", help="If set, it will download all assets to directory provided.")
parser.add_argument("--keep", dest="keep", help="If set, it will list all formats available.", action="store_true")
parser.add_argument("--info", help="If set, it will print manifest infos and exit.", action="store_true")
parser.add_argument("--no-mux", dest="nomux", help="If set, dont mux.", action="store_true")
#parser.add_argument("--force-mux", dest="force_mux", nargs=1, help="If set, force mux.", default=[])
#parser.add_argument("--langtag", dest="langtag", nargs=1, help="For configure language tag of MKV.", default=[])
parser.add_argument("--only-2ch-audio", dest="only_2ch_audio", help="If set, no clean tag subtitles.", action="store_true")
parser.add_argument("--alang", "--audio-language", dest="audiolang", nargs="*", help="If set, download only selected audio languages", default=[])
parser.add_argument("--slang", "--subtitle-language", dest="sublang", nargs="*", help="If set, download only selected subtitle languages", default=[])
parser.add_argument("--flang", "--forced-language", dest="forcedlang", nargs="*", help="If set, download only selected forced subtitle languages", default=[])
parser.add_argument("--no-cleansubs", dest="nocleansubs", help="If set, no clean tag subtitles.", action="store_true")
parser.add_argument("--hevc", dest="hevc", help="If set, it will return HEVC manifest", action="store_true")
parser.add_argument("--uhd", dest="uhd", help="If set, it will return UHD manifest", action="store_true")
parser.add_argument("--license", dest="license", help="Only print keys, don't download", action="store_true")
parser.add_argument("-licenses-as-json", help="Save the wv keys as json instead", action="store_true")
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--aformat-51ch", "--audio-format-51ch", dest="aformat_51ch", help="For configure format of audio.")
parser.add_argument("--nc", "--no-chapters", dest="nochpaters", help="If set, don't download chapters", action="store_true")
parser.add_argument("-c", "--codec", choices=["widevine", "playready"], help="Video type to download", default="playready")
parser.add_argument("--ap", dest="audiocodec", default="atmos", choices=["aac", "ac3", "atmos"], help="audio codec profile")

#HBOMAX
parser.add_argument("--atmos", dest="atmos", help="If set, it will return Atmos MPDs", action="store_true")
parser.add_argument("--ad", "--desc-audio", action="store_true", dest="desc_audio", help="Download descriptive audio instead of normal dialogue")
parser.add_argument("--hdr", dest="hdr", help="If set, it will return HDR manifest", action="store_true")
parser.add_argument("-r", "--region", choices=["la", "us"], help="HBO Max video region", default="us")
parser.add_argument("--vp", dest="videocodec", default="h264", choices=["h264", "hevc", "hdr"], help="video codec profile")

#Clarovideo:
parser.add_argument("--m3u8", dest="m3u8mode", help="If set, it will return M3U8 manifest", action="store_true")
parser.add_argument("--file", dest="txtpath", help="If set, it will download links of an txt file")

#DisneyPlus:
parser.add_argument("--tlang", "--title-language", dest="titlelang", nargs=1, help="If set, it will change title language", default="en-US")
parser.add_argument("--scenario1", dest="scenarioDSNP", help="Video API from DisneyPlus", default="chromecast")
parser.add_argument("--scenario2", dest="scenarioSTAR", help="Video API from DisneyPlus", default="restricted-drm-ctr-sw")

#PROXY:
parser.add_argument("--proxy", dest="proxy", help="Proxy URL to use for both fetching metadata and downloading")
#proxy format: http://email@email:password@host:port
args = parser.parse_args()


if args.debug:
	import logging
	logging.basicConfig(level=logging.DEBUG)

currentFile = '__main__'
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
dirName = os.path.basename(dirPath)

if __name__ == "__main__":
	if args.content:
		args.url_season = args.content
	
	if not args.url_season:
		print('Please specify the URL of the content to download.')
		sys.exit(1)

	if (args.url_season and 'hbomax' in args.url_season):
		mode = 'hbomax'
		import hbomax
		hbomax.main(args)
	elif (args.url_season and 'clarovideo' in args.url_season):
		mode = 'clarovideo'
		import clarovideo
		clarovideo.main(args)
	elif (args.url_season and 'blim' in args.url_season):
		mode = 'blimtv'
		import blimtv
		blimtv.main(args)
	elif (args.url_season and 'nowonline' in args.url_season):
		mode = 'nowonline'
		import nowonline
		nowonline.main(args)
	elif (args.url_season and 'globo' in args.url_season):
		mode = 'globoplay'
		import globoplay
		globoplay.main(args)
	elif (args.url_season and 'paramountplus.com' in args.url_season):
		mode = 'paramountplus'
		import paramountplus
		paramountplus.main(args)
	elif (args.url_season and 'disneyplus' in args.url_season):
		mode = 'disneyplus'
		import disneyplus
		disneyplus.main(args)
	elif (args.url_season and 'starplus.com' in args.url_season):
		mode = 'starplus'
		import starplus
		starplus.main(args)
	elif (args.url_season and 'tv.apple.com' in args.url_season):
		mode = 'appletv'
		import appletv
		appletv.main(args)
	elif (args.url_season and 'telecine' in args.url_season):
		mode = 'telecine'
		import telecineplay
		telecineplay.main(args)

	else:
		print("Error! This url or mode is not recognized.")
		sys.exit(0)