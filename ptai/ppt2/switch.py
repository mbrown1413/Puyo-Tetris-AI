import struct
import time
from typing import List

import usb


class SwitchDeviceNotFound(Exception):
    pass


def wait_for_connection() -> "Switch":
    while True:
        try:
            switch = Switch()
            print("Connected to Switch Successfully!")
            return switch
        except SwitchDeviceNotFound:
            print("Failed to Connect to Switch!")
            print("Attempting to Reconnect in 5 Seconds...")
            time.sleep(5)


class Switch:

    def __init__(self, vendor_id=0x057E, product_id=0x3000):
        self.usb_dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if self.usb_dev is None:
            raise SwitchDeviceNotFound()

        # Set active config to first one found
        self.usb_dev.set_configuration()

        # Get endpoint instance
        intf = self.usb_dev.get_active_configuration()[(0,0)]

        # Get in/out descriptors
        self.usb_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )
        self.usb_in = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
        )

    def send_command(self, command):
        #print(command)
        self.usb_out.write(struct.pack("<I", (len(command)+2)))
        self.usb_out.write(command)

    def set_sleep_time(self, milliseconds:int):
        """Milliseconds for switch USB-Botbase to sleep after a command.

        Every iteration in USB-Botbase `svcSleepThread(milliseconds*1e6)` is
        called, which is syscall 0x0B. The 1e6 is because svcSleepThread takes
        nanoseconds. See:
        * [svcSleepThread](https://switchbrew.github.io/libnx/svc_8h.html#a0591112f39c2dee78eb9a0a862611fa6)
        * [syscalls](https://switchbrew.org/wiki/SVC)

        Default (in USB-Botbase) is 50.
        """
        self.send_command(f"configure mainLoopSleepTime {milliseconds}")

    def press_button(self, button):
        self.send_command(f"click {button}")

    def hold_button(self, button):
        self.send_command(f"press {button}")

    def release_button(self, button):
        self.send_command(f"release {button}")

    def peek(self, segment, address, size):
        peek_commands = {
            "absolute": "peekAbsolute",
            "main": "peekMain",
            "heap": "peek",
        }
        assert segment in peek_commands, f"Invalid segment: {segment}"
        command = peek_commands[segment]
        self.send_command(f"{command} {hex(address)} {int(size)}")
        return self._read()

    def poke(self, segment, address, data):
        poke_commands = {
            "absolute": "pokeAbsolute",
            "main": "pokeMain",
            "heap": "poke",
        }
        assert segment in poke_commands, f"Invalid segment: {segment}"
        command = poke_commands[segment]
        self.send_command(f"{command} {hex(address)} {data.hex()}")

    def _read(self):
        # Read size of incomming data
        size = int(struct.unpack("<L", self.usb_in.read(4, timeout=0).tobytes())[0])

        # Read data in chunks
        chunks: List[bytes] = []
        MAX_CHUNK_SIZE = 4080
        while size > 0:
            chunk_size = min(MAX_CHUNK_SIZE, size)
            chunk = self.usb_in.read(chunk_size, timeout=0).tobytes()
            chunks.append(chunk)
            size -= chunk_size

        return b''.join(chunks)
