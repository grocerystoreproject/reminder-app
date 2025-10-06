"""
Enhanced background service for reminder app - FIXED VERSION
Handles AlarmManager triggers and reschedules
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
AlarmManager = autoclass('android.app.AlarmManager')
Calendar = autoclass('java.util.Calendar')

print("Enhanced Service starting...")

class ReminderService:
    def __init__(self):
        self.service = PythonService.mService
        self.data_dir = self.service.getFilesDir().getAbsolutePath()
        self.data_file = os.path.join(self.data_dir, 'reminders.json')
        self.triggered_reminders = set()
        self.last_check_minute = -1
        self.media_player = None
        self.wake_lock = None
        
        print(f"Service initialized. Data file: {self.data_file}")
        
        # Check if we were started by AlarmManager
        self.handle_alarm_intent()
        
        try:
            power_manager = self.service.getSystemService(Context.POWER_SERVICE)
            self.wake_lock = power_manager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "MyReminders::ServiceWakeLock"
            )
            self.wake_lock.acquire()
            print("Wake lock acquired")
        except Exception as e:
            print(f"Wake lock error: {e}")
    
    def handle_alarm_intent(self):
        """Check if service was started by AlarmManager"""
        try:
            intent = self.service.getIntent()
            if intent:
                action = intent.getAction()
                if action and action.startswith("ALARM_"):
                    reminder_id = intent.getIntExtra("reminder_id", -1)
                    reminder_text = intent.getStringExtra("reminder_text")
                    reminder_category = intent.getStringExtra("reminder_category")
                    reminder_note = intent.getStringExtra("reminder_note")
                    alarm_hour = intent.getIntExtra("alarm_hour", 0)
                    alarm_minute = intent.getIntExtra("alarm_minute", 0)
                    alarm_days_str = intent.getStringExtra("alarm_days")
                    
                    print(f"AlarmManager triggered reminder {reminder_id}: {reminder_text}")
                    
                    # Show notification immediately
                    self.show_alarm_notification({
                        'text': reminder_text,
                        'category': reminder_category,
                        'note': reminder_note,
                        'priority': 'High'
                    }, reminder_id)
                    
                    self.vibrate('High')
                    self.play_alarm({'text': reminder_text})
                    self.wake_screen()
                    
                    # IMPORTANT: Reschedule for next occurrence
                    if alarm_days_str:
                        alarm_days = [int(d) for d in alarm_days_str.split(',')]
                        self.reschedule_alarm(
                            reminder_id, 
                            alarm_hour, 
                            alarm_minute, 
                            alarm_days,
                            reminder_text,
                            reminder_category,
                            reminder_note
                        )
                    
        except Exception as e:
            print(f"Handle alarm intent error: {e}")
            import traceback
            traceback.print_exc()
    
    def reschedule_alarm(self, reminder_id, hour, minute, days, text, category, note):
        """Reschedule alarm for next occurrence"""
        try:
            alarm_manager = self.service.getSystemService('alarm')
            
            # Find next occurrence
            now = Calendar.getInstance()
            current_time = now.getTimeInMillis()
            
            next_alarm_time = None
            
            for day in days:
                calendar = Calendar.getInstance()
                calendar.set(Calendar.HOUR_OF_DAY, hour)
                calendar.set(Calendar.MINUTE, minute)
                calendar.set(Calendar.SECOND, 0)
                calendar.set(Calendar.MILLISECOND, 0)
                
                java_day = ((day + 1) % 7) + 1
                calendar.set(Calendar.DAY_OF_WEEK, java_day)
                
                if calendar.getTimeInMillis() <= current_time:
                    calendar.add(Calendar.WEEK_OF_YEAR, 1)
                
                if next_alarm_time is None or calendar.getTimeInMillis() < next_alarm_time:
                    next_alarm_time = calendar.getTimeInMillis()
            
            if next_alarm_time:
                intent = Intent(self.service, PythonService)
                intent.setAction(f"ALARM_{reminder_id}")
                intent.putExtra("reminder_id", reminder_id)
                intent.putExtra("reminder_text", text)
                intent.putExtra("reminder_category", category)
                intent.putExtra("reminder_note", note)
                intent.putExtra("alarm_hour", hour)
                intent.putExtra("alarm_minute", minute)
                intent.putExtra("alarm_days", ','.join(map(str, days)))
                
                pending_intent = PendingIntent.getService(
                    self.service,
                    reminder_id,
                    intent,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
                )
                
                alarm_manager.setExactAndAllowWhileIdle(
                    AlarmManager.RTC_WAKEUP,
                    next_alarm_time,
                    pending_intent
                )
                
                print(f"Rescheduled alarm {reminder_id} for next occurrence")
                
        except Exception as e:
            print(f"Reschedule error: {e}")
            import traceback
            traceback.print_exc()
    
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
                            'ringtone': item.get('ringtone', 'System Alarm'),
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
    
    def show_alarm_notification(self, reminder, reminder_id):
        """Show full-screen alarm notification"""
        try:
            notification_service = self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            
            intent = Intent(self.service.getApplicationContext(), PythonActivity)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
            pending_intent = PendingIntent.getActivity(
                self.service, 0, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            category = reminder.get('category', 'Reminder')
            priority = reminder.get('priority', 'High')
            
            priority_icon = "[!] " if priority == 'High' else ""
            
            builder = NotificationCompat.Builder(self.service, "reminder_channel")
            builder.setContentTitle(f"{priority_icon}⏰ {category}")
            builder.setContentText(reminder['text'])
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentIntent(pending_intent)
            builder.setPriority(NotificationCompat.PRIORITY_MAX)
            builder.setCategory(NotificationCompat.CATEGORY_ALARM)
            builder.setAutoCancel(True)
            builder.setVibrate([0, 1000, 500, 1000])
            
            if reminder.get('note'):
                builder.setStyle(
                    NotificationCompat.BigTextStyle()
                    .bigText(f"{reminder['text']}\n\n📝 {reminder['note']}")
                )
            
            sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            builder.setSound(sound_uri)
            
            notification = builder.build()
            notification.flags |= notification.FLAG_INSISTENT | notification.FLAG_AUTO_CANCEL
            notification_service.notify(3000 + reminder_id, notification)
            
            print(f"Notification shown: {category} - {reminder['text']}")
            
        except Exception as e:
            print(f"Notification error: {e}")
            import traceback
            traceback.print_exc()
    
    def vibrate(self, priority='Medium'):
        """Vibrate the device"""
        try:
            vibrator = self.service.getSystemService(Context.VIBRATOR_SERVICE)
            
            if priority == 'High':
                pattern = [0, 1000, 500, 1000, 500, 1000]
            else:
                pattern = [0, 500, 200, 500]
            
            if VERSION.SDK_INT >= 26:
                effect = VibrationEffect.createWaveform(pattern, -1)
                vibrator.vibrate(effect)
            else:
                vibrator.vibrate(pattern, -1)
            
            print(f"Vibrated with {priority} priority")
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
            
            self.media_player = MediaPlayer()
            self.media_player.setAudioStreamType(AudioManager.STREAM_ALARM)
            
            default_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            self.media_player.setDataSource(self.service, default_uri)
            self.media_player.setLooping(True)
            self.media_player.prepare()
            self.media_player.start()
            
            print("Alarm sound playing")
            
        except Exception as e:
            print(f"Play alarm error: {e}")
            import traceback
            traceback.print_exc()
    
    def wake_screen(self):
        """Wake up the screen"""
        try:
            power_manager = self.service.getSystemService(Context.POWER_SERVICE)
            wake_lock = power_manager.newWakeLock(
                PowerManager.SCREEN_BRIGHT_WAKE_LOCK | 
                PowerManager.ACQUIRE_CAUSES_WAKEUP,
                "MyReminders::AlarmWakeLock"
            )
            wake_lock.acquire(10000)
            
            intent = Intent(self.service.getApplicationContext(), PythonActivity)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | 
                          Intent.FLAG_ACTIVITY_CLEAR_TOP |
                          Intent.FLAG_FROM_BACKGROUND)
            self.service.startActivity(intent)
            
            print("Screen woken up")
            
        except Exception as e:
            print(f"Wake screen error: {e}")
    
    def check_reminders(self):
        """Backup check - AlarmManager should handle this"""
        try:
            now = datetime.datetime.now()
            current_minute = now.hour * 60 + now.minute
            
            if current_minute == self.last_check_minute:
                return
            
            self.last_check_minute = current_minute
            current_day = now.weekday()
            
            reminders = self.load_reminders()
            
            for idx, r in enumerate(reminders):
                if not r.get('enabled'):
                    continue
                
                if current_day not in r.get('days', list(range(7))):
                    continue
                
                if r['hour'] == now.hour and r['minute'] == now.minute:
                    reminder_key = f"{idx}_{r['hour']:02d}{r['minute']:02d}_{now.date()}"
                    
                    if reminder_key not in self.triggered_reminders:
                        print(f"Backup trigger: {r['text']}")
                        self.show_alarm_notification(r, idx)
                        self.vibrate(r.get('priority', 'Medium'))
                        self.play_alarm(r)
                        self.wake_screen()
                        self.triggered_reminders.add(reminder_key)
            
            if now.hour == 0 and now.minute == 0:
                self.triggered_reminders.clear()
                
        except Exception as e:
            print(f"Check reminders error: {e}")
    
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
            builder.setContentTitle("⏰ My Reminders")
            builder.setContentText("Alarm service active")
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentIntent(pending_intent)
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            builder.setOngoing(True)
            
            notification = builder.build()
            self.service.startForeground(1, notification)
            print("Service in foreground")
            
        except Exception as e:
            print(f"Foreground error: {e}")
    
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
    
    def __del__(self):
        """Cleanup"""
        try:
            if self.wake_lock and self.wake_lock.isHeld():
                self.wake_lock.release()
        except:
            pass


if __name__ == "__main__":
    try:
        service = ReminderService()
        service.run()
    except Exception as e:
        print(f"Service crash: {e}")
        import traceback
        traceback.print_exc()
