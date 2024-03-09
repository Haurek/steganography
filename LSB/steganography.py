from PIL import Image


def bits2bytes(bit_array):
    byte_array = bytearray()
    for i in range(0, len(bit_array), 8):
        byte_value = 0
        for j in range(8):
            if i + j < len(bit_array):
                byte_value = (byte_value << 1) | bit_array[i + j]
        byte_array.append(byte_value)
    return bytes(byte_array)


def bytes2bits(byte_array):
    bit_array = []
    for byte in byte_array:
        bits = [int(bit) for bit in format(byte, '08b')]
        bit_array.extend(bits)
    return bit_array


class Steganography:

    def __init__(self, c, o, t):
        self.carrier = None
        self.output = None
        self.target = None
        self.carrier_image = c
        self.output_file = o
        self.target_file = t
        self.carrier_mode = None
        self.target_mode = None
        self.carrier_width = 0
        self.carrier_height = 0

    def hide(self):
        # 打开载体图片
        try:
            self.carrier = Image.open(self.carrier_image)
        except(FileNotFoundError, FileExistsError):
            print(f"[-]Can not open file {self.carrier_image}")
            return False

        self.carrier_mode = self.carrier.mode

        if self.carrier_mode != 'RGB' and self.carrier_mode != 'RGBA':
            print(f"[-]Carrier image is {self.carrier_mode} mode can not use for steganography")
            return False

        self.carrier_width = self.carrier.size[0]
        self.carrier_height = self.carrier.size[1]

        # 创建输出图片
        self.output = self.carrier.copy()

        return True

    def extract(self):
        # 打开载体图片
        try:
            self.carrier = Image.open(self.carrier_image)
        except(FileNotFoundError, FileExistsError):
            print(f"[-]Can not open file {self.carrier_image}")
            return False

        self.carrier_mode = self.carrier.mode

        if self.carrier_mode != 'RGB' and self.carrier_mode != 'RGBA':
            print(f"[-]Carrier image is {self.carrier_mode} mode can not use for steganography")
            return False

        self.carrier_width = self.carrier.size[0]
        self.carrier_height = self.carrier.size[1]

        return True
