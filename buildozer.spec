[app]
title = My Reminders
package.name = myreminders
package.domain = com.reminder
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = service/*
version = 2.5

requirements = python3,kivy==2.3.0,android,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PLAYBACK,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

android.api = 33
android.minapi = 21
android.accept_sdk_license = True

android.services = ReminderService:service/main.py

android.apptheme = @android:style/Theme.Material.Light.NoActionBar

android.enable_androidx = True
android.gradle_dependencies = com.google.android.material:material:1.9.0

android.archs = arm64-v8a

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
