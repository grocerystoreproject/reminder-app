import os
import json
import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.config import Config

print("Enhanced Reminder App starting...")

class ThemeManager:
    """Manages dark and light themes"""
    def __init__(self):
        self.is_dark = False
        self.themes = {
            'light': {
                'bg': (0.95, 0.96, 0.98, 1),
                'card': (1, 1, 1, 1),
                'primary': (0.25, 0.55, 0.95, 1),
                'text': (0.2, 0.2, 0.25, 1),
                'text_secondary': (0.5, 0.55, 0.65, 1),
                'accent': (0.2, 0.75, 0.5, 1)
            },
            'dark': {
                'bg': (0.08, 0.08, 0.12, 1),
                'card': (0.12, 0.12, 0.18, 1),
                'primary': (0.3, 0.6, 0.95, 1),
                'text': (0.9, 0.9, 0.95, 1),
                'text_secondary': (0.6, 0.65, 0.7, 1),
                'accent': (0.2, 0.75, 0.5, 1)
            }
        }
    
    def get(self, key):
        theme = 'dark' if self.is_dark else 'light'
        return self.themes[theme].get(key, (1, 1, 1, 1))
    
    def toggle(self):
        self.is_dark = not self.is_dark
        Window.clearcolor = self.get('bg')

THEME = ThemeManager()

if platform == 'android':
    print("Requesting Android permissions...")
    try:
        from android.permissions import request_permissions, Permission
        from jnius import autoclass
        
        permissions = [
            Permission.VIBRATE,
            Permission.WAKE_LOCK,
            Permission.SCHEDULE_EXACT_ALARM,
            Permission.POST_NOTIFICATIONS,
            Permission.USE_EXACT_ALARM,
            Permission.FOREGROUND_SERVICE,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_MEDIA_AUDIO,
        ]
        
        request_permissions(permissions)
        print("Permissions requested")
        
        def request_special_permissions():
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                Build = autoclass('android.os.Build')
                
                activity = PythonActivity.mActivity
                
                if Build.VERSION.SDK_INT >= 31:
                    AlarmManager = autoclass('android.app.AlarmManager')
                    alarm_manager = activity.getSystemService('alarm')
                    
                    if not alarm_manager.canScheduleExactAlarms():
                        intent = Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
                        activity.startActivity(intent)
                
                PowerManager = autoclass('android.os.PowerManager')
                power_manager = activity.getSystemService('power')
                package_name = activity.getPackageName()
                
                if not power_manager.isIgnoringBatteryOptimizations(package_name):
                    intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                    intent.setData(Uri.parse(f"package:{package_name}"))
                    activity.startActivity(intent)
                    
            except Exception as e:
                print(f"Special permission error: {e}")
        
        Clock.schedule_once(lambda dt: request_special_permissions(), 2)
        
    except Exception as e:
        print(f"Permission error: {e}")


