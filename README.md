apk解压及二次打包脚本

【keystore配置】
工程自带了keystore文件，如果不需要，可以在config.ini文件中配置自己的

【命令使用方式】

将要处理的apk放到apk工程文件夹

python main.py -unpack # 解包apk，会在apk目录下生成相应的文件夹

python main.py -pack   # 对unpack的目录进行重新打包, 一般在解压apk包，并进行完相应修改后运行

python main.py -sign   # 对pack生成的包进行签名，生成*_sign.apk同名文件
