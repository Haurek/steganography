import sys
from optparse import OptionParser
from lsb import *
from degrade import *

if __name__ == "__main__":
    # generate_rsa_key("./public_send.pem", "./private_send.pem")
    # generate_rsa_key("./public_recv.pem", "./private_recv.pem")
    parser = OptionParser()
    parser.add_option("-M", "--mode", dest="mode", action="store_true", help="Enable LSB steganography")
    parser.add_option("-H", "--hide", dest="hide", action="store_true", help="Hide message")
    parser.add_option("-c", "--carrier", dest="carrier_image", help="Carrier image filename")
    parser.add_option("-t", "--targe", dest="targe_filename", help="Targe filename")
    parser.add_option("-E", "--extract", dest="extract", action="store_true", help="Extract message")
    parser.add_option("-T", "--text", dest="is_text", action="store_true", help="Output string")
    parser.add_option("-K", "--Key", dest="Key", action="store_true", help="Encrypt mode")
    parser.add_option("-o", "--output", dest="output_filename", help="Output filename")
    parser.add_option("--pub", "--public", dest="public_key", help="RSA public key")
    parser.add_option("--pri", "--private", dest="private_key", help="RSA private key")
    (options, args) = parser.parse_args()

    if len(sys.argv) < 4 or (not options.hide and not options.extract):
        print("Usage: LSB.py [options]\n")
        print("Options:")
        print("-M, enable LSB mode")
        print("-H, hide message into image file")
        print("-E, extract message from image file")
        print("-c, carrier image file")
        print("-t, target file to hide")
        print("-o, output file")
        print("-K, encryption mode")
        print("-pub, RSA public key file")
        print("-pri, RSA private key file")

    else:
        if options.mode:
            print("[+]Steganography in LSB mode")
            lsb = LSB(options.carrier_image, options.output_filename, options.targe_filename)
            if options.hide:
                print("[+]Hide data...")
                if options.Key:
                    lsb.set_encrypt_mode(True, options.public_key, options.private_key)
                if lsb.hide():
                    print("[+]Hide completion")
                else:
                    print("[-]Hide fail")
            else:
                print("[+]Extract data...")
                if options.is_text:
                    lsb.output_text(True)
                if options.Key:
                    lsb.set_encrypt_mode(True, options.public_key, options.private_key)
                if lsb.extract():
                    print("[+]Extract complete")
                else:
                    print("[-]Extract fail")

        else:
            print("[+]Steganography in Degrade mode")
            degrade = Degrade(options.carrier_image, options.output_filename, options.targe_filename)
            if options.hide:
                print("[+]Hide data...")
                if degrade.hide():
                    print("[+]Hide completion")
                else:
                    print("[-]Hide fail")
            else:
                print("[+]Extract data...")
                if degrade.extract():
                    print("[+]Extract complete")
                else:
                    print("[-]Extract fail")
