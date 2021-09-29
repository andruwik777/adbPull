from unittest import TestCase
import re

import adbPull


class Test(TestCase):
    def test_adb_process_directory(self):
        input = "ola\./la:REG*EX?PRES<SION>-|COOL"
        expected = "ola_DDD_._DDD_la_DDD_REG_DDD_EX_DDD_PRES_DDD_SION_DDD_-_DDD_COOL"
        actual = adbPull.replaceNotAllowedCharactersInWinPath(input)
        self.assertEqual(expected, actual)

    def test_ls_parsing(self):
        dirContent = "drwx------    2      4096 Feb  6  2019 u:object_r:app_data_file:s0      Some filename                 with weird spaces"
        self.assertEqual("Some filename                 with weird spaces", adbPull.getNameFromLsCommand(dirContent))

        dirContent = "drwxrwx--x   26      4096 Jan 13 22:06 u:object_r:system_data_file:s0   Longer before filename"
        self.assertEqual("Longer before filename", adbPull.getNameFromLsCommand(dirContent))

        dirContent = "-rw-rw-rw-    1    5,   0 Jan 14 09:04 u:object_r:owntty_device:s0      three"
        self.assertEqual("three", adbPull.getNameFromLsCommand(dirContent))

        dirContent = "-r--r--r--    1    131072 Jan 14 09:04 u:object_r:properties_device:s0  compose"
        self.assertEqual("compose", adbPull.getNameFromLsCommand(dirContent))

        dirContent = "drwxr-xr-x    4       960 Jan 14 09:04 u:object_r:block_device:s0       two"
        self.assertEqual("two", adbPull.getNameFromLsCommand(dirContent))

        dirContent = "-r--r--r--    1    131072 Jan 14 09:04 u:object_r:properties_device:s0  __properties__"
        self.assertEqual("__properties__", adbPull.getNameFromLsCommand(dirContent))

        dirContent = "drwxr-x--x    8      4096 May 10  2017 u:object_r:system_app_data_file:s0 com.android.settings"
        self.assertEqual("com.android.settings", adbPull.getNameFromLsCommand(dirContent))

        dirContent = "-rw-------    1         0 Dec  9  2018 u:object_r:app_data_file:s0      Web Data-journal"
        self.assertEqual("Web Data-journal", adbPull.getNameFromLsCommand(dirContent))

