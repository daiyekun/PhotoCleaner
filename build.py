import PyInstaller.__main__

PyInstaller.__main__(
    [
        "main.py",
        "--name=PhotoCleaner",
        "--onefile",
        "--windowed",
        "--add-data=src;src",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--clean",
    ]
)
