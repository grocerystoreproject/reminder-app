[app]
# App details
title = Reminder App
package.name = reminderapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Kivy + Python requirements
requirements = python3,kivy

# App settings
orientation = portrait
fullscreen = 0

# Permissions if you need sound + file access
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
# Logging
log_level = 2
warn_on_root = 1

# Automatically accept SDK/NDK if possible
# (GitHub Actions will handle licenses anyway)
build_dir = .buildozer

[android]
# Android build config
android.api = 33
android.minapi = 21
android.arch = armeabi-v7a,arm64-v8a
android.ndk = 23b
p4a.branch = master
