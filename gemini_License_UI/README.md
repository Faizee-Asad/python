## Generate a Key: Run the generate_key.py script from your terminal (python generate_key.py). It will print a valid license key. Copy this key.

### KEY = "VkFMSUQtTElDRU5TRS1GT1ItRElORURBU0g="

## Re-bundle Your .exe: When you are ready to distribute, remember to run the PyInstaller command again on the updated main.py to create a new .exe that includes the licensing system.

### python -m PyInstaller --windowed --onefile --exclude-module escpos.printer.cups --exclude-module escpos.printer.lp main.py
