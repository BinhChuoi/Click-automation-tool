# presentation/README.md

# Presentation Component

This directory contains the presentation (UI and user interaction) logic of the project.

## Project Idea (Summary)

The system watches selected screen areas, detects relevant objects/text, evaluates scenario logic, and triggers configured actions.
The presentation layer focuses on:

- Tool Maker UI for creating and starting tools
- Overlay windows for visual feedback
- User interactions that drive scenario execution

Detection quality is improved through a hybrid approach (template matching + OCR + custom YOLO), while behavior is controlled by scenario rules.
For the complete overview, see [README.md](../README.md).

## Structure
- `__init__.py`: Package initialization and versioning.
- `main.py`: Entry point for running the presentation component independently.

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

## Run
Always run from the project root so package imports resolve correctly:

```powershell
cd <project-root>
.\.venv\Scripts\Activate.ps1
python -m presentation.main
```

## Version
See `__init__.py` for the current version.
