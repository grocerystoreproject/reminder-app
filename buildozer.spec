[app]
title = My Reminders
package.name = myreminders
package.domain = com.reminder
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,mp3,wav,ogg,m4a
source.include_patterns = assets/*,service/*
version = 2.5
requirements = python3,kivy==2.3.0,android,pyjnius
orientation = portrait
fullscreen = 0

# Add BOOT permission so alarms restart after phone reboot
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM,FOREGROUND_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO,FOREGROUND_SERVICE_MEDIA_PLAYBACK,DISABLE_KEYGUARD,TURN_SCREEN_ON,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,SYSTEM_ALERT_WINDOW,USE_FULL_SCREEN_INTENT

android.api = 33
android.minapi = 21
android.ndk = 25b
android.private_storage = True
android.accept_sdk_license = True

# Keep your service but AlarmManager will do the heavy lifting
android.services = ReminderService:service/main.py:foreground

android.apptheme = @android:style/Theme.NoTitleBar.Fullscreen
android.gradle_dependencies = com.google.android.material:material:1.6.1
android.enable_androidx = True
android.add_compile_options = "sourceCompatibility = JavaVersion.VERSION_17", "targetCompatibility = JavaVersion.VERSION_17"
android.copy_libs = 1
android.archs = arm64-v8a
android.allow_backup = True
android.skip_update = False
p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
