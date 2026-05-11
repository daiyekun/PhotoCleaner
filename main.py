import sys
import os
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

if sys.base_prefix != sys.prefix:
    system_python = os.path.join(sys.base_prefix, "python.exe")
    if os.path.exists(system_python):
        print("检测到 uv 虚拟环境，正在使用系统 Python 运行...")
        result = subprocess.run([system_python, os.path.join(script_dir, "main.py")])
        sys.exit(result.returncode)

try:
    import tkinter
except ImportError:
    print("错误: 无法导入 tkinter")
    sys.exit(1)

from src.gui import run

if __name__ == "__main__":
    run()
