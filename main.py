# coding=utf-8
# 导入系统命令
import argparse
import os
import sys
from ApkTool import ApkTool
import shutil
# 对 APK 文件进行批处理

def batch_apk(args):
    # 列出 apk 目录下的所有文件
    for f in os.listdir('apk'):
        # 文件名长度超过 4 个字符
        if len(f) > 4:
            # 从后面 4 字节到结尾是 .apk ,
            # 则该文件是 APK 文件 , 对该文件进行解包
            if f[-4:] == '.apk':
                handle('apk/%s'%f, ApkTool(), args)
                break

def handle(apkfile_fullpath, tool, args):
    path, file = os.path.split(apkfile_fullpath)
    if len(path) == 0:
        path = '.'
    apk_filename = file[:-4]
    print("开始处理:", apk_filename)
    unpack_path = path + tool.file_separator + 'unpack' + tool.file_separator + apk_filename
    repack_apk_path = path + tool.file_separator + 'out' + tool.file_separator + apk_filename + '_first.apk'
    align_apk_path = path + tool.file_separator + 'out' + tool.file_separator + apk_filename + '_align.apk'
    sign_path = path + tool.file_separator + 'out' + tool.file_separator + apk_filename + '_sign.apk'
    # apktool打包
    if os.path.exists(path + tool.file_separator + 'out') is False:
        os.makedirs(path + tool.file_separator + 'out')
        print("创建out目录")
    if args.unpack is not None:
        if os.path.exists(unpack_path):
            shutil.rmtree(unpack_path)
            os.makedirs(unpack_path)
            print("创建upack目录")
        tool.unpack(apkfile_fullpath, unpack_path)
    if args.pack is not None:
        if os.path.exists(repack_apk_path) is True:
            os.remove(repack_apk_path)
            print("删除旧的apktool d 生成的apk")
        tool.pack(unpack_path, repack_apk_path)
    if args.sign:
        # zipalign 对齐
        if os.path.exists(align_apk_path) is True:
            os.remove(align_apk_path)
            print("删除旧的对齐apk")
        tool.zipalign(repack_apk_path, align_apk_path)
        # apksigner 签名
        if os.path.exists(sign_path) is True:
            os.remove(sign_path)
            print("删除旧的签名apk")
        tool.sign_with_apk_signer(align_apk_path, sign_path)
        # 自动安装
        print("开始自动安装签名apk:", sign_path)
        install_cmd = 'adb install -r %s' % sign_path
        os.system(install_cmd)


# 主函数入口
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-unpack", action="store_const", help="解压apk包", const="unpack")
    parser.add_argument("-pack", action="store_const", help="打apk包", const="pack")
    parser.add_argument("-sign", action="store_const", help="签名apk包", const="sign")

    batch_apk(parser.parse_args())
