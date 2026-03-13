# Anyx CC

Anyx CC is a custom control center I put together for the Trimui Smart Pro (and it should work on other Linux-based retro handhelds). It's written in Python using Pygame and basically gives you a UI to tweak system settings, run cleanup scripts, and mess with the CPU governor without having to SSH into the device or write bash scripts.

## What it does
* **CPU & RAM Tweaks:** Toggle between CPU governors (Balanced, Performance, Power Save) and turn ZRAM on/off.
* **Maintenance:** Flush the system cache, fix SD card permissions.
* **Themes:** Full UI color customization via a simple JSON file.
* **Extras:** Plays background music and has an OTA update option that pulls straight from this repo.

## Controls
If you're testing on a keyboard, the mappings are in parentheses.
* **Up / Down:** Scroll through the list
* **Left / Right (Q / E):** Switch menu tabs
* **A Button (Enter):** Toggle an option or run a command
* **B Button (Escape):** Cancel or close the app

## Theming & Setup
If you want to change the colors, just edit `settings/theme.json`. It takes standard RGB arrays `[R, G, B]`. If you mess up the formatting or delete the file, the app won't crash; it just defaults back to the built-in dark theme.

You can also drop a custom font file into the `settings/` folder if you want to override the default system font. If you want background music, drop an MP3 file at `sound/bg-music.mp3`.

## Dev Note
If you're running or testing this on your PC, make sure to change `DEBUG_MODE = True` at the top of the python script. If you leave it as `False`, it's going to try running actual Linux shell commands on your local machine and will probably throw a bunch of errors in your terminal. 

## License
GPLv3. Do whatever you want with it, just keep it open source if you share your modified versions!