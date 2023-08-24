from PIL import Image
import glob
import os
class CompareImage():
    def calculate(self, image1, image2):
        g = image1.histogram()
        s = image2.histogram()
        assert len(g) == len(s), "error"
 
        data = []
 
        for index in range(0, len(g)):
            if g[index] != s[index]:
                data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
            else:
                data.append(1)
 
        return sum(data) / len(g)
 
    def split_image(self, image, part_size):
        pw, ph = part_size
        w, h = image.size
 
        sub_image_list = []
 
        assert w % pw == h % ph == 0, "error"
 
        for i in range(0, w, pw):
            for j in range(0, h, ph):
                sub_image = image.crop((i, j, i + pw, j + ph)).copy()
                sub_image_list.append(sub_image)
 
        return sub_image_list
 
 
    def compare_image(self, file_image1, file_image2, size=(256, 256), part_size=(64, 64)):
        '''
        'file_image1'和'file_image2'是传入的文件路径
         可以通过'Image.open(path)'创建'image1' 和 'image2' Image 对象.
         'size' 重新将 image 对象的尺寸进行重置，默认大小为256 * 256 .
         'part_size' 定义了分割图片的大小.默认大小为64*64 .
         返回值是 'image1' 和 'image2'对比后的相似度，相似度越高，图片越接近，达到1.0说明图片完全相同。
        '''
 
        image1 = Image.open(file_image1)
        image2 = Image.open(file_image2)
 
        #调用"split_image"函数，把图片切割，并分别放在数组中
        img1 = image1.resize(size).convert("RGB")
        sub_image1 = self.split_image(img1, part_size)
 
        img2 = image2.resize(size).convert("RGB")
        sub_image2 = self.split_image(img2, part_size)
 
        sub_data = 0
        #把切割好的照片，从数组中一一对应的提出来，传入"calculate"函数，做直方图比较
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)
 
        x = size[0] / part_size[0]
        y = size[1] / part_size[1]
  
        pre = round((sub_data / (x * y)), 6)
        # print(str(pre * 100) + '%')
 
        print('Compare the image result is: ' + str(pre))
        return pre
 
 
if __name__ == '__main__':
    img1 =  '/Users/yizhilaomuzhu/Downloads/喵2.jpg'
    img2 =  '/Users/yizhilaomuzhu/Downloads/喵3.jpg'
    compare_image = CompareImage()
    compare_image.compare_image(img1,img2)
 
 