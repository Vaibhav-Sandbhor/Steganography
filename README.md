# Steganography Project

This project hides and reveals secret text inside images using Python.

## Features

- Encode secret messages into images
- Decode messages from encoded images
- Password-protected encryption/decryption
- GUI support (single-page and multi-page UI)

## Requirements

- Python 3.8+
- Dependencies in `requirements.txt`

## Setup

```bash
pip install -r requirements.txt
```

## Run

Single-page UI:

```bash
python main.py
```

Multi-page UI:

```bash
python main_multipage.py
```

## Quick test

```bash
python test_steganography.py
```

## Main files

- `main.py` - Entry point for single-page GUI
- `main_multipage.py` - Entry point for multi-page GUI
- `steganography.py` - Core encode/decode logic
- `ui.py` - Single-page GUI
- `ui_multipage.py` - Multi-page GUI
- `requirements.txt` - Python dependencies
