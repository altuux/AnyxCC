#!/bin/sh
# Anyx CC - OTA Updater

# 1. Local version check
LOCAL_VER=$(cat version.txt 2>/dev/null || echo "0.0")

# 2. Download (raw) version.txt from github
REMOTE_VER=$(wget -qO- https://raw.githubusercontent.com/altuux/AnyxCC/main/version.txt 2>/dev/null | tr -d '\n\r')

# If any problems occur, end
if [ -z "$REMOTE_VER" ]; then
    exit 1
fi

# 3. Version compare
if [ "$LOCAL_VER" = "$REMOTE_VER" ]; then
    # Versions are the same
    exit 0
fi

# 4. Version are different, updating...
wget -q --show-progress https://github.com/altuux/AnyxCC/archive/refs/heads/main.zip -O update.zip

if [ -f "update.zip" ]; then
    # Unzip the file
    unzip -o update.zip
    
    # 1. Backing up preferences
    cp settings/theme.json /tmp/anyx_theme_backup.json 2>/dev/null
    cp sound/bg-music.mp3 /tmp/anyx_music_backup.mp3 2>/dev/null
    
    # 2. Copy files
    cp -rf AnyxCC-main/* .
    
    # 3. Restoring preferences
    cp /tmp/anyx_theme_backup.json settings/theme.json 2>/dev/null
    cp /tmp/anyx_music_backup.mp3 sound/bg-music.mp3 2>/dev/null
    
    # 4. Cleanup
    rm -rf AnyxCC-main update.zip
fi