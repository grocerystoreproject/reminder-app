[app]
title = My Reminders
package.name = myreminders
package.domain = com.reminder
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = service/*
version = 2.5

# Minimal requirements for faster build
requirements = python3,kivy==2.3.0,android,jnius,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PLAYBACK,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO,DISABLE_KEYGUARD,TURN_SCREEN_ON,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,SYSTEM_ALERT_WINDOW,USE_FULL_SCREEN_INTENT,android.permission.FOREGROUND_SERVICE_SPECIAL_USE,ACCESS_NOTIFICATION_POLICY

android.api = 33
android.minapi = 26
android.ndk = 25b
android.private_storage = True
android.accept_sdk_license = True

android.services = ReminderService:service/main.py

android.apptheme = @android:style/Theme.Material.Light.NoActionBar

android.gradle_dependencies = com.google.android.material:material:1.9.0,androidx.core:core:1.12.0

android.enable_androidx = True

android.add_compile_options = sourceCompatibility = JavaVersion.VERSION_17, targetCompatibility = JavaVersion.VERSION_17

android.copy_libs = 1

# Single architecture for faster testing
android.archs = arm64-v8a

android.allow_backup = True
android.skip_update = False

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
