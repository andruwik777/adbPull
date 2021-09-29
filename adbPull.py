import re
import subprocess
import os
import time
from datetime import datetime
import argparse

STATIC_SKIP_LIST = ["/dev/usb-ffs/adb"]

LONG_FILES_COUNTER = 0
WIN_PATH_SEPARATOR = "\\"
ANDROID_PATH_SEPARATOR = "/"
LOOONG_PATH_FILES_DIR = "_LOOONG_"
LOOONG_FILES_FILENAME = "looongFiles.txt"
LS_DIR_AND_FILES_REGEXP = r"^[-d][xwr-]{9} +.*[^ ] +(.*[^ ]) +(.*[^ ]) +(.*[^ ]) +(.*[^ ]) +.*:.*:.*:[^ ]* +(.*)$"
FORBIDDEN_CHAR_REPLACEMENT_REGEXP = r"_DDD_"
FORBIDDEN_WINPATH_CHARS_REGEX = r"[\\/:*?<>|]"


def log(message):
    print(message, flush=True)


def adb_process_directory(adbPullParams, androidPath, winOutPath, LONG_PATH_DIR, PATH_TO_SKIP):
    command = "adb shell ls -lAZ " + androidPath
    try:
        res = subprocess.run(command,
                             stdout=subprocess.PIPE,
                             text=True,
                             encoding="utf8",
                             timeout=5)
    except Exception:
        log("ERROR: Exception during executing: " + command)
        return

    lines = res.stdout.split("\n\n")

    for dirContent in lines:

        # drwx------    2      4096 Feb  6  2019 u:object_r:app_data_file:s0      dirOrFileIsPlacedHere
        try:
            size, nameOfDirOrFile = parseLsCommand(dirContent)
        except Exception:
            log("ERROR: Exception during parsing size and name of " + dirContent)
            continue

        if not nameOfDirOrFile:
            # skip any warnings and other not interested data
            continue

        if (dirContent.startswith("-")):
            file = nameOfDirOrFile
            dirPath = androidPath if androidPath.endswith(ANDROID_PATH_SEPARATOR) else androidPath + ANDROID_PATH_SEPARATOR
            fullFilePath = file if file.startswith(ANDROID_PATH_SEPARATOR) else dirPath + file

            winFilePath = winOutPath + WIN_PATH_SEPARATOR + replaceNotAllowedCharactersInWinPath(file)

            command = 'adb ' + adbPullParams + ' pull "' + fullFilePath + '" "' + winFilePath + '"'
            try:
                # 6.8 MB/s (109371824 bytes in 15.414s)
                timeout = int(size / 1000000)
                timeout = 5 if timeout < 5 else timeout
                subprocess.run(command, timeout=timeout)
            except Exception:
                log("ERROR: Exception during executing: " + command)
        elif (dirContent.startswith("d")):
            dir = nameOfDirOrFile
            androidDirPath = androidPath + dir if androidPath.endswith(ANDROID_PATH_SEPARATOR) else androidPath + ANDROID_PATH_SEPARATOR + dir

            if androidDirPath in PATH_TO_SKIP:
                log("Skipping " + androidDirPath + " because of script settings")
                continue

            winDirAdjusted = replaceNotAllowedCharactersInWinPath(dir)
            winDirPath = winOutPath + winDirAdjusted if winOutPath.endswith(WIN_PATH_SEPARATOR) else winOutPath + WIN_PATH_SEPARATOR + winDirAdjusted

            if(len(winDirPath) > 255):
                global LONG_FILES_COUNTER
                if(LONG_FILES_COUNTER == 0):
                    os.mkdir(LONG_PATH_DIR)

                LONG_FILES_COUNTER = LONG_FILES_COUNTER + 1
                d = LONG_PATH_DIR + WIN_PATH_SEPARATOR + str(LONG_FILES_COUNTER)
                os.mkdir(d)

                LOONG_FILES_TXT = LONG_PATH_DIR + WIN_PATH_SEPARATOR + LOOONG_FILES_FILENAME
                with open(LOONG_FILES_TXT, 'a+') as f:
                    f.write(str(LONG_FILES_COUNTER) + "_" + winDirPath + "\n")

                winDirPath = d
                adb_process_directory(adbPullParams, androidDirPath, winDirPath, LONG_PATH_DIR, PATH_TO_SKIP)

            else:
                os.mkdir(winDirPath)
                adb_process_directory(adbPullParams, androidDirPath, winDirPath, LONG_PATH_DIR, PATH_TO_SKIP)

def replaceNotAllowedCharactersInWinPath(dir):
    return re.sub(FORBIDDEN_WINPATH_CHARS_REGEX, FORBIDDEN_CHAR_REPLACEMENT_REGEXP, dir)

def parseLsCommand(lsCommandLine):
    parsed = re.search(LS_DIR_AND_FILES_REGEXP, lsCommandLine)
    if not parsed:
        return None, None
    else:
        size = int(parsed.group(1))
        name = parsed.group(5)
        return size, name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wraps adb pull on Windows to copy files/dirs from device',
                                     epilog="This script additionaly overcome issues with not allowed characters in dir names, "
                                            "long path entities (which finally would be stored in " + LOOONG_PATH_FILES_DIR + " directory), "
                                            "adb pull hangs, exceptions etc etc. Allows to skip some paths during pulling.")
    parser.add_argument('REMOTE', nargs='+', help='directories on device to pull')
    parser.add_argument('LOCAL', help='destination path on Windows OS')
    parser.add_argument('-a', action='store_const', const='-a', default='', help='preserve file timestamp and mode')
    parser.add_argument('-z', action='store', metavar='ALGORITHM', help='enable compression with a specified algorithm (any, none, brotli)', choices=['any', 'none', 'brotli'])
    parser.add_argument('-Z', action='store_const', const='-Z', default='', help='disable compression')
    parser.add_argument('-s', action='append', default=[], metavar='path', help='full android path to skip (can be used multiple times like \'-s /sbin -s /proc\' )')
    args = None
    try:
        args = parser.parse_args()
    except SystemExit:
        time.sleep(3)
        exit(-1)

    androidDirsToPull = args.REMOTE
    windowsOutDir = args.LOCAL
    optionPreserveMode = args.a
    optionAlgorithm = ("-z " + args.z) if args.z else ""
    optionDisableCompression = args.Z
    adbPullParams = " ".join([optionPreserveMode, optionAlgorithm, optionDisableCompression])
    PATH_TO_SKIP = args.s
    PATH_TO_SKIP.extend(STATIC_SKIP_LIST)
    LONG_PATH_DIR = windowsOutDir + WIN_PATH_SEPARATOR + LOOONG_PATH_FILES_DIR

    log("STARTED:" + str(datetime.now()))
    for androidDir in androidDirsToPull:
        adb_process_directory(adbPullParams, androidDir, windowsOutDir, LONG_PATH_DIR, PATH_TO_SKIP)
    log("FINISHED:" + str(datetime.now()))
