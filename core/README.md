# core/README.md

# Core Component

This directory contains the core (business logic) of the project.

## Project Idea (Summary)

The core engine executes the automation loop:

1. Detect objects in configured screen regions
2. Evaluate scenario conditions
3. Execute actions when scenarios match

It uses a hybrid detection strategy to handle edge cases:

- Template matching for stable visual patterns
- Text detection for UI/state cues
- Custom YOLO models (trained in Roboflow) for harder or art-styled objects

This keeps the system both practical and adaptable for niche datasets.
For the complete overview, see [README.md](../README.md).

## Structure
- `__init__.py`: Package initialization and versioning.
- `main.py`: Entry point for running the core component independently.

## Requirements
- Python 3.11.x (validated with 3.11.5)

## Setup (from project root)

```powershell
cd <project-root>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install blinker dynaconf pyautogui keyboard pillow opencv-python numpy easyocr inference
```

## Usage
Run the core component directly from project root:

```powershell
cd <project-root>
.\.venv\Scripts\Activate.ps1
python core/main/main.py
```

## Version
See `__init__.py` for the current version.
