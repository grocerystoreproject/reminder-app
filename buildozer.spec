[app]

# (str) Title of your application
title = My Reminders

# (str) Package name
package.name = myreminders

# (str) Package domain (needed for android/ios packaging)
package.domain = com.reminder

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,mp3,wav,ogg,m4a

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,assets/ringtones/*,service/*

# (str) Application versioning (method 1)
version = 3.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,android,pyjnius

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions - ALL CRITICAL PERMISSIONS FOR ANDROID 12+
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,SCHEDULE_EXACT_ALARM,POST_NOTIFICATIONS,USE_EXACT_ALARM,FOREGROUND_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO,FOREGROUND_SERVICE_MEDIA_PLAYBACK,DISABLE_KEYGUARD,TURN_SCREEN_ON,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,SYSTEM_ALERT_WINDOW,USE_FULL_SCREEN_INTENT,RECEIVE,SET_ALARM

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
# CRITICAL: AlarmReceiver service to handle alarms when app is closed
android.services = AlarmReceiver:service/alarm_receiver.py:foreground

# (str) Android app theme, default is ok for Kivy-based app
android.apptheme = @android:style/Theme.NoTitleBar.Fullscreen

# (list) Gradle dependencies to add
android.gradle_dependencies = com.google.android.material:material:1.6.1

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) add java compile options
android.add_compile_options = "sourceCompatibility = JavaVersion.VERSION_17", "targetCompatibility = JavaVersion.VERSION_17"

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) If True, then skip trying to update the Android sdk
android.skip_update = False

# (str) python-for-android branch to use, defaults to master
p4a.branch = develop

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.no_compile_pyo = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
