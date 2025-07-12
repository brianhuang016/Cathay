# Cathay Bank Mortgage Calculator Selenium Script

This script automates the interaction with the Cathay Bank mortgage calculator page to locate and click the "選擇縣市" (Select County/City) dropdown menu, then takes a screenshot.

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Chrome browser** installed
3. **ChromeDriver** - The script will attempt to use the system ChromeDriver, but you may need to install it manually

## Installation

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Install ChromeDriver (if not already installed):
   - Download from: https://chromedriver.chromium.org/
   - Or use webdriver-manager (included in requirements.txt)

## Usage

Run the script:
```bash
python cathay_mortgage_selenium.py
```

## What the script does

1. Opens Chrome browser
2. Navigates to the Cathay Bank mortgage calculator page
3. Searches for the "選擇縣市" dropdown using multiple selectors
4. Clicks on the dropdown when found
5. Takes screenshots:
   - `cathay_mortgage_dropdown.png` - Screenshot after clicking the dropdown
   - `cathay_mortgage_full_page.png` - Full page screenshot
   - `cathay_mortgage_debug.png` - Debug screenshot if dropdown is not found

## Troubleshooting

If the script cannot find the dropdown:
1. Check the debug screenshot to see the current page state
2. The script will print the page source for debugging
3. You may need to adjust the selectors based on the actual page structure

## Notes

- The script keeps the browser open for 10 seconds after completion so you can see the results
- If you want to run in headless mode, uncomment the headless option in the script
- The script uses multiple fallback selectors to try to find the dropdown element 