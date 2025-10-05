"""
AlarmManager Receiver Service
This handles alarms even when the app is completely closed
"""
import os
import json
from jnius import autoclass

PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
NotificationChannel = autoclass('android.app.NotificationChannel')
PendingIntent = autoclass('android.app.PendingIntent')
Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Vibrator = autoclass('android.os.Vibrator')
VibrationEffect = autoclass('android.os.VibrationEffect')
VERSION = autoclass('android.os.Build$VERSION')
MediaPlayer = autoclass('android.media.MediaPlayer')
AudioManager = autoclass('android.media.AudioManager')
Uri = autoclass('android.net.Uri')
RingtoneManager = autoclass('android.media.RingtoneManager')
PowerManager = autoclass('android.os.PowerManager')
AudioAttributes = autoclass('android.media.AudioAttributes')

print("AlarmReceiver service starting...")


class AlarmReceiver:
    def __init__(self):
        self.service = PythonService.mService
        self.media_player = None
        print("AlarmReceiver initialized")
    
    def show_fullscreen_alarm(self, reminder_id):
        """Show full-screen notification with alarm"""
        try:
            # Load reminder data
            data_dir = self.service.getFilesDir().getAbsolutePath()
            data_file = os.path.join(data_dir, 'reminders.json')
            
            reminder = None
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    reminders = json.load(f)
                    if 0 <= reminder_id < len(reminders):
                        reminder = reminders[reminder_id]
            
            if not reminder:
                print(f"Reminder {reminder_id} not found")
                return
            
            # Create notification channel
            notification_service = self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            
            channel_id = "alarm_fullscreen"
            channel = NotificationChannel(
                channel_id,
                "Alarm Notifications",
                NotificationManager.IMPORTANCE_HIGH
            )
            channel.setDescription("Full-screen alarm notifications")
            channel.enableVibration(True)
            channel.setVibrationPattern([0, 1000, 500, 1000])
            channel.setLockscreenVisibility(1)
            channel.setBypassDnd(True)
            
            # Set alarm sound
            alarm_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            audio_attributes = AudioAttributes.Builder() \
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION) \
                .setUsage(AudioAttributes.USAGE_ALARM) \
                .build()
            channel.setSound(alarm_uri, audio_attributes)
            
            notification_service.createNotificationChannel(channel)
            
            # Wake up the device
            power_manager = self.service.getSystemService(Context.POWER_SERVICE)
            wake_lock = power_manager.newWakeLock(
                PowerManager.SCREEN_BRIGHT_WAKE_LOCK | 
                PowerManager.ACQUIRE_CAUSES_WAKEUP |
                PowerManager.ON_AFTER_RELEASE,
                "AlarmReceiver::WakeLock"
            )
            wake_lock.acquire(60000)  # 60 seconds
            
            # Create full-screen intent
            full_screen_intent = Intent(self.service, PythonActivity)
            full_screen_intent.setFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK | 
                Intent.FLAG_ACTIVITY_CLEAR_TOP |
                Intent.FLAG_ACTIVITY_SINGLE_TOP
            )
            full_screen_intent.putExtra("alarm_triggered", True)
            full_screen_intent.putExtra("reminder_id", reminder_id)
            
            full_screen_pending = PendingIntent.getActivity(
                self.service,
                reminder_id + 10000,
                full_screen_intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Dismiss action
            dismiss_intent = Intent(self.service, PythonService)
            dismiss_intent.setAction("DISMISS_ALARM")
            dismiss_intent.putExtra("reminder_id", reminder_id)
            
            dismiss_pending = PendingIntent.getService(
                self.service,
                reminder_id + 20000,
                dismiss_intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Build notification
            builder = NotificationCompat.Builder(self.service, channel_id)
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentTitle(f"REMINDER: {reminder.get('category', 'Reminder')}")
            builder.setContentText(reminder['text'])
            builder.setPriority(NotificationCompat.PRIORITY_MAX)
            builder.setCategory(NotificationCompat.CATEGORY_ALARM)
            builder.setAutoCancel(False)
            builder.setOngoing(True)
            builder.setFullScreenIntent(full_screen_pending, True)
            builder.setContentIntent(full_screen_pending)
            
            # Add dismiss button
            builder.addAction(
                0,
                "Dismiss",
                dismiss_pending
            )
            
            # Vibration
            builder.setVibrate([0, 1000, 500, 1000, 500, 1000])
            
            # Sound
            builder.setSound(alarm_uri)
            
            # Style with note
            if reminder.get('note'):
                builder.setStyle(
                    NotificationCompat.BigTextStyle()
                    .bigText(f"{reminder['text']}\n\nNote: {reminder['note']}")
                )
            
            notification = builder.build()
            notification.flags |= (
                notification.FLAG_INSISTENT |
                notification.FLAG_NO_CLEAR |
                notification.FLAG_ONGOING_EVENT
            )
            
            notification_service.notify(3000 + reminder_id, notification)
            
            print(f"Full-screen alarm notification shown for reminder {reminder_id}")
            
            # Start vibration
            self.vibrate()
            
            # Play alarm sound
            self.play_alarm()
            
            # Launch activity
            self.service.startActivity(full_screen_intent)
            
        except Exception as e:
            print(f"Show fullscreen alarm error: {e}")
            import traceback
            traceback.print_exc()
    
    def vibrate(self):
        """Vibrate the device"""
        try:
            vibrator = self.service.getSystemService(Context.VIBRATOR_SERVICE)
            
            pattern = [0, 1000, 500, 1000, 500, 1000, 500, 1000]
            
            if VERSION.SDK_INT >= 26:
                effect = VibrationEffect.createWaveform(pattern, 0)  # Repeat
                vibrator.vibrate(effect)
            else:
                vibrator.vibrate(pattern, 0)  # Repeat
            
            print("Vibration started")
        except Exception as e:
            print(f"Vibration error: {e}")
    
    def play_alarm(self):
        """Play alarm sound"""
        try:
            if self.media_player:
                try:
                    self.media_player.stop()
                    self.media_player.release()
                except:
                    pass
            
            self.media_player = MediaPlayer()
            self.media_player.setAudioStreamType(AudioManager.STREAM_ALARM)
            
            alarm_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            self.media_player.setDataSource(self.service, alarm_uri)
            self.media_player.setLooping(True)
            self.media_player.prepare()
            self.media_player.start()
            
            print("Alarm sound playing")
            
        except Exception as e:
            print(f"Play alarm error: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_alarm(self):
        """Stop alarm sound and vibration"""
        try:
            # Stop sound
            if self.media_player:
                self.media_player.stop()
                self.media_player.release()
                self.media_player = None
            
            # Stop vibration
            vibrator = self.service.getSystemService(Context.VIBRATOR_SERVICE)
            vibrator.cancel()
            
            print("Alarm stopped")
            
        except Exception as e:
            print(f"Stop alarm error: {e}")
    
    def handle_intent(self, intent):
        """Handle incoming intent"""
        try:
            action = intent.getAction()
            
            if action and action.startswith("REMINDER_ALARM_"):
                reminder_id = intent.getIntExtra("reminder_id", -1)
                print(f"Alarm received for reminder {reminder_id}")
                self.show_fullscreen_alarm(reminder_id)
            
            elif action == "DISMISS_ALARM":
                reminder_id = intent.getIntExtra("reminder_id", -1)
                print(f"Dismissing alarm {reminder_id}")
                self.stop_alarm()
                
                # Cancel notification
                notification_service = self.service.getSystemService(Context.NOTIFICATION_SERVICE)
                notification_service.cancel(3000 + reminder_id)
            
        except Exception as e:
            print(f"Handle intent error: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Main service loop"""
        print("AlarmReceiver running...")
        
        # Start as foreground service
        self.start_foreground()
        
        # Keep service alive
        import time
        while True:
            time.sleep(10)
    
    def start_foreground(self):
        """Start as foreground service"""
        try:
            notification_service = self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            
            channel_id = "service_channel"
            channel = NotificationChannel(
                channel_id,
                "Alarm Service",
                NotificationManager.IMPORTANCE_LOW
            )
            notification_service.createNotificationChannel(channel)
            
            intent = Intent(self.service, PythonActivity)
            pending_intent = PendingIntent.getActivity(
                self.service,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            builder = NotificationCompat.Builder(self.service, channel_id)
            builder.setContentTitle("My Reminders")
            builder.setContentText("Alarm service active")
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setContentIntent(pending_intent)
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            builder.setOngoing(True)
            
            notification = builder.build()
            self.service.startForeground(1, notification)
            
            print("Service started in foreground")
            
        except Exception as e:
            print(f"Start foreground error: {e}")


if __name__ == "__main__":
    try:
        receiver = AlarmReceiver()
        receiver.run()
    except Exception as e:
        print(f"Service crash: {e}")
        import traceback
        traceback.print_exc()
