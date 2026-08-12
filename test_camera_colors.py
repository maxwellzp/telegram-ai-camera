import cv2
from pathlib import Path
from PIL import Image
from libcamera import Transform
from picamera2 import Picamera2

from config import CAMERA_SIZE


OUTPUT_DIR = Path("photos/color_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


camera = Picamera2()

config = camera.create_video_configuration(
    main={
        "size": CAMERA_SIZE,
        "format": "RGB888",
    },
    transform=Transform(
        hflip=1,
        vflip=1,
    ),
)

camera.configure(config)
camera.start()

frame = camera.capture_array()

camera.stop()
camera.close()

print("Shape:", frame.shape)
print("Dtype:", frame.dtype)
print("First pixel:", frame[0, 0])
print("Min:", frame.min())
print("Max:", frame.max())


# 1. Treat array as RGB
Image.fromarray(frame).save(
    OUTPUT_DIR / "01_pillow_rgb.jpg",
    quality=90,
)


# 2. Treat array as BGR and convert to RGB
rgb = cv2.cvtColor(
    frame,
    cv2.COLOR_BGR2RGB,
)

Image.fromarray(rgb).save(
    OUTPUT_DIR / "02_bgr_to_rgb.jpg",
    quality=90,
)


# 3. OpenCV writes the array directly
cv2.imwrite(
    str(OUTPUT_DIR / "03_opencv_direct.jpg"),
    frame,
)


# 4. Explicit RGB -> BGR before OpenCV writes
bgr = cv2.cvtColor(
    frame,
    cv2.COLOR_RGB2BGR,
)

cv2.imwrite(
    str(OUTPUT_DIR / "04_rgb_to_bgr.jpg"),
    bgr,
)


print()
print("Saved:")
for path in sorted(OUTPUT_DIR.glob("*.jpg")):
    print(path)

# (.venv) maksim@raspberrypi:~/telegram-ai-camera $ python3 test_camera_colors.py 
# [2:02:51.208170888] [8452]  INFO Camera camera_manager.cpp:340 libcamera v0.7.0+rpt20260205
# [2:02:51.218479929] [8465]  INFO RPI pisp.cpp:720 libpisp version 1.3.0
# [2:02:51.235635330] [8465]  INFO IPAProxy ipa_proxy.cpp:180 Using tuning file /usr/share/libcamera/ipa/rpi/pisp/imx708.json
# [2:02:51.245317846] [8465]  INFO Camera camera_manager.cpp:223 Adding camera '/base/axi/pcie@1000120000/rp1/i2c@88000/imx708@1a' for pipeline handler rpi/pisp
# [2:02:51.245428644] [8465]  INFO RPI pisp.cpp:1181 Registered camera /base/axi/pcie@1000120000/rp1/i2c@88000/imx708@1a to CFE device /dev/media2 and ISP device /dev/media1 using PiSP variant BCM2712_C0
# [2:02:51.253419181] [8452]  INFO Camera camera.cpp:1215 configuring streams: (0) 2304x1296-RGB888/Rec709/Rec709/None/Full (1) 2304x1296-RGGB_PISP_COMP1/RAW
# [2:02:51.253718295] [8465]  INFO RPI pisp.cpp:1485 Sensor: /base/axi/pcie@1000120000/rp1/i2c@88000/imx708@1a - Selected sensor format: 2304x1296-SRGGB10_1X10/RAW - Selected CFE format: 2304x1296-PC1R/RAW
# Shape: (1296, 2304, 3)
# Dtype: uint8
# First pixel: [144 150 151]
# Min: 0
# Max: 253

# Saved:
# photos/color_test/01_pillow_rgb.jpg
# photos/color_test/02_bgr_to_rgb.jpg
# photos/color_test/03_opencv_direct.jpg
# photos/color_test/04_rgb_to_bgr.jpg
