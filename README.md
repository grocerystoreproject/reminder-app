# ⏰ My Reminders - Professional Reminder App

A feature-rich, beautifully designed reminder application built with Kivy for Android. Organize your life with categories, priorities, custom sounds, and smart scheduling.

## ✨ Enhanced Features

### 🎯 Core Functionality
- **📝 Smart Reminders** - Create reminders with rich details and notes
- **📂 Categories** - Organize reminders by Work, Personal, Health, Shopping, or Other
- **⚠️ Priority Levels** - Set High, Medium, or Low priority for each reminder
- **🔔 Custom Notifications** - Choose system sounds, custom ringtones, or vibrate only
- **📅 Flexible Scheduling** - Repeat on specific days, weekdays, weekends, or daily
- **😴 Smart Snooze** - Snooze reminders for 5-30 minutes
- **✅ Quick Toggle** - Enable or disable reminders without deletion
- **✏️ Easy Editing** - Update any reminder detail anytime
- **🗑️ Safe Deletion** - Delete with confirmation dialog

### 🎨 User Experience
- **Modern Material Design** - Clean, colorful interface with accent colors
- **Category Color Coding** - Visual distinction for different reminder types
- **📊 Live Statistics** - View total, active, and today's reminders at a glance
- **🔍 Smart Filtering** - Filter reminders by category
- **📑 Multiple Sorting** - Sort by time, category, or priority
- **⏱️ Live Clock** - Always see current time and date
- **📱 Portrait Optimized** - Perfect for one-handed mobile use
- **💾 Auto-Save** - Changes saved automatically

### 🚀 Smart Features
- **🔄 Recurring Reminders** - Set for multiple days with visual day picker
- **🎯 Quick Day Presets** - One-tap weekdays, weekends, or all days
- **📝 Optional Notes** - Add detailed notes to any reminder
- **🌙 Midnight Reset** - Reminders automatically reset for the next day
- **💾 Persistent Storage** - All data saved between sessions
- **🔔 Background Service** - Works even when app is closed
- **📱 Priority Notifications** - High priority reminders get extra attention

## 📱 New UI Components

### Category System
- **Work** 🔶 - Orange accent for professional tasks
- **Personal** 🔵 - Blue accent for personal reminders
- **Health** 🟢 - Green accent for health & fitness
- **Shopping** 🟣 - Purple accent for shopping lists
- **Other** ⚫ - Gray accent for miscellaneous

### Priority Indicators
- **High Priority** - Red badge with "!!!" indicator and enhanced notifications
- **Medium Priority** - Orange badge with standard notifications
- **Low Priority** - Blue badge with gentle notifications

### Enhanced Stats Dashboard
- 📋 **Total Reminders** - Count of all reminders
- ✅ **Active Reminders** - Currently enabled reminders
- 📅 **Today's Count** - Reminders scheduled for today

## 📸 Screenshots

*(Coming soon - Add your screenshots here)*

## 🚀 Installation

### Option 1: Download APK (Recommended)
1. Go to the [Releases](../../releases) page
2. Download the latest `.apk` file
3. Install on your Android device (enable "Install from Unknown Sources")
4. Grant all requested permissions

### Option 2: Build from Source

#### Prerequisites
- Python 3.11
- Android SDK and NDK
- Buildozer 1.5.0

#### Build Steps

```bash
# Clone repository
git clone https://github.com/yourusername/reminder-app.git
cd reminder-app

# Install dependencies
pip install buildozer cython==0.29.36

# Create directories
mkdir -p assets/ringtones
mkdir -p service

# Build APK
buildozer android debug

# Find APK
ls bin/*.apk
```

## 📖 Usage Guide

### Creating a Reminder

1. **Tap "➕ Add New Reminder"**
2. **Enter reminder details:**
   - Reminder message (required)
   - Category (Work, Personal, Health, Shopping, Other)
   - Priority (High, Medium, Low)
   - Time (using hour/minute spinners)
   - Ringtone (system, custom, or vibrate only)
   - Days to repeat
   - Optional note for additional details
3. **Use quick presets:**
   - "Weekdays" - Monday through Friday
   - "Weekend" - Saturday and Sunday
   - "Every Day" - All seven days
4. **Tap "💾 Save Reminder"**

### Managing Reminders

- **Toggle On/Off**: Tap the ON/OFF button
- **Edit**: Tap "✏️ Edit" to modify any detail
- **Delete**: Tap "🗑️" and confirm deletion
- **Filter**: Use category dropdown to filter by type
- **Sort**: Choose Time, Category, or Priority sorting
- **Snooze**: When alarm triggers, adjust slider (5-30 min) and tap "😴 Snooze"

### Understanding the UI

#### Card Colors
- **White with colored accent** = Active reminder
- **Gray with muted accent** = Disabled reminder

