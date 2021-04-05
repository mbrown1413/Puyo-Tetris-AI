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

    def old_read_bytes(self, array=False, position=0):
        #TODO: Remove depricated method
        size = int(struct.unpack("<L", self.usb_in.read(4, timeout=0).tobytes())[0])

        data = [0] * size
        if size > 4080:
            i = 0
            while i < size:
                chunkSize = 4080
                if size - i < 4080:
                    chunkSize = size - i
                x = self.usb_in.read(chunkSize, timeout=0).tobytes()

                for j in range(len(x)):
                    data[i] = x[j]
                    i+=1
        else:
            x = self.usb_in.read(size, timeout=0).tobytes()

            #Converts received data to integer array
            for i in range(size):
                data[i] = int(x[i])

        if array:
            if position == -1:
                return data
            return data[position]

        return int.from_bytes(data, byteorder="little", signed=False)
