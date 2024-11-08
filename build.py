
import sys
from PyInstaller.__main__ import run

if __name__ == '__main__':
    ##打包参数和选项
    opts = ['--name=SoilFertility-Analysis', '--onefile', '--windowed',
            '--add-data', 'templates/*.html;templates',
            'main.py']
    ##运行PyInstaller命令
    run(opts)
    ## 打包命令 根目录下运行python build.py