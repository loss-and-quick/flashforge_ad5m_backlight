from fcntl import ioctl
from struct import pack
import argparse

DISP_LCD_SET_BRIGHTNESS = 0x102
DISP_LCD_GET_BRIGHTNESS = 0x103
DISP_LCD_BACKLIGHT_ENABLE = 0x104
DISP_LCD_BACKLIGHT_DISABLE = 0x105

def backlight_enable(enable=True):
    if enable:
        ctl = DISP_LCD_BACKLIGHT_ENABLE
    else:
        ctl = DISP_LCD_BACKLIGHT_DISABLE
    with open("/dev/disp", "wb") as f:
        ioctl(f, ctl, b"")

def backlight_get():
    with open("/dev/disp", "wb") as f:
        buffer = bytearray(4)
        value = ioctl(f, DISP_LCD_GET_BRIGHTNESS, buffer)
    return value

def backlight_set(value):
    with open("/dev/disp", "wb") as f:
        ioctl(f, DISP_LCD_SET_BRIGHTNESS, pack("=L", 0) + pack("=L", int(value)))

def parse_brightness(value_str):
    if value_str is None:
        return None
    
    value_str = str(value_str).strip()
    
    if value_str.endswith('%'):
        try:
            percent = float(value_str[:-1])
            if not (0 <= percent <= 100):
                raise argparse.ArgumentTypeError("percentage value must be within 0-100%")
            return int(percent * 255 / 100) if percent > 0 else 0
        except ValueError:
            raise argparse.ArgumentTypeError("invalid percentage value")
    
    try:
        value = float(value_str)
        if not (0 <= value <= 255):
            raise argparse.ArgumentTypeError("absolute value must be within 0-255")
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("value must be a number or percentage (e.g., 50 or 50%)")

def main():
    parser = argparse.ArgumentParser(
        prog="FF AD5M Backlight control",
        description='Control the backlight. Supports 0-255 (absolute) or 0%-100% (percentage). 0 disables backlight.',
        epilog="See https://github.com/consp/flashforge_ad5m_backlight and https://github.com/xblax/flashforge_adm5_klipper_mod")

    parser.add_argument(
            'brightness',
            type=parse_brightness,
            nargs='?',
            help="brightness: 0-255 (absolute) or 0%%-100%% (percentage). 0 disables, nothing returns current value",
            )

    args = parser.parse_args()
    brightness_value = args.brightness

    if brightness_value is None:
        current = backlight_get()
        percent = int(current * 100 / 255)
        print(f"Current brightness: {current}/255 ({percent}%)")
    elif brightness_value == 0:
        backlight_enable(False)
        print("Backlight disabled")
    else:
        backlight_enable(True)
        backlight_set(brightness_value)
        percent = int(brightness_value * 100 / 255)
        print(f"Brightness set: {brightness_value}/255 ({percent}%)")

if __name__ == "__main__":
    main()