def schedule_alarm_with_manager(reminder_id, hour, minute, days):
    """Schedule alarm using Android AlarmManager - WORKS WHEN APP IS CLOSED"""
    if platform == 'android':
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            PendingIntent = autoclass('android.app.PendingIntent')
            AlarmManager = autoclass('android.app.AlarmManager')
            Calendar = autoclass('java.util.Calendar')
            
            activity = PythonActivity.mActivity
            alarm_manager = activity.getSystemService('alarm')
            
            # Create intent for alarm receiver
            intent = Intent(activity, PythonActivity)
            intent.setAction(f"REMINDER_ALARM_{reminder_id}")
            intent.putExtra("reminder_id", reminder_id)
            
            pending_intent = PendingIntent.getBroadcast(
                activity, 
                reminder_id, 
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Schedule for each selected day
            for day in days:
                calendar = Calendar.getInstance()
                calendar.set(Calendar.HOUR_OF_DAY, hour)
                calendar.set(Calendar.MINUTE, minute)
                calendar.set(Calendar.SECOND, 0)
                calendar.set(Calendar.MILLISECOND, 0)
                
                # Set day of week (Calendar uses 1=Sunday, so add 1 and wrap)
                target_day = ((day + 1) % 7) + 1
                calendar.set(Calendar.DAY_OF_WEEK, target_day)
                
                # If time has passed today, schedule for next week
                now = Calendar.getInstance()
                if calendar.before(now):
                    calendar.add(Calendar.WEEK_OF_YEAR, 1)
                
                trigger_time = calendar.getTimeInMillis()
                
                # Use setExactAndAllowWhileIdle for better reliability
                alarm_manager.setExactAndAllowWhileIdle(
                    AlarmManager.RTC_WAKEUP,
                    trigger_time,
                    pending_intent
                )
            
            print(f"AlarmManager scheduled for reminder {reminder_id} at {hour}:{minute:02d}")
            return True
            
        except Exception as e:
            print(f"AlarmManager schedule error: {e}")
            import traceback
            traceback.print_exc()
    return False


def cancel_alarm_with_manager(reminder_id):
    """Cancel scheduled alarm"""
    if platform == 'android':
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            PendingIntent = autoclass('android.app.PendingIntent')
            AlarmManager = autoclass('android.app.AlarmManager')
            
            activity = PythonActivity.mActivity
            alarm_manager = activity.getSystemService('alarm')
            
            intent = Intent(activity, PythonActivity)
            intent.setAction(f"REMINDER_ALARM_{reminder_id}")
            
            pending_intent = PendingIntent.getBroadcast(
                activity,
                reminder_id,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            alarm_manager.cancel(pending_intent)
            print(f"AlarmManager cancelled for reminder {reminder_id}")
            
        except Exception as e:
            print(f"AlarmManager cancel error: {e}")


def show_full_screen_notification(reminder):
    """Show modern full-screen notification"""
    if platform == 'android':
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            NotificationManager = autoclass('android.app.NotificationManager')
            NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
            NotificationChannel = autoclass('android.app.NotificationChannel')
            PendingIntent = autoclass('android.app.PendingIntent')
            Intent = autoclass('android.content.Intent')
            RingtoneManager = autoclass('android.media.RingtoneManager')
            Uri = autoclass('android.net.Uri')
            AudioAttributes = autoclass('android.media.AudioAttributes')
            
            activity = PythonActivity.mActivity
            notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            
            # Create high-importance channel
            channel_id = "reminder_fullscreen"
            channel = NotificationChannel(
                channel_id,
                "Reminder Alarms",
                NotificationManager.IMPORTANCE_HIGH
            )
            channel.setDescription("Full-screen alarm notifications")
            channel.enableVibration(True)
            channel.setVibrationPattern([0, 500, 200, 500])
            channel.setLockscreenVisibility(1)
            channel.setBypassDnd(True)
            
            sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            audio_attributes = AudioAttributes.Builder() \
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION) \
                .setUsage(AudioAttributes.USAGE_ALARM) \
                .build()
            channel.setSound(sound_uri, audio_attributes)
            
            notification_service.createNotificationChannel(channel)
            
            # Create full-screen intent
            full_screen_intent = Intent(activity, PythonActivity)
            full_screen_intent.setFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK | 
                Intent.FLAG_ACTIVITY_CLEAR_TOP
            )
            
            full_screen_pending = PendingIntent.getActivity(
                activity,
                0,
                full_screen_intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
            
            # Build notification
            builder = NotificationCompat.Builder(activity, channel_id)
            builder.setSmallIcon(activity.getApplicationInfo().icon)
            builder.setContentTitle(f"REMINDER: {reminder.get('category', 'Personal')}")
            builder.setContentText(reminder['text'])
            builder.setPriority(NotificationCompat.PRIORITY_MAX)
            builder.setCategory(NotificationCompat.CATEGORY_ALARM)
            builder.setAutoCancel(False)
            builder.setOngoing(True)
            builder.setFullScreenIntent(full_screen_pending, True)
            builder.setVibrate([0, 500, 200, 500])
            builder.setSound(sound_uri)
            
            # Add note if exists
            if reminder.get('note'):
                builder.setStyle(
                    NotificationCompat.BigTextStyle()
                    .bigText(f"{reminder['text']}\n\nNote: {reminder['note']}")
                )
            
            notification = builder.build()
            notification.flags |= notification.FLAG_INSISTENT
            notification_service.notify(2001, notification)
            
            print("Full-screen notification shown")
            
        except Exception as e:
            print(f"Full-screen notification error: {e}")
            import traceback
            traceback.print_exc()


class ModernCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            self.shadow_color = Color(0, 0, 0, 0.1)
            self.shadow = RoundedRectangle(radius=[dp(16)])
            
            self.bg_color = Color(*THEME.get('card'))
            self.bg_rect = RoundedRectangle(radius=[dp(16)])
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.shadow.pos = (self.pos[0] + dp(2), self.pos[1] - dp(2))
        self.shadow.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
        self.bg_color.rgba = THEME.get('card')


class ReminderCard(ModernCard):
    def __init__(self, reminder, index, callbacks, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(140)
        self.padding = [dp(16), dp(12), dp(16), dp(12)]
        self.spacing = dp(8)
        
        # Header
        header = BoxLayout(size_hint_y=0.3, spacing=dp(8))
        
        category = Label(
            text=reminder.get('category', 'Personal'),
            font_size='12sp',
            bold=True,
            color=THEME.get('primary'),
            size_hint_x=0.4,
            halign='left'
        )
        category.bind(size=category.setter('text_size'))
        header.add_widget(category)
        
        header.add_widget(Label(size_hint_x=0.3))
        
        time_label = Label(
            text=reminder['time'].strftime('%I:%M %p'),
            font_size='20sp',
            bold=True,
            color=THEME.get('text'),
            size_hint_x=0.3,
            halign='right'
        )
        time_label.bind(size=time_label.setter('text_size'))
        header.add_widget(time_label)
        
        self.add_widget(header)
        
        # Text
        text_label = Label(
            text=reminder['text'],
            font_size='14sp',
            color=THEME.get('text'),
            size_hint_y=0.4,
            halign='left',
            valign='top'
        )
        text_label.bind(size=lambda *x: setattr(text_label, 'text_size', (text_label.width, None)))
        self.add_widget(text_label)
        
        # Buttons
        btn_row = BoxLayout(size_hint_y=0.3, spacing=dp(6))
        
        toggle_btn = ToggleButton(
            state='down' if reminder.get('enabled') else 'normal',
            text="ON" if reminder.get('enabled') else "OFF",
            size_hint_x=0.25,
            background_normal='',
            background_color=THEME.get('accent') if reminder.get('enabled') else (0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='11sp',
            bold=True
        )
        toggle_btn.bind(on_press=lambda x: callbacks['toggle'](index))
        
        edit_btn = Button(
            text="Edit",
            size_hint_x=0.4,
            background_normal='',
            background_color=THEME.get('primary'),
            color=(1, 1, 1, 1),
            font_size='12sp',
            bold=True
        )
        edit_btn.bind(on_press=lambda x: callbacks['edit'](index))
        
        del_btn = Button(
            text="Delete",
            size_hint_x=0.35,
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='12sp',
            bold=True
        )
        del_btn.bind(on_press=lambda x: callbacks['delete'](index))
        
        btn_row.add_widget(toggle_btn)
        btn_row.add_widget(edit_btn)
        btn_row.add_widget(del_btn)
        
        self.add_widget(btn_row)


class ReminderApp(App):
    def build(self):
        print("Building UI...")
        self.reminders = []
        self.editing_index = None
        
        try:
            if platform == 'android':
                self.data_dir = self.user_data_dir
            else:
                self.data_dir = os.path.dirname(os.path.abspath(__file__))
            
            self.data_file = os.path.join(self.data_dir, 'reminders.json')
        except Exception as e:
            print(f"Data dir error: {e}")
            self.data_file = 'reminders.json'
        
        self.load_reminders()
        Window.clearcolor = THEME.get('bg')

        root = FloatLayout()
        self.layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))

        # Header with theme toggle
        header = ModernCard()
        header.size_hint = (1, None)
        header.height = dp(100)
        header.padding = [dp(16), dp(12)]
        header.orientation = 'vertical'
        
        title_row = BoxLayout(size_hint_y=0.5)
        title = Label(
            text="My Reminders",
            font_size='24sp',
            bold=True,
            halign='left',
            color=THEME.get('text')
        )
        title.bind(size=title.setter('text_size'))
        self.title_label = title
        title_row.add_widget(title)
        
        theme_btn = Button(
            text="Theme",
            size_hint=(None, 1),
            width=dp(80),
            background_normal='',
            background_color=THEME.get('primary'),
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True
        )
        theme_btn.bind(on_press=self.toggle_theme)
        title_row.add_widget(theme_btn)
        
        header.add_widget(title_row)
        
        time_row = BoxLayout(size_hint_y=0.5)
        self.time_label = Label(
            text="",
            font_size='16sp',
            halign='left',
            color=THEME.get('text_secondary')
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        time_row.add_widget(self.time_label)
        header.add_widget(time_row)
        
        self.layout.add_widget(header)
        Clock.schedule_interval(self.update_time, 1)

        # Add button
        add_btn = Button(
            text="+ Add New Reminder",
            size_hint=(1, None),
            height=dp(54),
            background_normal='',
            background_color=THEME.get('accent'),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        add_btn.bind(on_press=self.show_add_dialog)
        self.layout.add_widget(add_btn)

        # Reminders list
        scroll = ScrollView(size_hint=(1, 1))
        self.reminder_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10),
            padding=[0, dp(6), 0, dp(12)]
        )
        self.reminder_list.bind(minimum_height=self.reminder_list.setter('height'))
        scroll.add_widget(self.reminder_list)
        self.layout.add_widget(scroll)

        root.add_widget(self.layout)
        
        self.refresh_reminder_list()
        
        print("UI built successfully")
        return root

    def toggle_theme(self, instance):
        THEME.toggle()
        self.title_label.color = THEME.get('text')
        self.time_label.color = THEME.get('text_secondary')
        instance.background_color = THEME.get('primary')
        self.refresh_reminder_list()

    def update_time(self, dt):
        now = datetime.datetime.now()
        self.time_label.text = now.strftime('%A, %B %d - %I:%M %p')

    def load_reminders(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        h, m = map(int, item['time'].split(':'))
                        self.reminders.append({
                            'text': item['text'],
                            'time': datetime.time(h, m),
                            'enabled': item.get('enabled', True),
                            'days': item.get('days', list(range(7))),
                            'ringtone_uri': item.get('ringtone_uri', None),
                            'category': item.get('category', 'Personal'),
                            'priority': item.get('priority', 'Medium'),
                            'note': item.get('note', '')
                        })
                print(f"Loaded {len(self.reminders)} reminders")
        except Exception as e:
            print(f"Load error: {e}")

    def save_reminders(self):
        try:
            data = [{
                'text': r['text'],
                'time': r['time'].strftime('%H:%M'),
                'enabled': r.get('enabled', True),
                'days': r.get('days', list(range(7))),
                'ringtone_uri': r.get('ringtone_uri', None),
                'category': r.get('category', 'Personal'),
                'priority': r.get('priority', 'Medium'),
                'note': r.get('note', '')
            } for r in self.reminders]
            
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {len(data)} reminders")
            
            # Reschedule all alarms
            self.reschedule_all_alarms()
            
        except Exception as e:
            print(f"Save error: {e}")

    def reschedule_all_alarms(self):
        """Reschedule all enabled reminders with AlarmManager"""
        for idx, r in enumerate(self.reminders):
            if r.get('enabled'):
                schedule_alarm_with_manager(
                    idx,
                    r['time'].hour,
                    r['time'].minute,
                    r.get('days', list(range(7)))
                )
            else:
                cancel_alarm_with_manager(idx)

    def show_add_dialog(self, instance):
        self.editing_index = None
        self.show_reminder_dialog()

    def show_reminder_dialog(self, reminder=None):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(16))
        
        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        
        # Title
        form.add_widget(Label(
            text="Edit Reminder" if reminder else "New Reminder",
            font_size='20sp',
            bold=True,
            size_hint=(1, None),
            height=dp(35),
            color=THEME.get('text')
        ))
        
        # Text input
        text_input = TextInput(
            hint_text="What to remind?",
            size_hint=(1, None),
            height=dp(45),
            multiline=False,
            background_color=THEME.get('card'),
            foreground_color=THEME.get('text'),
            font_size='14sp'
        )
        if reminder:
            text_input.text = reminder['text']
        form.add_widget(text_input)

        # Category
        category_spinner = Spinner(
            text=reminder.get('category', 'Personal') if reminder else 'Personal',
            values=['Work', 'Personal', 'Health', 'Shopping', 'Other'],
            size_hint=(1, None),
            height=dp(40),
            background_color=THEME.get('card'),
            color=THEME.get('text')
        )
        form.add_widget(category_spinner)

        # Time
        time_box = BoxLayout(size_hint=(1, None), height=dp(45), spacing=dp(6))
        
        hour = Spinner(
            text=str(reminder['time'].hour % 12 or 12) if reminder else "9",
            values=[str(i) for i in range(1, 13)],
            size_hint=(0.3, 1),
            background_color=THEME.get('card'),
            color=THEME.get('text')
        )
        
        colon = Label(text=":", size_hint=(0.08, 1), font_size='20sp', color=THEME.get('text'))
        
        minute = Spinner(
            text=str(reminder['time'].minute).zfill(2) if reminder else "00",
            values=[str(i).zfill(2) for i in range(0, 60)],
            size_hint=(0.3, 1),
            background_color=THEME.get('card'),
            color=THEME.get('text')
        )
        
        ampm = Spinner(
            text="PM" if reminder and reminder['time'].hour >= 12 else "AM",
            values=["AM", "PM"],
            size_hint=(0.32, 1),
            background_color=THEME.get('card'),
            color=THEME.get('text')
        )
        
        time_box.add_widget(hour)
        time_box.add_widget(colon)
        time_box.add_widget(minute)
        time_box.add_widget(ampm)
        form.add_widget(time_box)

        # Days
        days_box = BoxLayout(size_hint=(1, None), height=dp(60), spacing=dp(3))
        day_names = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        day_checks = []
        
        for i, day in enumerate(day_names):
            cb_box = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(2))
            
            cb = CheckBox(
                active=reminder and i in reminder.get('days', list(range(7))) if reminder else True,
                size_hint=(1, 0.6),
                color=THEME.get('primary')
            )
            
            day_lbl = Label(
                text=day,
                size_hint=(1, 0.4),
                font_size='11sp',
                color=THEME.get('text')
            )
            
            cb_box.add_widget(cb)
            cb_box.add_widget(day_lbl)
            day_checks.append(cb)
            days_box.add_widget(cb_box)
        
        form.add_widget(days_box)

        # Note
        note_input = TextInput(
            hint_text="Note (optional)",
            size_hint=(1, None),
            height=dp(60),
            multiline=True,
            background_color=THEME.get('card'),
            foreground_color=THEME.get('text'),
            font_size='13sp'
        )
        if reminder and reminder.get('note'):
            note_input.text = reminder['note']
        form.add_widget(note_input)

        scroll.add_widget(form)
        content.add_widget(scroll)

        # Buttons
        btn_box = BoxLayout(size_hint=(1, None), height=dp(48), spacing=dp(8))
        
        cancel_btn = Button(
            text="Cancel",
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        save_btn = Button(
            text="Save",
            background_normal='',
            background_color=THEME.get('accent'),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True
        )
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(save_btn)
        content.add_widget(btn_box)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.95, 0.85),
            separator_height=0,
            background_color=THEME.get('bg')
        )

        def save_reminder(instance):
            text = text_input.text.strip()
            if not text:
                return

            h = int(hour.text)
            m = int(minute.text)
            if ampm.text == "PM" and h != 12:
                h += 12
            elif ampm.text == "AM" and h == 12:
                h = 0

            selected_days = [i for i, cb in enumerate(day_checks) if cb.active]
            if not selected_days:
                return

            new_reminder = {
                'text': text,
                'time': datetime.time(h, m),
                'enabled': True,
                'days': sorted(selected_days),
                'category': category_spinner.text,
                'note': note_input.text.strip()
            }

            if self.editing_index is not None:
                self.reminders[self.editing_index] = new_reminder
                self.editing_index = None
            else:
                self.reminders.append(new_reminder)
            
            self.save_reminders()
            self.refresh_reminder_list()
            popup.dismiss()

        save_btn.bind(on_press=save_reminder)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def edit_reminder(self, index):
        if 0 <= index < len(self.reminders):
            self.editing_index = index
            self.show_reminder_dialog(self.reminders[index])

    def toggle_reminder(self, index):
        if 0 <= index < len(self.reminders):
            self.reminders[index]['enabled'] = not self.reminders[index].get('enabled', True)
            self.save_reminders()
            self.refresh_reminder_list()

    def delete_reminder(self, index):
        if 0 <= index < len(self.reminders):
            cancel_alarm_with_manager(index)
            del self.reminders[index]
            self.save_reminders()
            self.refresh_reminder_list()

    def refresh_reminder_list(self):
        self.reminder_list.clear_widgets()
        
        if not self.reminders:
            empty_card = ModernCard()
            empty_card.size_hint_y = None
            empty_card.height = dp(150)
            empty_card.padding = dp(20)
            
            empty_box = BoxLayout(orientation='vertical', spacing=dp(10))
            empty_box.add_widget(Label(
                text="No Reminders Yet",
                font_size='18sp',
                bold=True,
                color=THEME.get('text')
            ))
            empty_box.add_widget(Label(
                text="Tap 'Add New Reminder' to get started",
                font_size='13sp',
                color=THEME.get('text_secondary')
            ))
            
            empty_card.add_widget(empty_box)
            self.reminder_list.add_widget(empty_card)
            return
        
        callbacks = {
            'edit': self.edit_reminder,
            'toggle': self.toggle_reminder,
            'delete': self.delete_reminder
        }
        
        for idx, r in enumerate(self.reminders):
            self.reminder_list.add_widget(ReminderCard(r, idx, callbacks))

    def on_pause(self):
        print("App pausing - AlarmManager will continue working")
        return True

    def on_resume(self):
        print("App resuming")
        self.refresh_reminder_list()

    def on_stop(self):
        print("App stopping - AlarmManager alarms still active")
        self.save_reminders()


if __name__ == "__main__":
    print("Starting ReminderApp...")
    try:
        ReminderApp().run()
    except Exception as e:
        print(f"App crash: {e}")
        import traceback
        traceback.print_exc()
