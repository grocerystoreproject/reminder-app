[app]
title = ReminderApp
package.name = reminderapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
android.permissions = INTERNET,VIBRATE
android.api = 33
android.minapi = 21
p4a.branch = master
android.arch = armeabi-v7a, arm64-v8a

[buildozer]
log_level = 2
