[app]
title = My Reminders
package.name = myreminders
package.domain = com.reminder
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = service/*
version = 2.5

# Minimal requirements
requirements = python3,kivy==2.3.0,android,pyjnius

orientation = portrait
fullscreen = 0

# Permissions (one per line for clarity)
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PLAYBACK,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

# API levels - Use compatible NDK
android.api = 33
android.minapi = 26
android.ndk = 27c
android.accept_sdk_license = True

# Service configuration
android.services = ReminderService:service/main.py

# Theme
android.apptheme = @android:style/Theme.Material.Light.NoActionBar

# Gradle dependencies
android.gradle_dependencies = com.google.android.material:material:1.9.0

# AndroidX
android.enable_androidx = True

# Java compatibility
android.add_compile_options = sourceCompatibility JavaVersion.VERSION_11, targetCompatibility JavaVersion.VERSION_11

# Architecture
android.archs = arm64-v8a

# P4A settings - Use develop branch for better compatibility
p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
