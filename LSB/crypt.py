from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto import Random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


# 生成128位的AES密钥
def generate_aes128_key():
    return get_random_bytes(16)


# 生成RSA公钥和私钥
def generate_rsa_key(pub_file, pri_file):
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()

    private_pem = private_key.export_key().decode()
    public_pem = public_key.export_key().decode()

    with open(pri_file, 'w') as pr:
        pr.write(private_pem)
    with open(pub_file, 'w') as pu:
        pu.write(public_pem)

    return private_key, public_key


# 读取密钥文件
def get_rsa_key(key_file):
    try:
        key = open(key_file, "r")
        return RSA.import_key(key.read())
    except(FileNotFoundError, FileExistsError):
        print(f"[-]Can not open file {key_file}")
        return None


# AES加密
def aes128_encrypt(data, key):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(data, AES.block_size))


# AES解密
def aes128_decrypt(enc, key):
    iv = enc[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[AES.block_size:]), AES.block_size)


# RSA加密
def rsa_encrypt(data, pub_key):
    cipher = PKCS1_OAEP.new(key=pub_key)
    return cipher.encrypt(data)


# RSA解密
def rsa_decrypt(enc, pri_key):
    cipher = PKCS1_OAEP.new(key=pri_key)
    return cipher.decrypt(enc)
