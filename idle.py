import logging
from ctypes import Structure, windll, c_uint, sizeof, byref

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

# Function to check user inactivity on Windows
def check_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    logging.debug(millis / 1000.0)
    return millis / 1000.0

# Set the maximum idle duration (in seconds) for the script to run
max_idle_duration = 5  # Adjust as needed