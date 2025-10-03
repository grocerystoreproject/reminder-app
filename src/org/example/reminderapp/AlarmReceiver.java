package org.example.reminderapp;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import org.kivy.android.PythonActivity;

public class AlarmReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Intent i = new Intent(context, PythonActivity.class);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        i.putExtra("alarm_triggered", true);
        context.startActivity(i);
    }
}
