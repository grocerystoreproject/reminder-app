[app]
title = My Reminders
package.name = myreminders
package.domain = com.reminder

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = service/*

version = 2.5

# Dependencies
requirements = python3,kivy==2.3.0,android,pyjnius

# App behaviour
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PLAYBACK,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

# Android SDK / NDK versions
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Background service (auto reminder)
android.services = ReminderService:service/main.py

# Theme
android.apptheme = @android:style/Theme.Material.Light.NoActionBar

# AndroidX & Gradle setup
android.enable_androidx = True
android.gradle_dependencies = com.google.android.material:material:1.9.0
android.add_compile_options = sourceCompatibility JavaVersion.VERSION_11, targetCompatibility JavaVersion.VERSION_11

# Supported architectures
android.archs = arm64-v8a

# Python-for-Android branch
p4a.branch = master
p4a.bootstrap = sdl2

# Optional: improve build reliability
android.gradle_plugin = 8.1.0
android.sdk = 33
android.ndk_path = $ANDROID_NDK_HOME

[buildozer]
log_level = 2
warn_on_root = 1
# Force rebuild only if needed (useful in CI)
build_dir = .buildozer
bin_dir = bin

# Optional: disable host checks on CI
# (prevents "running as root" warnings)
allow_hostpython_prebuilt = True

# Compatibility for GitHub Actions (Ubuntu 24+)
require_android_api = 33
use_legacy_toolchain = False
