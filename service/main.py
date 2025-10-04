"""
Background service for reminder app
This runs even when the app is closed
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

print("Service starting...")

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
        """Load reminders from JSON file"""
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
                            'ringtone_uri': item.get('ringtone_uri', None)
                        })
                    print(f"Loaded {len(reminders)} reminders")
                    return reminders
        except Exception as e:
            print(f"Error loading reminders: {e}")
        return []
    
    def show_notification(self, reminder):
        """Show notification when reminder triggers"""
        try:
            notification_service = self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            
            intent = Intent(self.service.getApplicationContext(), PythonActivity)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
            pending_intent = PendingIntent.getActivity(
                self.service, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            builder = NotificationCompat.Builder(self.service, "reminder_channel")
            builder.setContentTitle("Reminder!")
            builder.setContentText(reminder['text'])
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentIntent(pending_intent)
            builder.setPriority(NotificationCompat.PRIORITY_MAX)
            builder.setCategory(NotificationCompat.CATEGORY_ALARM)
            builder.setAutoCancel(True)
            builder.setVibrate([0, 500, 200, 500])
            
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
            
            print(f"Notification shown for: {reminder['text']}")
            
        except Exception as e:
            print(f"Notification error: {e}")
            import traceback
            traceback.print_exc()
    
    def vibrate(self):
        """Vibrate the device"""
        try:
            vibrator = self.service.getSystemService(Context.VIBRATOR_SERVICE)
            if VERSION.SDK_INT >= 26:
                pattern = [0, 500, 200, 500, 200, 500]
                effect = VibrationEffect.createWaveform(pattern, -1)
                vibrator.vibrate(effect)
            else:
                vibrator.vibrate([0, 500, 200, 500, 200, 500], -1)
            print("Device vibrated")
        except Exception as e:
            print(f"Vibration error: {e}")
    
    def play_alarm(self, reminder):
        """Play alarm sound"""
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
                    # Play custom user-selected ringtone
                    uri = Uri.parse(ringtone_uri)
                    self.media_player.setDataSource(self.service, uri)
                else:
                    # Use default alarm sound
                    default_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                    self.media_player.setDataSource(self.service, default_uri)
                
                self.media_player.setLooping(True)
                self.media_player.prepare()
                self.media_player.start()
                
                print(f"Playing alarm sound: {ringtone_name}")
                
        except Exception as e:
            print(f"Alarm playback error: {e}")
            import traceback
            traceback.print_exc()
    
    def wake_screen(self):
        """Wake up the screen"""
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
            
            print("Screen woken up")
            
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
            
            for idx, r in enumerate(reminders):
                if not r.get('enabled'):
                    continue
                
                if current_day not in r.get('days', list(range(7))):
                    continue
                
                if r['hour'] == now.hour and r['minute'] == now.minute:
                    reminder_key = f"{idx}_{r['hour']:02d}{r['minute']:02d}_{now.date()}"
                    
                    if reminder_key not in self.triggered_reminders:
                        print(f"Triggering reminder {idx}: {r['text']}")
                        
                        self.show_notification(r)
                        self.vibrate()
                        self.play_alarm(r)
                        self.wake_screen()
                        
                        self.triggered_reminders.add(reminder_key)
            
            if now.hour == 0 and now.minute == 0:
                print("Midnight reset - clearing triggered reminders")
                self.triggered_reminders.clear()
                
        except Exception as e:
            print(f"Check reminders error: {e}")
            import traceback
            traceback.print_exc()
    
    def start_foreground(self):
        """Start service in foreground"""
        try:
            intent = Intent(self.service.getApplicationContext(), PythonActivity)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            pending_intent = PendingIntent.getActivity(
                self.service, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            builder = NotificationCompat.Builder(self.service, "reminder_channel")
            builder.setContentTitle("My Reminders")
            builder.setContentText("Reminder service is running")
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentIntent(pending_intent)
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            builder.setOngoing(True)
            
            notification = builder.build()
            self.service.startForeground(1, notification)
            print("Service started in foreground")
            
        except Exception as e:
            print(f"Foreground service error: {e}")
    
    def run(self):
        """Main service loop"""
        print("Service running...")
        self.start_foreground()
        
        while True:
            try:
                self.check_reminders()
                time.sleep(30)
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
