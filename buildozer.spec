[app]
title = ReminderApp
package.name = reminderapp
package.domain = org.example
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
orientation = portrait
fullscreen = 0
# Permissions
android.permissions = INTERNET,VIBRATE

# Kivy requirements
requirements = python3,kivy==2.2.1

# Android-specific
android.arch = arm64-v8a,armeabi-v7a
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = @android:style/Theme.NoTitleBar
