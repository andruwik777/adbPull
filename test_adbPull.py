from unittest import TestCase
import adbPull


class Test(TestCase):
    def test_adb_process_directory(self):
        input = "ola\./la:REG*EX?PRES<SION>-|COOL"
        expected = "ola_DDD_._DDD_la_DDD_REG_DDD_EX_DDD_PRES_DDD_SION_DDD_-_DDD_COOL"
        actual = adbPull.replaceNotAllowedCharactersInWinPath(input)
        self.assertEqual(expected, actual)

    def test_ls_parsing(self):
        dirContent = "drwx------    2      4096 Feb  6  2019 u:object_r:app_data_file:s0      Some filename                 with weird spaces"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(4096, size)
        self.assertEqual("Some filename                 with weird spaces", name)

        dirContent = "drwxrwx--x   26      553 Jan 13 22:06 u:object_r:system_data_file:s0   Longer before filename"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(553, size)
        self.assertEqual("Longer before filename", name)

        dirContent = "-rw-rw-rw-    1    5,   0 Jan 14 09:04 u:object_r:owntty_device:s0      three"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(0, size)
        self.assertEqual("three", name)

        dirContent = "-r--r--r--    1    1 Jan 14 09:04 u:object_r:properties_device:s0  compose"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(1, size)
        self.assertEqual("compose", name)

        dirContent = "drwxr-xr-x    4       960 Jan 14 09:04 u:object_r:block_device:s0       two"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(960, size)
        self.assertEqual("two", name)

        dirContent = "-r--r--r--    1    131072 Jan 14 09:04 u:object_r:properties_device:s0  __properties__"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(131072, size)
        self.assertEqual("__properties__", name)

        dirContent = "drwxr-x--x    8      15 May 10  2017 u:object_r:system_app_data_file:s0 com.android.settings"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(15, size)
        self.assertEqual("com.android.settings", name)

        dirContent = "-rw-------    1         0 Dec  9  2018 u:object_r:app_data_file:s0      Web Data-journal"
        size, name = adbPull.parseLsCommand(dirContent)
        self.assertEqual(0, size)
        self.assertEqual("Web Data-journal", name)
