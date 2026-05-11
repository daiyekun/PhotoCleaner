# AGENTS.md - PhotoCleaner Development Guide

## Project Overview
PhotoCleaner is a simple desktop application for removing unwanted objects/people from photos using OpenCV inpainting. It uses Tkinter for the UI and PyInstaller for packaging.

## Build Commands

### Run Development Version
```bash
python main.py
# or
py main.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
# or
py -m pip install -r requirements.txt
```

### Build EXE (Production)
```bash
# Single file executable (recommended)
py -m PyInstaller --name=PhotoCleaner --onefile --windowed --clean main.py

# With additional options
py -m PyInstaller --name=PhotoCleaner --onefile --windowed --add-data="src;src" --hidden-import=cv2 --hidden-import=numpy --hidden-import=PIL --clean main.py
```

### Linting
```bash
# If ruff is installed
ruff check .
ruff check src/

# Fix automatically
ruff check --fix .
```

## Code Style Guidelines

### Imports
- Standard library imports first (tkinter, threading, etc.)
- Third-party imports second (cv2, numpy, PIL)
- Local imports last (from src.inpainting import ...)
- Use explicit relative imports within the project

### Naming Conventions
- **Classes**: PascalCase (e.g., `PhotoCleanerApp`)
- **Functions/Methods**: snake_case (e.g., `auto_remove`, `inpaint_region`)
- **Variables**: snake_case (e.g., `original_image`, `file_path`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_SIZE`)
- **Private methods**: prefix with underscore (e.g., `_internal_method`)

### Type Hints
- Add type hints for function parameters and return values when beneficial
- Use built-in types (str, int, bool) or typing module
```python
def inpaint_region(image, mask, method: str = "telea") -> np.ndarray:
    ...
```

### Error Handling
- Use try/except blocks for operations that may fail (file I/O, image processing)
- Show user-friendly error messages via messagebox
- Log errors appropriately for debugging
- Never expose raw exception messages to end users

### Code Structure
- Keep functions focused and small (< 50 lines preferred)
- Group related functionality into classes
- Use meaningful variable and function names
- Add docstrings for complex functions
- Use threading for long-running operations (image processing)

### UI Development (Tkinter)
- Use ttk widgets for better appearance
- Handle UI updates via `root.after()` from background threads
- Use consistent padding and layout
- Keep UI logic separate from business logic

### Image Processing (OpenCV)
- Use BGR color space (OpenCV default)
- Convert to RGB before displaying with PIL
- Use numpy arrays for image data
- Handle None cases for image loading

### File Organization
```
PhotoCleaner/
├── main.py              # Entry point
├── src/
│   ├── gui.py           # UI logic
│   └── inpainting.py    # Image processing
├── requirements.txt     # Dependencies
├── pyproject.toml      # Project metadata
└── dist/               # Built executables
```

### Testing
- No formal test framework currently in use
- For manual testing: use `python main.py` and test with sample images
- Test edge cases: large images, corrupt files, missing files

### Packaging (PyInstaller)
- Use `--onefile` for single executable
- Use `--windowed` to hide console window
- Include `--hidden-import` for modules not auto-detected
- Clean build directory between builds: `--clean`

### Git Conventions
- Do not commit: `dist/`, `build/`, `*.pyc`, `.venv/`, `__pycache__/`
- Do commit: source code, requirements.txt, README.md

## Common Tasks

### Adding a New Feature
1. Implement logic in appropriate module (gui.py or inpainting.py)
2. Add corresponding UI element if needed
3. Test manually with `python main.py`
4. Rebuild EXE: `py -m PyInstaller --onefile --windowed --clean main.py`

### Debugging EXE Issues
1. Remove `--windowed` flag to see console output
2. Check build warnings in build directory
3. Verify all dependencies are included with `--hidden-import`

## Configuration Files

### requirements.txt
```
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
pyinstaller>=6.0.0
```

### pyproject.toml
- Minimal configuration (no complex build system needed)
- Python 3.10+ required

## Notes
- This is a simple single-user desktop application
- No database or API integrations
- Chinese UI text used throughout (simplified Chinese)