## adbPull
Wraps 'adb pull' on Windows to copy files/dirs from device.  
This script additionaly overcome issues with not allowed characters in dir names, long path entities (which finally would be stored in separate directory), hangs, exceptions etc etc.
In addition to standard adb pull flags it also allows to skip some paths during pulling.

---

### Sample of using:
```
python adbPull.py /data/data C:\tmp
```
or just read man :)
```
python adbPull.py --help
```

P.S. I'd suggest to redirect output to file for investigation log in case of any errors.
```
python adbPull.py /data/data C:\tmp > logfile.txt
```
