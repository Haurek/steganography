from steganography import *
from crypt import *
import random


# 加密数据并生成签名
def generate_encrypt_data(data, pub_key, pri_key):
    public_key = get_rsa_key(pub_key)
    private_key = get_rsa_key(pri_key)

    # 随机生成AES密钥
    aes_key = generate_aes128_key()

    # AES加密嵌入信息
    encrypted_text = aes128_encrypt(data, aes_key)

    # RSA加密AES密钥
    encrypted_key = rsa_encrypt(aes_key, public_key)
    encrypted_data = encrypted_key + encrypted_text

    # 生成签名
    h = SHA256.new(encrypted_data)
    signature = pkcs1_15.new(private_key).sign(h)
    payload = signature + encrypted_data

    # 计算payload长度,用6byte保存
    length = len(payload).to_bytes(6, 'big')

    return length, payload


# 验证和解密数据
def decrypt_data(payload, pri_key, pub_key):
    print("[+]Decrypt data...")
    public_key = get_rsa_key(pub_key)
    private_key = get_rsa_key(pri_key)

    # 验证签名
    sig = payload[:128]
    h = SHA256.new(payload[128:])
    try:
        pkcs1_15.new(public_key).verify(h, sig)
        print("[+]verify successfully!")
    except (ValueError, TypeError):
        print("[-]verify fail")
        return False

    # 获取AES密钥
    aes_key = rsa_decrypt(payload[128:128 * 2], private_key)

    # 解密信息
    return aes128_decrypt(payload[128 * 2:], aes_key)


# 获取像素点的LSB
def get_lsb(pixel, lsb_bits):
    for channel in pixel:
        lsb_bits.append(channel & 1)


# 设置像素点的LSB
def set_lsb(pixel, bits):
    new_pixel = list(pixel)
    for channel in range(len(bits)):
        new_pixel[channel] = (pixel[channel] & 254 | bits[channel])
    return tuple(new_pixel)


