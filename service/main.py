"""
Enhanced background service for reminder app
Supports categories, priorities, and notes
"""
import os
import json
import datetime
import time
from jnius import autoclass

# Android classes
PythonService = autoclass('org.kivy.android.PythonService')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass('android.content.Context')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
PendingIntent = autoclass('android.app.PendingIntent')
Intent = autoclass('android.content.Intent')
Vibrator = autoclass('android.os.Vibrator')
VibrationEffect = autoclass('android.os.VibrationEffect')
VERSION = autoclass('android.os.Build$VERSION')
MediaPlayer = autoclass('android.media.MediaPlayer')
AudioManager = autoclass('android.media.AudioManager')
Uri = autoclass('android.net.Uri')
RingtoneManager = autoclass('android.media.RingtoneManager')
PowerManager = autoclass('android.os.PowerManager')

print("Enhanced Service starting...")

class ReminderService:
    def __init__(self):
        self.service = PythonService.mService
        self.data_dir = self.service.getFilesDir().getAbsolutePath()
        self.data_file = os.path.join(self.data_dir, 'reminders.json')
        self.triggered_reminders = set()
        self.last_check_minute = -1
        self.media_player = None
        
        print(f"Service initialized. Data file: {self.data_file}")
    
    def load_reminders(self):
        """Load reminders from JSON file with enhanced fields"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    reminders = []
                    for item in data:
                        h, m = map(int, item['time'].split(':'))
                        reminders.append({
                            'text': item['text'],
                            'hour': h,
                            'minute': m,
                            'enabled': item.get('enabled', True),
                            'days': item.get('days', list(range(7))),
                            'ringtone': item.get('ringtone', 'Default System Sound'),
                            'ringtone_uri': item.get('ringtone_uri', None),
                            'category': item.get('category', 'Personal'),
                            'priority': item.get('priority', 'Medium'),
                            'note': item.get('note', '')
                        })
                    print(f"Loaded {len(reminders)} reminders")
                    return reminders
        except Exception as e:
            print(f"Error loading reminders: {e}")
        return []
    
    def show_notification(self, reminder):
        """Show enhanced notification with category and priority"""
        try:
            notification_service = self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            
            intent = Intent(self.service.getApplicationContext(), PythonActivity)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
            pending_intent = PendingIntent.getActivity(
                self.service, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Enhanced notification title with category
            category = reminder.get('category', 'Reminder')
            priority = reminder.get('priority', 'Medium')
            
            # Priority icon
            priority_icon = "⚠️ " if priority == 'High' else ""
            
            builder = NotificationCompat.Builder(self.service, "reminder_channel")
            builder.setContentTitle(f"{priority_icon}⏰ {category}")
            builder.setContentText(reminder['text'])
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentIntent(pending_intent)
            
            # Set priority based on reminder priority
            if priority == 'High':
                builder.setPriority(NotificationCompat.PRIORITY_MAX)
            elif priority == 'Medium':
                builder.setPriority(NotificationCompat.PRIORITY_HIGH)
            else:
                builder.setPriority(NotificationCompat.PRIORITY_DEFAULT)
            
            builder.setCategory(NotificationCompat.CATEGORY_ALARM)
            builder.setAutoCancel(True)
            
            # Vibration pattern based on priority
            if priority == 'High':
                builder.setVibrate([0, 300, 100, 300, 100, 500])
            else:
                builder.setVibrate([0, 500, 200, 500])
            
            # Add note to notification if exists
            if reminder.get('note'):
                builder.setStyle(
                    NotificationCompat.BigTextStyle()
                    .bigText(f"{reminder['text']}\n\n📝 {reminder['note']}")
                )
            
            # Add sound based on user preference
            if reminder.get('ringtone') != 'Vibrate Only':
                ringtone_uri = reminder.get('ringtone_uri')
                if ringtone_uri and ringtone_uri != 'SYSTEM_DEFAULT':
                    sound_uri = Uri.parse(ringtone_uri)
                else:
                    sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                builder.setSound(sound_uri)
            
            notification = builder.build()
            notification.flags |= notification.FLAG_INSISTENT | notification.FLAG_AUTO_CANCEL
            notification_service.notify(1001, notification)
            
            print(f"Notification shown: {category} - {reminder['text']}")
            
        except Exception as e:
            print(f"Notification error: {e}")
            import traceback
            traceback.print_exc()
    
    def vibrate(self, priority='Medium'):
        """Vibrate the device with pattern based on priority"""
        try:
            vibrator = self.service.getSystemService(Context.VIBRATOR_SERVICE)
            
            if priority == 'High':
                pattern = [0, 300, 100, 300, 100, 500, 100, 500]
            elif priority == 'Medium':
                pattern = [0, 500, 200, 500, 200, 500]
            else:
                pattern = [0, 400, 300, 400]
            
            if VERSION.SDK_INT >= 26:
                effect = VibrationEffect.createWaveform(pattern, -1)
                vibrator.vibrate(effect)
            else:
                vibrator.vibrate(pattern, -1)
            
            print(f"Device vibrated with {priority} priority pattern")
        except Exception as e:
            print(f"Vibration error: {e}")
    
    def play_alarm(self, reminder):
        """Play alarm sound with enhanced handling"""
        try:
            if self.media_player:
                try:
                    self.media_player.stop()
                    self.media_player.release()
                except:
                    pass
                self.media_player = None
            
            ringtone_name = reminder.get('ringtone', 'Default System Sound')
            
            if ringtone_name != 'Vibrate Only':
                self.media_player = MediaPlayer()
                self.media_player.setAudioStreamType(AudioManager.STREAM_ALARM)
                
                ringtone_uri = reminder.get('ringtone_uri')
                if ringtone_uri and ringtone_uri != 'SYSTEM_DEFAULT':
                    uri = Uri.parse(ringtone_uri)
                    self.media_player.setDataSource(self.service, uri)
                    print(f"Playing custom ringtone for {reminder.get('category', 'reminder')}")
                else:
                    default_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                    self.media_player.setDataSource(self.service, default_uri)
                    print(f"Playing default alarm for {reminder.get('category', 'reminder')}")
                
                # High priority reminders loop more aggressively
                self.media_player.setLooping(True)
                self.media_player.prepare()
                self.media_player.start()
                
        except Exception as e:
            print(f"Alarm playback error: {e}")
            import traceback
            traceback.print_exc()
    
    def wake_screen(self):
        """Wake up the screen and launch app"""
        try:
            power_manager = self.service.getSystemService(Context.POWER_SERVICE)
            wake_lock = power_manager.newWakeLock(
                PowerManager.SCREEN_BRIGHT_WAKE_LOCK | 
                PowerManager.ACQUIRE_CAUSES_WAKEUP,
                "MyReminders::WakeLock"
            )
            wake_lock.acquire(10000)  # 10 seconds
            
            intent = Intent(self.service.getApplicationContext(), PythonActivity)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | 
                          Intent.FLAG_ACTIVITY_CLEAR_TOP |
                          Intent.FLAG_FROM_BACKGROUND)
            self.service.startActivity(intent)
            
            print("Screen woken up and app launched")
            
        except Exception as e:
            print(f"Wake screen error: {e}")
    
    def check_reminders(self):
        """Check if any reminders should trigger"""
        try:
            now = datetime.datetime.now()
            current_minute = now.hour * 60 + now.minute
            
            if current_minute == self.last_check_minute:
                return
            
            self.last_check_minute = current_minute
            current_day = now.weekday()
            
            print(f"Checking reminders at {now.strftime('%H:%M')}, day {current_day}")
            
            reminders = self.load_reminders()
            
            # Sort by priority to trigger high priority first
            priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
            reminders.sort(key=lambda x: priority_order.get(x.get('priority', 'Medium'), 1))
            
            for idx, r in enumerate(reminders):
                if not r.get('enabled'):
                    continue
                
                if current_day not in r.get('days', list(range(7))):
                    continue
                
                if r['hour'] == now.hour and r['minute'] == now.minute:
                    reminder_key = f"{idx}_{r['hour']:02d}{r['minute']:02d}_{now.date()}"
                    
                    if reminder_key not in self.triggered_reminders:
                        category = r.get('category', 'Personal')
                        priority = r.get('priority', 'Medium')
                        
                        print(f"Triggering {priority} priority {category} reminder: {r['text']}")
                        
                        self.show_notification(r)
                        self.vibrate(priority)
                        self.play_alarm(r)
                        self.wake_screen()
                        
                        self.triggered_reminders.add(reminder_key)
            
            # Midnight reset
            if now.hour == 0 and now.minute == 0:
                print("Midnight reset - clearing triggered reminders")
                self.triggered_reminders.clear()
                
        except Exception as e:
            print(f"Check reminders error: {e}")
            import traceback
            traceback.print_exc()
    
    def start_foreground(self):
        """Start service in foreground with enhanced notification"""
        try:
            intent = Intent(self.service.getApplicationContext(), PythonActivity)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            pending_intent = PendingIntent.getActivity(
                self.service, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            builder = NotificationCompat.Builder(self.service, "reminder_channel")
            builder.setContentTitle("⏰ My Reminders")
            builder.setContentText("Monitoring your reminders...")
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentIntent(pending_intent)
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            builder.setOngoing(True)
            
            # Show active reminder count
            reminders = self.load_reminders()
            active_count = sum(1 for r in reminders if r.get('enabled'))
            if active_count > 0:
                builder.setSubText(f"{active_count} active reminder{'s' if active_count != 1 else ''}")
            
            notification = builder.build()
            self.service.startForeground(1, notification)
            print("Service started in foreground")
            
        except Exception as e:
            print(f"Foreground service error: {e}")
    
    def run(self):
        """Main service loop"""
        print("Enhanced service running...")
        self.start_foreground()
        
        while True:
            try:
                self.check_reminders()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Service loop error: {e}")
                time.sleep(30)


if __name__ == "__main__":
    try:
        service = ReminderService()
        service.run()
    except Exception as e:
        print(f"Service crash: {e}")
        import traceback
        traceback.print_exc()
