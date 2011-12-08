'''
Ingests new GPS track logs from the WBT202.
'''
from ctypes import windll
from string import ascii_uppercase
import datetime
import re
import os
import subprocess
import time

II3 = r"C:\Program Files\ImageIngesterPro3\ImageIngesterPro.exe"
BABEL = r"C:\Program Files\GPSBabel\gpsbabel.exe"
OUTPUT = r"C:\temp\gps.gpx"
OLDEST_PHOTO_IN_DAYS = 14

def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives

def get_file_list():
    '''Finds the latest track log file.'''
    for drive_letter in get_drives():
        wbt202 = drive_letter+':\\WBT202'
        if os.path.exists(wbt202):
            # found the directory
            file_list = []
            for (dirpath, dirnames, filenames) in os.walk(wbt202):
                for filename in filenames:
                    if re.search(r"\.TES", filename):
                        file_list.append(os.path.join(dirpath, filename))
            return file_list
    raise "No WBT202 directory found"

def build_command_line():
    files = get_file_list()
    args = [BABEL]
    for file in files:
        args.extend(['-i', 'wintec_tes', '-f', file])

    today = datetime.date.today()
    delta = datetime.timedelta(OLDEST_PHOTO_IN_DAYS)
    start_date = today - delta
    start_arg = '%04d%02d%02d' % (start_date.year, start_date.month, start_date.day)
    args.extend(['-x', 'track,merge,start=' + start_arg])
    args.extend(['-o', 'gpx', '-F', OUTPUT])
    return args

def run_babel():
    args = build_command_line()
    retcode = subprocess.call(args)
    if retcode != 0:
        raise "GPSBabel exited with " + retcode

def run_imageingester():
    subprocess.call([II3])

if __name__ == '__main__':
    print "Running GPSBabel"
    run_babel()
    print "Running ImageIngester"
    run_imageingester()
