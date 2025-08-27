# Research Log Manager

A Python-based desktop application for managing daily research logs with automatic file organization.
![Research Log Manager Banner](/docs/images/applicationImage.png)
## Features

- Automatic file organization by month and date
- Calendar-based navigation
- Dark/light mode toggle
- Auto-save functionality
- Basic text formatting
- Modern, professional UI

## Installation

1. Install Python 3.7+
2. Install dependencies:

```
python research_log_manager.py
```
## Usage

- The application automatically loads today's log
- Use the calendar to navigate to different dates
- Text is auto-saved every 30 seconds
- Use the formatting buttons for basic text formatting
- Toggle between dark and light mode with the sun/moon button

## File Structure

Logs are saved in your Documents folder under "Research Logs"

```
Research Logs/
├── January 2025/
│   ├── 01-01-2025.txt
│   └── 02-01-2025.txt
├── February 2025/
│   ├── 01-02-2025.txt
│   └── 15-02-2025.txt
└── settings.json
```
