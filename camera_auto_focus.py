#!/usr/bin/python3

import time

from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()


picam2.configure(preview_config)

picam2.start()
time.sleep(3600)

picam2.set_controls({"AfMode": 2, "AfTrigger": 0})
# If your libcamera-dev version is 0.0.10, use the following code.
# AfMode Set the AF mode (manual, auto, continuous)
# For example, single focus: picam2.set_controls({"AfMode": 1 ,"AfTrigger": 0})
#              continuous focus: picam2.set_controls({"AfMode": 2 ,"AfTrigger": 0})

time.sleep(1)
