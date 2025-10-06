[app]
title = My Reminders
package.name = myreminders
package.domain = com.reminder
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,mp3,wav,ogg,m4a
source.include_patterns = assets/*,service/*
version = 2.5

# Complete requirements with all necessary packages
requirements = python3==3.11.6,kivy==2.3.0,android,jnius,pyjnius,certifi

orientation = portrait
fullscreen = 0

# Complete permissions list for alarm functionality
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PLAYBACK,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO,DISABLE_KEYGUARD,TURN_SCREEN_ON,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,SYSTEM_ALERT_WINDOW,USE_FULL_SCREEN_INTENT,android.permission.FOREGROUND_SERVICE_SPECIAL_USE,ACCESS_NOTIFICATION_POLICY

# Target Android 13 (API 33) for broad compatibility with modern features
android.api = 33
android.minapi = 26
android.ndk = 25b
android.private_storage = True
android.accept_sdk_license = True

# Service configuration - removed 'foreground' keyword
android.services = ReminderService:service/main.py

# Modern Material theme
android.apptheme = @android:style/Theme.Material.Light.NoActionBar

# Updated gradle dependencies for compatibility
android.gradle_dependencies = com.google.android.material:material:1.9.0,androidx.core:core:1.12.0,androidx.appcompat:appcompat:1.6.1

# Enable AndroidX for modern Android support
android.enable_androidx = True

# Java 17 compatibility
android.add_compile_options = sourceCompatibility = JavaVersion.VERSION_17, targetCompatibility = JavaVersion.VERSION_17

# Copy native libraries
android.copy_libs = 1

# Support all major architectures for maximum device compatibility
android.archs = arm64-v8a,armeabi-v7a

# Backup and update settings
android.allow_backup = True
android.skip_update = False

# Use stable p4a version
p4a.branch = master
p4a.bootstrap = sdl2

# Required for proper compilation
p4a.local_recipes = ./p4a-recipes

# Manifest configurations
android.manifest_placeholders = [:]
android.meta_data = com.google.android.gms.car.application=false

# Foreground service type for Android 14+
android.manifest.service_attributes = android:foregroundServiceType="mediaPlayback|specialUse"

# Additional manifest additions for receivers
android.add_src = java

# Presplash and icon (optional - remove if you don't have these)
# presplash.filename = %(source.dir)s/data/presplash.png
# icon.filename = %(source.dir)s/data/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
