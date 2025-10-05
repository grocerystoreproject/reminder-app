package com.reminder.myreminders;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.app.NotificationManager;
import android.app.NotificationChannel;
import android.app.PendingIntent;
import android.media.RingtoneManager;
import android.media.AudioAttributes;
import android.net.Uri;
import android.os.Build;
import android.os.PowerManager;
import androidx.core.app.NotificationCompat;
import android.os.Vibrator;
import android.os.VibrationEffect;

/**
 * BroadcastReceiver that handles alarms even when app is completely closed
 * This is a native Java component that Android can wake up anytime
 */
public class AlarmBroadcastReceiver extends BroadcastReceiver {
    
    @Override
    public void onReceive(Context context, Intent intent) {
        // This method is called when the alarm triggers
        // It works even if the app is force-closed or phone was off
        
        String action = intent.getAction();
        if (action != null && action.startsWith("com.reminder.ALARM_")) {
            
            // Get reminder data from intent
            int reminderId = intent.getIntExtra("reminder_id", -1);
            String reminderText = intent.getStringExtra("reminder_text");
            String reminderCategory = intent.getStringExtra("reminder_category");
            String reminderNote = intent.getStringExtra("reminder_note");
            
            // Wake up the device
            wakeUpDevice(context);
            
            // Show notification
            showAlarmNotification(context, reminderId, reminderText, reminderCategory, reminderNote);
            
            // Vibrate
            vibrateDevice(context);
        }
    }
    
    private void wakeUpDevice(Context context) {
        PowerManager powerManager = (PowerManager) context.getSystemService(Context.POWER_SERVICE);
        PowerManager.WakeLock wakeLock = powerManager.newWakeLock(
            PowerManager.SCREEN_BRIGHT_WAKE_LOCK | 
            PowerManager.ACQUIRE_CAUSES_WAKEUP |
            PowerManager.ON_AFTER_RELEASE,
            "MyReminders::AlarmWakeLock"
        );
        wakeLock.acquire(60000); // 60 seconds
    }
    
    private void showAlarmNotification(Context context, int reminderId, String text, String category, String note) {
        NotificationManager notificationManager = 
            (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        
        String channelId = "reminder_alarm_channel";
        
        // Create notification channel for Android 8.0+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                channelId,
                "Reminder Alarms",
                NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("Full-screen alarm notifications");
            channel.enableVibration(true);
            channel.setVibrationPattern(new long[]{0, 1000, 500, 1000});
            channel.setLockscreenVisibility(NotificationCompat.VISIBILITY_PUBLIC);
            channel.setBypassDnd(true);
            
            // Set alarm sound
            Uri alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM);
            AudioAttributes audioAttributes = new AudioAttributes.Builder()
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .setUsage(AudioAttributes.USAGE_ALARM)
                .build();
            channel.setSound(alarmSound, audioAttributes);
            
            notificationManager.createNotificationChannel(channel);
        }
        
        // Create intent to open app
        Intent launchIntent = context.getPackageManager()
            .getLaunchIntentForPackage(context.getPackageName());
        if (launchIntent != null) {
            launchIntent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            launchIntent.putExtra("alarm_triggered", true);
            launchIntent.putExtra("reminder_id", reminderId);
        }
        
        PendingIntent pendingIntent = PendingIntent.getActivity(
            context,
            reminderId + 10000,
            launchIntent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        
        // Build notification
        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
            .setContentTitle("⏰ REMINDER: " + category)
            .setContentText(text)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(false)
            .setOngoing(true)
            .setFullScreenIntent(pendingIntent, true)
            .setContentIntent(pendingIntent)
            .setVibrate(new long[]{0, 1000, 500, 1000, 500, 1000})
            .setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM));
        
        // Add note if exists
        if (note != null && !note.isEmpty()) {
            builder.setStyle(new NotificationCompat.BigTextStyle()
                .bigText(text + "\n\n📝 " + note));
        }
        
        // Show notification
        notificationManager.notify(3000 + reminderId, builder.build());
    }
    
    private void vibrateDevice(Context context) {
        Vibrator vibrator = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
        long[] pattern = {0, 1000, 500, 1000, 500, 1000};
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            VibrationEffect effect = VibrationEffect.createWaveform(pattern, 0); // Repeat
            vibrator.vibrate(effect);
        } else {
            vibrator.vibrate(pattern, 0); // Repeat
        }
    }
}
