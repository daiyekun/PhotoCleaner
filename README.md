# Photo Cleaner - 照片去路人工具

## 图片
<img width="1258" height="887" alt="image" src="https://github.com/user-attachments/assets/734a07f7-dda4-471f-b044-08bda96fd550" />

## 功能特点
- 一键自动去除照片中的路人
- 手动框选方式精确去除路人
- 实时预览处理效果
- 保存处理后的照片

## 环境要求
- Python 3.10+
- Windows 10/11

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 打包成 EXE

```bash
pip install pyinstaller
python build.py
```

打包完成后，EXE 文件位于 `dist` 目录。

## 使用说明
1. 点击"打开图片"加载需要处理的照片
2. 使用"一键去路人"自动检测并去除路人
3. 或使用"手动框选"框住要去除的区域
4. 处理完成后点击"保存图片"保存结果


