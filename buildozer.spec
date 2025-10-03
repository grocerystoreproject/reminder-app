[app]
title = ReminderApp
package.name = reminderapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,ogg
version = 0.1
requirements = python3,kivy==2.2.1,kivymd,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
android.add_src = src

[buildozer]
log_level = 2
warn_on_root = 1
