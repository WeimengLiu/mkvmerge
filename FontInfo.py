from fontTools.ttLib import TTFont
from fontTools.ttLib import TTCollection
import os
import argparse




def extract_font_names(file_path):
    # 使用 os.path.splitext() 函数提取文件后缀名
    file_extension = os.path.splitext(file_path)[1]
    font_families = set()
    if file_extension.lower().endswith(("ttf","otf")) :
        font = TTFont(file_path)
        #print(font['name'].getName())
        for record in font['name'].names:
            if record.nameID == 1:
                font_family = record.toStr()
                font_families.add(font_family)
    
        # 关闭字体文件
        font.close()
    
    if file_extension.lower().endswith(("ttc")) :
        # 打开字体集文件
        collection = TTCollection(file_path)

        # 获取字体集中的字体数量
        #num_fonts = len(collection.fonts)
        #print("Number of fonts in the collection:", num_fonts)

        # 打印每个字体的基本信息
        for i, font in enumerate(collection.fonts):
            #print("\nFont", i+1)
            for record in font['name'].names:
                if record.nameID == 1:
                    font_family = record.toStr()
                    font_families.add(font_family)

        # 关闭字体集文件
        collection.close()
    return font_families

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract font names from Font file')
    parser.add_argument('file_path', help='Path to the Font file')

    args = parser.parse_args()
    file_path = args.file_path

    font_names = extract_font_names(file_path)
    for font_name in font_names:
        print(font_name)