#### Category Colors
- **Orange accent** = Work reminders
- **Blue accent** = Personal reminders
- **Green accent** = Health reminders
- **Purple accent** = Shopping reminders
- **Gray accent** = Other/disabled reminders

#### Priority Indicators
- **"!!!" badge** = High priority (red)
- **No badge** = Medium/Low priority

## 🛠️ Technical Details

### Built With
- **Python 3.11** - Programming language
- **Kivy 2.3.0** - Cross-platform UI framework
- **Buildozer 1.5.0** - Android packaging tool
- **python-for-android** - Android backend

### Permissions Required
- `VIBRATE` - For vibration alerts
- `WAKE_LOCK` - To wake device for alarms
- `SCHEDULE_EXACT_ALARM` - For precise timing
- `POST_NOTIFICATIONS` - For notification support
- `FOREGROUND_SERVICE` - Background service
- `READ_MEDIA_AUDIO` - For custom ringtones

### File Structure
```
reminder-app/
├── main.py              # Main app with enhanced UI
├── service/
│   └── main.py         # Enhanced background service
├── buildozer.spec      # Build configuration
├── .github/
│   └── workflows/
│       └── build-apk.yml # CI/CD workflow
├── assets/
│   └── ringtones/      # Custom ringtones (optional)
└── README.md           # This file
```

### Data Structure
Each reminder includes:
```json
{
  "text": "Reminder message",
  "time": "14:30",
  "category": "Work",
  "priority": "High",
  "enabled": true,
  "days": [0, 1, 2, 3, 4],
  "ringtone": "Default System Sound",
  "ringtone_uri": null,
  "note": "Optional additional details"
}
```

## 🐛 Troubleshooting

### App won't install
- Enable "Install from Unknown Sources" in Android settings
- Check storage space (need ~60MB free)
- Uninstall old version first if updating

### Reminders not triggering
- Ensure app has all permissions
- Check reminder is enabled (ON state)
- Verify correct days are selected
- Disable battery optimization for the app
- Check "Do Not Disturb" settings

### Custom ringtones not playing
- Grant audio file access permission
- Verify audio file format (MP3, OGG, WAV supported)
- Try using system default sound first

### Build fails
- Use Python 3.11 (not 3.12+)
- Clear buildozer cache: `buildozer android clean`
- Update buildozer: `pip install --upgrade buildozer`
- Check Java version (JDK 17 required)

## 🆕 What's New

### Version 2.3
- ✅ Category system with 5 types
- ✅ Priority levels (High, Medium, Low)
- ✅ Optional notes for reminders
- ✅ Enhanced filtering and sorting
- ✅ Improved statistics dashboard
- ✅ Better visual design with accent colors
- ✅ Priority-based notifications
- ✅ Category grouping in sorted view

## 🔮 Upcoming Features

- [ ] Widgets for home screen
- [ ] Dark mode support
- [ ] Reminder templates
- [ ] Location-based reminders
- [ ] Voice input for reminders
- [ ] Backup & restore to cloud
- [ ] Multiple alarm sounds per reminder
- [ ] Reminder history and completion tracking
- [ ] Recurring patterns (e.g., every 2 weeks)
- [ ] Sub-reminders/checklists
- [ ] Share reminders with others

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes.

**Developed by SBGI Miraj Third Year Students:**
1. Harshvardhan Chandanshive
2. Nikita Bagate
3. Shreya Dalwai

## 👤 Contact

**Harshvardhan Chandanshive**  
Email: harshvardhanchandanshive703@gmail.com

## 🙏 Acknowledgments

- Kivy Team for the excellent framework
- Material Design guidelines for UI inspiration
- Android development community
- All contributors and testers

## 💡 Tips for Best Experience

1. **Use Categories** - Organize reminders by type for better management
2. **Set Priorities** - Mark important reminders as High priority
3. **Add Notes** - Include details that help you remember context
4. **Quick Presets** - Use weekday/weekend buttons for faster setup
5. **Custom Sounds** - Choose distinct sounds for different categories
6. **Filter View** - Use category filter when you have many reminders
7. **Today Count** - Check stats to see today's reminder load

## 📊 Comparison with Similar Apps

| Feature | My Reminders | Others |
|---------|-------------|---------|
| Categories | ✅ 5 types | Limited |
| Priorities | ✅ 3 levels | Usually none |
| Notes | ✅ Full text | Limited |
| Custom Ringtones | ✅ | Often paid |
| Filtering | ✅ | Basic |
| Sorting | ✅ 3 ways | Limited |
| Free & Open Source | ✅ | Rare |
| No Ads | ✅ | Uncommon |
| Offline | ✅ 100% | Varies |

---

**Made with ❤️ and Python**

*Remember everything that matters!* ⏰📝✨
