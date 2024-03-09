from steganography import *


class Degrade(Steganography):

    def __init__(self, c, o, t):
        super().__init__(c, o, t)

    # 图像退化隐写
    def hide(self):

        if not Steganography.hide(self):
            return False

        # 打开目标图像
        try:
            self.target = Image.open(self.target_file)
        except (FileNotFoundError, FileExistsError):
            print(f"[-]Can not open file {self.target_file}")

        (width_target, height_target) = self.target.size

        # 判断载体是否足够大
        if width_target > self.carrier_width or height_target > self.carrier_height:
            print("[-]The carrier is too small to embed data")
            return False

        if self.target.mode != self.carrier_mode:
            print("[-]Carrier image and Target image doesn't match")
            return False

        # 隐写图像
        index_y = 0
        for y in range(self.carrier_height):
            index_x = 0
            for x in range(self.carrier_width):
                carrier_rgb = self.carrier.getpixel((x, y))
                if index_x < width_target and index_y < height_target:
                    target_rgb = self.target.getpixel((x, y))
                    index_x += 1
                else:
                    if self.carrier_mode == 'RGBA':
                        target_rgb = (0, 0, 0)
                    else:
                        target_rgb = (0, 0, 0, 0)
                new_rgb = []
                for channel in range(len(carrier_rgb)):
                    new_rgb.append((carrier_rgb[channel] & 0xf0) | ((target_rgb[channel] & 0xf0) >> 4))

                self.output.putpixel((x, y), tuple(new_rgb))
            index_y += 1

        self.output.save(self.output_file)

        self.carrier.close()
        self.target.close()
        return True

    # 提取退化隐写图像
    def extract(self):
        if not Steganography.extract(self):
            return False

        # 创建输出文件
        self.output = self.carrier.copy()

        for y in range(self.carrier_height):
            for x in range(self.carrier_width):
                carrier_rgb = self.carrier.getpixel((x, y))
                new_rgb = []
                for channel in range(len(carrier_rgb)):
                    new_rgb.append((carrier_rgb[channel] & 0x0f) << 4)
                self.output.putpixel((x, y), tuple(new_rgb))

        self.output.save(self.output_file)
        self.carrier.close()
        return True

