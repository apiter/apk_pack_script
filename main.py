# coding=utf-8
# 导入系统命令
import argparse
import os


# 对 APK 文件进行批处理
def batch_apk(from_step=0):
    # 列出 apk 目录下的所有文件
    for f in os.listdir('apk'):
        # 文件名长度超过 4 个字符
        if len(f) > 4:
            # 从后面 4 字节到结尾是 .apk ,
            # 则该文件是 APK 文件 , 对该文件进行解包
            if f[-4:] == '.apk':
                os.system('python ApkTool.py -analyse -step %s -inapk apk/%s' % (from_step, f))
                # 只处理一个apk
                break


# 主函数入口
if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    # 默认从第一步开始(apk打包),因为第一步解包可能有很多文件，较耗时，需要时从解包开始指定-s 0
    parse.add_argument('-s', '--step', dest='step', type=int, help='从哪一步开始,0=从解apk开始,1=从压apk开始,2=从对齐签名开始', default=1)
    batch_apk(parse.parse_args().step)
