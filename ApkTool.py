# coding=utf-8
import os
import shutil
import argparse
from subprocess import Popen, PIPE

import sys
import importlib

importlib.reload(sys)


class ApkTool:
    def __init__(self, keystore=None, password=None, alias=None):
        if sys.platform == 'win32':
            self.file_separator = '\\'
        else:
            self.file_separator = '/'
        path = ''
        if hasattr(sys, '_MEIPASS'):
            path = sys._MEIPASS + self.file_separator
        self.apk_tool_jar = path + 'apktool_2.9.1.jar'
        self.aapt = path + 'aapt.exe'
        self.objdump_x86 = path + 'objdump_x86.exe'
        self.objdump_arm = path + 'objdump_arm.exe'
        if keystore is None:
            self.keystore = path + 'test_abc123'
        else:
            self.keystore = keystore
        if password is None:
            self.password = 'abc123'
        else:
            self.password = password
        if alias is None:
            self.alias = 'abc123'
        else:
            self.alias = alias
        self.cur_apk = {}
        return

    def unpack(self, apk, path):
        cmd = 'java -jar ' + self.apk_tool_jar + (' d -f -o %s %s' % (path, apk))
        print("unpack命令:", cmd)
        os.system(cmd)
        print("unpack完成!!!")
        return

    def pack(self, path, apk):
        cmd = 'java -jar ' + self.apk_tool_jar + (' b %s -o %s' % (path, apk))
        print("pack命令:", cmd)
        os.system(cmd)
        print("pack完成!!!")
        return

    def sign_with_apk_signer(self, apk_path, signed_apk_path):
        keystore = '--ks %s --ks-key-alias %s --ks-pass pass:%s' % (self.keystore, self.alias, self.password)
        cmd = "apksigner sign %s --in %s --out %s" % (keystore, apk_path, signed_apk_path)
        print("签名命令:", cmd)
        os.system(cmd)
        print("签名结束!!!")
        return

    @staticmethod
    def zipalign(apk_path, apk_align_path):
        cmd = 'zipalign -p -f -v 4 %s %s' % (apk_path, apk_align_path)
        print("对齐命令:", cmd)
        os.system(cmd)
        print("对齐结束!!!")
        return

    def get_apk_label(self, apk_path):
        pipe = Popen([self.aapt, 'dump', 'badging', apk_path], stdout=PIPE)
        if pipe is not None:
            while True:
                line = pipe.stdout.readline()
                line = line.decode('utf-8')
                if len(line) == 0:
                    break
                pos = line.find('application-label:')
                if pos != -1:
                    return line[pos + 19:len(line) - 3]  # \r\n占了2个，加上单引号一共3个字符
        return ''

    def get_apk_package_name(self, apk):
        pipe = Popen([self.aapt, 'dump', 'badging', apk], stdout=PIPE)
        if pipe is not None:
            while True:
                line = pipe.stdout.readline()
                line = line.decode('utf-8')
                if len(line) == 0:
                    break
                pos = line.find('package:')
                if pos != -1:
                    return line[pos + 8:len(line) - 2]  # \r\n占了2个，加上单引号一共3个字符
        return ''


def get_game_engine(libpath, file_separator):
    data = {
        'libcocos2dcpp.so': 'cocos引擎 cpp',
        'libcocos2dlua.so': 'cocos引擎 lua',
        'libcocos2djs.so': 'cocos引擎 javascipt',
        'libunity.so': 'unity3D引擎',
        'libgdx.so': 'libgdx引擎'
    }
    arch_dir = ['armeabi-v7a', 'armeabi', 'x86']
    for d in arch_dir:
        lib = libpath + d + file_separator
        for f in data.keys():
            if os.path.exists(lib + f):
                return data[f]
    return '未知引擎'


def analyse(apk, tool, step):
    path, file = os.path.split(apk)
    if len(path) == 0:
        path = '.'
    out_name = file[:-4]
    print("开始处理:", out_name)
    unpack_path = path + tool.file_separator + 'unpack' + tool.file_separator + out_name
    repack_apk_path = path + tool.file_separator + 'out' + tool.file_separator + out_name + '_first.apk'
    align_apk_path = path + tool.file_separator + 'out' + tool.file_separator + out_name + '_align.apk'
    sign_path = path + tool.file_separator + 'out' + tool.file_separator + out_name + '_sign.apk'
    # apktool打包
    if os.path.exists(path + tool.file_separator + 'out') is False:
        os.makedirs(path + tool.file_separator + 'out')
        print("创建out目录")
    if step == 0:
        if os.path.exists(unpack_path):
            shutil.rmtree(unpack_path)
            os.makedirs(unpack_path)
            print("创建upack目录")
        tool.unpack(apk, unpack_path)
    if step <= 1:
        if os.path.exists(repack_apk_path) is True:
            os.remove(repack_apk_path)
            print("删除旧的apktool d 生成的apk")
        tool.pack(unpack_path, repack_apk_path)
    if step <= 2:
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


def main():
    parser = argparse.ArgumentParser(prog=sys.argv[0], usage='%(prog)s [options]')
    help = """help 或者 -h 显示本帮助文档 """
    parser.add_argument('-help', help=help, action='store_const', const='help')
    parser.add_argument('-analyse', help='分析包', action='store_const', const='analyse')
    parser.add_argument('-step', nargs='?', type=int, help='开始步骤')
    parser.add_argument('-inapk', nargs='?', help='指定输入apk路径')
    args = parser.parse_args()
    if args.help is not None:
        parser.print_help()
        return
    attrs = ['inapk', 'help', 'step']
    value_map = {}
    for attr in attrs:
        value_map[attr] = getattr(args, attr, None)
    tool = ApkTool()
    step = value_map['step']
    print("开始步骤:", step)

    if args.analyse is not None:
        if value_map['inapk'] is None:
            print('需要指定输入游戏包，现在分析当前目录下所有的apk文件')
            for file in os.listdir(os.curdir):
                if os.path.isdir(file):
                    continue
                if os.path.splitext(file)[1] == '.apk':
                    analyse(file, tool, step)
            return
        analyse(value_map['inapk'], tool, step)
        return
    parser.print_help()


if __name__ == '__main__':
    main()