class LSB(Steganography):

    def __init__(self, c, o, t):
        super().__init__(c, o, t)
        self.data = None
        self.is_text = False
        self.is_encrypt = False
        self.public_key = None
        self.private_key = None

    # 设置加密模式，添加公钥和私钥pem文件
    def set_encrypt_mode(self, encrypt, pub_key, pri_key):
        self.is_encrypt = encrypt
        self.private_key = pri_key
        self.public_key = pub_key

    # 设置纯文本输出
    def output_text(self, text):
        self.is_text = text

    # 伪随机数生成随机坐标
    def get_random_map(self, length, x_min, x_max, y_min, y_max):
        addresses = set()

        # 利用payload长度设置伪随机数种子
        random.seed(length)

        # 计算需要的像素点个数
        if self.carrier_mode == 'RGBA':
            num = int((length * 8) / 4) + 1
        else:
            num = int((length * 8) / 3) + 1

        while len(addresses) < num:
            x = random.randint(x_min, x_max - 1)
            y = random.randint(y_min, y_max - 1)
            # RGBA下预留前12个像素点，RGB下预留16个
            # 保证6个byte的LSB保存长度信息
            if y == 0 and ((x in range(16) and self.carrier_mode == 'RGB') or (
                    x in range(12) and self.carrier_mode == 'RGBA')):
                continue
            addresses.add((x, y))

        return list(addresses)

    # 设置最低有效位，从第一个像素点开始
    def set_data(self, bits):
        index_bit = 0
        gap = 3
        if self.carrier_mode == 'RGBA':
            gap = 4

        for y in range(self.carrier_height):
            for x in range(self.carrier_width):
                if index_bit >= len(bits):
                    return True
                try:
                    self.output.putpixel((x, y), set_lsb(self.carrier.getpixel((x, y)), bits[index_bit:index_bit + gap]))
                except IndexError:
                    print(f"[-]Fail to set data at {x, y}")
                    return False
                index_bit += gap

        return True

    # 设置最低有效位为加密数据
    def set_encrypt_data(self, bits, length):
        print("[+]Generate random bit map...")
        random_bmp = self.get_random_map(length, 0, self.carrier_width, 0, self.carrier_height)

        index_bit = 0
        gap = 3
        if self.carrier_mode == 'RGBA':
            gap = 4

        print("[+]Set encrypt data...")

        for addr in random_bmp:
            x = addr[0]
            y = addr[1]
            if index_bit + gap >= len(bits):
                gap = len(bits) - index_bit
            try:
                self.output.putpixel((x, y), set_lsb(self.carrier.getpixel((x, y)), bits[index_bit:index_bit + gap]))
            except IndexError:
                print(f"[-]Fail to set data at {x, y}")
                return False
            index_bit += gap
            if index_bit == len(bits):
                return True

        return True

    # 从最低有效位获取指定大小的加密数据
    def get_encrypt_data(self, length):
        print("[+]Generate random bit map...")
        random_bmp = self.get_random_map(length, 0, self.carrier_width, 0, self.carrier_height)

        print("[+]Get encrypt data...")

        lsb_bits = []
        index_bit = 0
        for addr in random_bmp:
            x = addr[0]
            y = addr[1]
            if index_bit >= length * 8:
                return bits2bytes(lsb_bits[:length * 8])
            get_lsb(self.carrier.getpixel((x, y)), lsb_bits)
            if self.carrier_mode == 'RGBA':
                index_bit += 4
            else:
                index_bit += 3

        return bits2bytes(lsb_bits[:length * 8])

    # 从第一个像素点开始获取指定长度最低有效位
    def get_data(self, length):
        lsb_bits = []
        index_bit = 0
        for y in range(self.carrier_height):
            for x in range(self.carrier_width):
                if index_bit >= length * 8:
                    return bits2bytes(lsb_bits[:length * 8])
                get_lsb(self.carrier.getpixel((x, y)), lsb_bits)
                if self.carrier_mode == 'RGBA':
                    index_bit += 4
                else:
                    index_bit += 3

        return bits2bytes(lsb_bits)

    # 最低有效位隐藏信息
    def hide(self):

        if not Steganography.hide(self):
            return False

        if self.carrier_mode == 'RGB':
            cap = self.carrier_width * self.carrier_height * 3
        elif self.carrier_mode == 'RGBA':
            cap = self.carrier_width * self.carrier_height * 4
        else:
            print(f"[-]{self.carrier_mode} mode can not use for LSB steganography")
            return False

        print(f"[+]Carrier capacity {int(cap / 8)} byte")

        # 获取目标文件字节信息
        try:
            self.target = open(self.target_file, "rb")
        except(FileNotFoundError, FileExistsError):
            print(f"[-]Can not open file {self.target_file}")
        target_data = self.target.read()

        print(f"[+]Target capacity {len(target_data)} byte")

        # 判断载体是否足够大
        if len(target_data) * 8 > cap:
            print("[-]The carrier is too small to embed data")
            return False

        # 加密隐写内容
        if self.is_encrypt:
            print("[+]Message encryption...")
            # 判断载体是否能嵌入加密信息
            if (len(target_data) + 6 + 32) * 8 > cap:
                print("[-]The carrier is too small to embed the encrypted data")
                print("[-]Will embed in non-encrypted mode")
            else:
                # 生成加密数据和签名
                length, encrypt_data = generate_encrypt_data(target_data, self.public_key, self.private_key)
                print(f"[+]Encrypt complete, payload size: {len(encrypt_data)} byte")
                # 前6个字节设置长度
                self.set_data(bytes2bits(length))
                # 设置加密信息
                if not self.set_encrypt_data(bytes2bits(encrypt_data), len(encrypt_data)):
                    return False
        else:
            # 隐写信息嵌入最低有效位
            self.set_data(bytes2bits(target_data))

        # 保存嵌入了目标图像的载体图像
        self.output.save(self.output_file)

        self.carrier.close()
        self.target.close()
        return True

    # 提取最低有效位信息
    def extract(self):
        if not Steganography.extract(self):
            return False

        # 嵌入信息存在加密
        if self.is_encrypt:
            print("[+]Message decryption...")
            # 取出前6byte数据得到payload长度
            length = int.from_bytes(self.get_data(6), 'big')
            print(f"[+]Payload size: {length} byte")
            # 根据定义的加密形式提取并解密信息
            self.data = decrypt_data(self.get_encrypt_data(length), self.private_key, self.public_key)
            if not self.data:
                return False
        # 没有加密直接提取信息
        else:
            self.data = self.get_data(self.carrier_width * self.carrier_height)

        # 输出纯文本
        if self.is_text:
            plain_text = ""
            for i in self.data:
                plain_text += chr(i)
            print("[+]Output plain text:")
            print(plain_text)
        # 输出到文件
        else:
            try:
                self.output = open(self.output_file, "wb")
                self.output.write(self.data)
                self.output.close()
            except(FileNotFoundError, FileExistsError):
                print(f"[-]Can not open file {self.output_file}")

        self.carrier.close()
        return True
