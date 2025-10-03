# reminder-app
# ⏰ My Reminders - Modern Reminder App

A beautiful, peaceful, and feature-rich reminder application built with Kivy for Android.

## ✨ Features

### Core Functionality
- 📝 **Create Custom Reminders** - Set reminders with custom text and times
- 🔔 **Smart Notifications** - Get alerted with vibrations and on-screen popups
- 📅 **Flexible Scheduling** - Choose specific days or repeat patterns (daily, weekdays, weekends)
- 😴 **Snooze Function** - Snooze reminders for 5-30 minutes
- ✅ **Toggle On/Off** - Easily enable or disable reminders without deleting
- ✏️ **Edit Reminders** - Update existing reminders anytime
- 🗑️ **Delete with Confirmation** - Safe deletion with confirmation dialog

### User Experience
- 🎨 **Modern, Peaceful UI** - Clean design with rounded cards and calming colors
- 🌈 **Visual Status Indicators** - Color-coded cards show active/inactive status
- 📊 **Statistics Dashboard** - View total, active, and inactive reminders at a glance
- ⏱️ **Live Clock** - Always see the current time and date
- 📱 **Portrait Optimized** - Designed specifically for mobile use
- 💾 **Auto-Save** - All changes are automatically saved

### Smart Features
- 🔄 **Recurring Reminders** - Set reminders for multiple days
- 🎯 **Quick Day Selection** - Presets for weekdays, weekends, or all days
- 🌙 **Midnight Reset** - Reminders automatically reset for the next day
- 💾 **Persistent Storage** - Your reminders are saved between app sessions

## 📸 Screenshots

*(Add your screenshots here)*

## 🚀 Installation

### Option 1: Download APK (Recommended)
1. Go to the [Releases](../../releases) page
2. Download the latest `.apk` file
3. Install on your Android device
4. Grant necessary permissions when prompted

### Option 2: Build from Source

#### Prerequisites
- Python 3.10 or 3.11
- Android SDK and NDK
- Buildozer

#### Build Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/reminder-app.git
cd reminder-app
```

2. **Install dependencies**
```bash
pip install buildozer cython==0.29.36
```

3. **Create required directories**
```bash
mkdir -p assets/ringtones
```

4. **Build the APK**
```bash
buildozer android debug
```

5. **Find your APK**
```bash
# The APK will be in the bin/ directory
ls bin/*.apk
```

## 🔧 Development Setup

### Local Testing (Desktop)

```bash
# Install Kivy
pip install kivy

# Run the app
python main.py
```

### Testing on Android

```bash
# Connect your Android device via USB with USB debugging enabled
buildozer android debug deploy run logcat
```

## 📝 Usage Guide

### Creating a Reminder

1. Tap **"+ Add New Reminder"**
2. Enter your reminder text
3. Set the time using the hour/minute spinners
4. Select AM or PM
5. Choose which days to repeat
   - Use quick buttons: "Weekdays", "Weekend", or "Every day"
   - Or manually select specific days
6. Tap **"💾 Save Reminder"**

### Managing Reminders

- **Turn On/Off**: Tap the "Turn On"/"Turn Off" button on any reminder card
- **Edit**: Tap the "✎ Edit" button to modify a reminder
- **Delete**: Tap the "🗑" button and confirm deletion
- **Snooze**: When an alarm triggers, adjust the slider and tap "😴 Snooze"

### Understanding the UI

- **White cards** = Active reminders
- **Gray cards** = Disabled reminders
- **Green indicator** = Reminder is active (✓ Active)
- **Gray indicator** = Reminder is off (○ Off)

## 🛠️ Technical Details

### Built With
- **Python 3.11** - Programming language
- **Kivy 2.3.0** - Cross-platform UI framework
- **Buildozer** - Android packaging tool
- **python-for-android** - Android backend

### Permissions Required
- `VIBRATE` - For vibration alerts
- `WAKE_LOCK` - To wake device for alarms
- `SCHEDULE_EXACT_ALARM` - For precise timing
- `POST_NOTIFICATIONS` - For notification support

### File Structure
```
reminder-app/
├── main.py              # Main application code
├── buildozer.spec       # Build configuration
├── .github/
│   └── workflows/
│       └── build-apk.yml # CI/CD workflow
├── assets/
│   └── ringtones/       # Custom ringtones (optional)
└── README.md            # This file
```

## 🐛 Troubleshooting

### App won't install
- Enable "Install from Unknown Sources" in Android settings
- Check if you have sufficient storage space

### Reminders not triggering
- Ensure the app has all required permissions
- Check that the reminder is enabled (green indicator)
- Verify battery optimization is disabled for the app

### Build fails
- Ensure you have Python 3.10 or 3.11
- Clear buildozer cache: `buildozer android clean`
- Check that all system dependencies are installed

## 🔮 Upcoming Features

- [ ] Custom ringtones
- [ ] Multiple alarms per day
- [ ] Reminder categories
- [ ] Dark mode
- [ ] Widget support
- [ ] Notification sound selection
- [ ] Import/Export reminders
- [ ] Cloud sync

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the SBGI Miraj third year students for mini project:- 1. Harshvardhan Chandanshive 2:- Nikita Bagate 3:- Shreya Dalwai

## 👤 Author

Your Name - [harshvardhanchandanshive703@gmail.com]

## 🙏 Acknowledgments

- Kivy Team for the amazing framework
- Contributors and testers
- Icon and emoji providers

## 📞 Support

If you encounter any issues or have suggestions:
- Open an [issue](../../issues)
- Star ⭐ the repository if you find it useful!

---

Made with ❤️ and Python
