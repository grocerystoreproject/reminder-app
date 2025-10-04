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

print("Enhanced Reminder App starting...")

Window.clearcolor = (0.95, 0.96, 0.98, 1)

if platform == 'android':
    print("Requesting Android permissions...")
    try:
        from android.permissions import request_permissions, Permission, check_permission
        from jnius import autoclass
        
        # Request ALL necessary permissions
        permissions = [
            Permission.VIBRATE,
            Permission.WAKE_LOCK,
            Permission.SCHEDULE_EXACT_ALARM,
            Permission.POST_NOTIFICATIONS,
            Permission.USE_EXACT_ALARM,
            Permission.FOREGROUND_SERVICE,
            Permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_MEDIA_AUDIO,
        ]
        
        request_permissions(permissions)
        print("Permissions requested")
        
        # Request special permissions for Android 12+
        def request_special_permissions():
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                Build = autoclass('android.os.Build')
                
                activity = PythonActivity.mActivity
                
                # Request SCHEDULE_EXACT_ALARM for Android 12+
                if Build.VERSION.SDK_INT >= 31:
                    AlarmManager = autoclass('android.app.AlarmManager')
                    alarm_manager = activity.getSystemService('alarm')
                    
                    if not alarm_manager.canScheduleExactAlarms():
                        print("Requesting exact alarm permission...")
                        intent = Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
                        activity.startActivity(intent)
                
                # Request to ignore battery optimization
                PowerManager = autoclass('android.os.PowerManager')
                power_manager = activity.getSystemService('power')
                package_name = activity.getPackageName()
                
                if not power_manager.isIgnoringBatteryOptimizations(package_name):
                    print("Requesting battery optimization exemption...")
                    intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                    intent.setData(Uri.parse(f"package:{package_name}"))
                    activity.startActivity(intent)
                    
            except Exception as e:
                print(f"Special permission error: {e}")
        
        Clock.schedule_once(lambda dt: request_special_permissions(), 2)
        
    except Exception as e:
        print(f"Permission error: {e}")


def create_notification_channel():
    """Create notification channel for Android 8.0+"""
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            NotificationManager = autoclass('android.app.NotificationManager')
            NotificationChannel = autoclass('android.app.NotificationChannel')
            AudioAttributes = autoclass('android.media.AudioAttributes')
            RingtoneManager = autoclass('android.media.RingtoneManager')
            
            activity = PythonActivity.mActivity
            notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            
            channel_id = "reminder_channel"
            channel_name = "Reminder Notifications"
            importance = NotificationManager.IMPORTANCE_HIGH
            
            channel = NotificationChannel(channel_id, channel_name, importance)
            channel.setDescription("Notifications for reminders")
            channel.enableVibration(True)
            channel.setVibrationPattern([0, 500, 200, 500])
            channel.setLockscreenVisibility(1)  # Show on lockscreen
            channel.setBypassDnd(True)  # Bypass Do Not Disturb
            
            # Set default sound
            default_sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            audio_attributes = AudioAttributes.Builder() \
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION) \
                .setUsage(AudioAttributes.USAGE_ALARM) \
                .build()
            channel.setSound(default_sound_uri, audio_attributes)
            
            notification_service.createNotificationChannel(channel)
            print("Notification channel created with alarm sound")
        except Exception as e:
            print(f"Channel creation error: {e}")
            import traceback
            traceback.print_exc()


def start_background_service():
    """Start the background service for reminders"""
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonService = autoclass('org.kivy.android.PythonService')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Context = autoclass('android.content.Context')
            Build = autoclass('android.os.Build')
            
            activity = PythonActivity.mActivity
            
            service_intent = Intent(activity, PythonService)
            service_intent.putExtra("serviceTitle", "My Reminders")
            service_intent.putExtra("serviceDescription", "Monitoring reminders")
            
            # Start as foreground service on Android 8+
            if Build.VERSION.SDK_INT >= 26:
                activity.startForegroundService(service_intent)
            else:
                activity.startService(service_intent)
            
            print("Background service started")
        except Exception as e:
            print(f"Service start error: {e}")
            import traceback
            traceback.print_exc()


class ModernCard(BoxLayout):
    """Enhanced card with gradient-like effect"""
    def __init__(self, bg_color=(1, 1, 1, 1), accent_color=(0.3, 0.6, 0.95, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.accent_color = accent_color
        
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 0.15)
            self.shadow = RoundedRectangle(radius=[dp(18)])
            
            Color(*accent_color)
            self.accent_line = RoundedRectangle(radius=[dp(18), 0, 0, dp(18)])
            
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(radius=[dp(18)])
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.shadow.pos = (self.pos[0] + dp(3), self.pos[1] - dp(3))
        self.shadow.size = self.size
        
        self.accent_line.pos = self.pos
        self.accent_line.size = (dp(5), self.size[1])
        
        self.bg_rect.pos = (self.pos[0] + dp(5), self.pos[1])
        self.bg_rect.size = (self.size[0] - dp(5), self.size[1])


class CategoryChip(Button):
    """Small chip for categories"""
    def __init__(self, text, color=(0.3, 0.6, 0.95, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint = (None, None)
        self.size = (dp(80), dp(28))
        self.background_normal = ''
        self.background_color = (*color[:3], 0.15)
        self.color = color
        self.font_size = '12sp'
        self.bold = True
        
        with self.canvas.before:
            Color(*color[:3], 0.15)
            self.bg = RoundedRectangle(radius=[dp(14)])
        
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class ReminderCard(ModernCard):
    def __init__(self, reminder, index, callbacks, **kwargs):
        category = reminder.get('category', 'Personal')
        category_colors = {
            'Work': (0.95, 0.5, 0.2, 1),
            'Personal': (0.3, 0.65, 0.95, 1),
            'Health': (0.2, 0.8, 0.5, 1),
            'Shopping': (0.85, 0.35, 0.75, 1),
            'Other': (0.6, 0.6, 0.65, 1)
        }
        accent = category_colors.get(category, (0.3, 0.6, 0.95, 1))
        
        if not reminder.get('enabled', True):
            bg_color = (0.96, 0.96, 0.97, 1)
            accent = (0.7, 0.7, 0.72, 1)
        else:
            bg_color = (1, 1, 1, 1)
        
        super().__init__(bg_color=bg_color, accent_color=accent, **kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(160)
        self.padding = [dp(20), dp(16), dp(16), dp(16)]
        self.spacing = dp(10)
        
        header_row = BoxLayout(size_hint_y=0.25, spacing=dp(10))
        
        category_chip = CategoryChip(text=category, color=accent)
        header_row.add_widget(category_chip)
        header_row.add_widget(Label(size_hint_x=1))
        
        time_label = Label(
            text=reminder['time'].strftime('%I:%M %p'),
            font_size='22sp',
            bold=True,
            size_hint_x=None,
            width=dp(110),
            halign='right',
            color=accent if reminder.get('enabled') else (0.65, 0.65, 0.65, 1)
        )
        time_label.bind(size=time_label.setter('text_size'))
        header_row.add_widget(time_label)
        
        priority = reminder.get('priority', 'Medium')
        if priority == 'High':
            priority_indicator = Label(
                text="!!!",
                font_size='18sp',
                bold=True,
                color=(0.95, 0.3, 0.3, 1),
                size_hint_x=None,
                width=dp(30)
            )
            header_row.add_widget(priority_indicator)
        
        self.add_widget(header_row)
        
        text_label = Label(
            text=reminder['text'],
            halign='left',
            valign='top',
            font_size='16sp',
            color=(0.2, 0.2, 0.25, 1) if reminder.get('enabled') else (0.6, 0.6, 0.6, 1),
            size_hint_y=0.3,
            text_size=(None, None)
        )
        text_label.bind(size=lambda *x: setattr(text_label, 'text_size', (text_label.width, None)))
        self.add_widget(text_label)
        
        info_row = BoxLayout(size_hint_y=0.2, spacing=dp(12))
        
        days_map = {0: 'M', 1: 'T', 2: 'W', 3: 'T', 4: 'F', 5: 'S', 6: 'S'}
        selected_days = reminder.get('days', list(range(7)))
        
        if len(selected_days) == 7:
            days_text = "Every day"
        elif len(selected_days) == 5 and selected_days == [0, 1, 2, 3, 4]:
            days_text = "Weekdays"
        elif len(selected_days) == 2 and selected_days == [5, 6]:
            days_text = "Weekend"
        else:
            days_text = " ".join([days_map[d] for d in sorted(selected_days)])
        
        repeat_icon = Label(text="🔁", font_size='16sp', size_hint_x=None, width=dp(25))
        info_row.add_widget(repeat_icon)
        
        days_label = Label(
            text=days_text,
            halign='left',
            font_size='13sp',
            color=(0.45, 0.5, 0.6, 1),
            size_hint_x=0.5
        )
        days_label.bind(size=days_label.setter('text_size'))
        info_row.add_widget(days_label)
        
        if reminder.get('note'):
            note_icon = Label(text="📝", font_size='14sp', size_hint_x=None, width=dp(25))
            info_row.add_widget(note_icon)
        
        info_row.add_widget(Label(size_hint_x=1))
        self.add_widget(info_row)
        
        btn_row = BoxLayout(size_hint_y=0.25, spacing=dp(8))
        
        toggle_btn = ToggleButton(
            state='down' if reminder.get('enabled') else 'normal',
            size_hint_x=0.3,
            background_normal='',
            background_down='',
            background_color=(0.2, 0.75, 0.5, 1) if reminder.get('enabled') else (0.7, 0.7, 0.72, 1),
            color=(1, 1, 1, 1),
            font_size='12sp',
            bold=True
        )
        toggle_btn.text = "ON" if reminder.get('enabled') else "OFF"
        toggle_btn.bind(on_press=lambda x: callbacks['toggle'](index))
        
        edit_btn = Button(
            text="✏️ Edit",
            background_normal='',
            background_color=(0.35, 0.6, 0.95, 1),
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True,
            size_hint_x=0.4
        )
        edit_btn.bind(on_press=lambda x: callbacks['edit'](index))
        
        del_btn = Button(
            text="🗑️",
            background_normal='',
            background_color=(0.95, 0.4, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            size_hint_x=0.3
        )
        del_btn.bind(on_press=lambda x: callbacks['delete'](index))
        
        btn_row.add_widget(toggle_btn)
        btn_row.add_widget(edit_btn)
        btn_row.add_widget(del_btn)
        
        self.add_widget(btn_row)


class ReminderApp(App):
    def build(self):
        print("Building Enhanced UI...")
        self.reminders = []
        self.editing_index = None
        self.alarm_popup = None
        self.media_player = None
        self.snooze_minutes = 10
        self.triggered_reminders = set()
        self.last_check_minute = -1
        self.selected_ringtone_uri = None
        self.current_filter = 'All'
        self.current_sort = 'Time'
        
        try:
            if platform == 'android':
                self.data_dir = self.user_data_dir
            else:
                self.data_dir = os.path.dirname(os.path.abspath(__file__))
            
            self.data_file = os.path.join(self.data_dir, 'reminders.json')
        except Exception as e:
            print(f"Data dir error: {e}")
            self.data_file = 'reminders.json'
        
        create_notification_channel()
        
        # Start service after a delay to ensure app is fully initialized
        Clock.schedule_once(lambda dt: start_background_service(), 3)
        
        self.load_ringtones()
        self.load_reminders()

        root = FloatLayout()
        self.layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))

        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(140), spacing=0)
        
        top_header = ModernCard(
            bg_color=(0.25, 0.55, 0.95, 1),
            accent_color=(0.2, 0.45, 0.85, 1)
        )
        top_header.orientation = 'vertical'
        top_header.size_hint = (1, 0.65)
        top_header.padding = [dp(20), dp(14), dp(20), dp(10)]
        top_header.spacing = dp(6)
        
        title_row = BoxLayout(size_hint_y=0.5)
        title = Label(
            text="⏰ My Reminders",
            font_size='26sp',
            bold=True,
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        title_row.add_widget(title)
        
        settings_btn = Button(
            text="⚙️",
            size_hint=(None, 1),
            width=dp(45),
            background_normal='',
            background_color=(1, 1, 1, 0.2),
            color=(1, 1, 1, 1),
            font_size='20sp'
        )
        settings_btn.bind(on_press=self.show_settings)
        title_row.add_widget(settings_btn)
        
        time_row = BoxLayout(size_hint_y=0.5)
        self.time_label = Label(
            text="",
            font_size='20sp',
            halign='left',
            bold=True,
            color=(1, 1, 1, 0.95)
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        
        self.date_label = Label(
            text="",
            font_size='14sp',
            halign='right',
            color=(1, 1, 1, 0.85)
        )
        self.date_label.bind(size=self.date_label.setter('text_size'))
        
        time_row.add_widget(self.time_label)
        time_row.add_widget(self.date_label)
        
        top_header.add_widget(title_row)
        top_header.add_widget(time_row)
        header.add_widget(top_header)
        
        filter_bar = BoxLayout(size_hint=(1, 0.35), spacing=dp(8), padding=[0, dp(8), 0, 0])
        
        category_filter = Spinner(
            text='All',
            values=['All', 'Work', 'Personal', 'Health', 'Shopping', 'Other'],
            size_hint_x=0.5,
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0.3, 0.3, 0.4, 1),
            font_size='13sp'
        )
        category_filter.bind(text=self.filter_reminders)
        
        sort_spinner = Spinner(
            text='Time',
            values=['Time', 'Category', 'Priority'],
            size_hint_x=0.5,
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0.3, 0.3, 0.4, 1),
            font_size='13sp'
        )
        sort_spinner.bind(text=self.sort_reminders)
        
        filter_bar.add_widget(category_filter)
        filter_bar.add_widget(sort_spinner)
        header.add_widget(filter_bar)
        
        self.layout.add_widget(header)
        Clock.schedule_interval(self.update_time, 1)

        fab_container = BoxLayout(size_hint=(1, None), height=dp(70), padding=[0, dp(4), 0, dp(4)])
        
        add_btn = Button(
            text="+ Add New Reminder",
            size_hint=(1, 1),
            background_normal='',
            background_color=(0.2, 0.75, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='17sp',
            bold=True
        )
        add_btn.bind(on_press=self.show_add_dialog)
        
        with add_btn.canvas.before:
            Color(0.2, 0.75, 0.5, 1)
            add_btn.bg = RoundedRectangle(radius=[dp(16)])
        
        def update_fab_bg(*args):
            add_btn.bg.pos = add_btn.pos
            add_btn.bg.size = add_btn.size
        
        add_btn.bind(pos=update_fab_bg, size=update_fab_bg)
        fab_container.add_widget(add_btn)
        self.layout.add_widget(fab_container)

        stats_card = ModernCard(
            bg_color=(0.97, 0.98, 1, 1),
            accent_color=(0.3, 0.6, 0.95, 1)
        )
        stats_card.size_hint = (1, None)
        stats_card.height = dp(75)
        stats_card.padding = [dp(20), dp(12), dp(16), dp(12)]
        stats_card.orientation = 'horizontal'
        stats_card.spacing = dp(16)
        
        def create_stat_box(icon, value, label):
            box = BoxLayout(orientation='vertical', size_hint_x=1, spacing=dp(2))
            
            icon_label = Label(text=icon, font_size='22sp', size_hint_y=0.4)
            value_label = Label(
                text=str(value),
                font_size='20sp',
                bold=True,
                color=(0.2, 0.3, 0.5, 1),
                size_hint_y=0.35
            )
            text_label = Label(
                text=label,
                font_size='11sp',
                color=(0.5, 0.55, 0.65, 1),
                size_hint_y=0.25
            )
            
            box.add_widget(icon_label)
            box.add_widget(value_label)
            box.add_widget(text_label)
            return box, value_label
        
        total_box, self.total_stat = create_stat_box("📋", 0, "Total")
        active_box, self.active_stat = create_stat_box("✅", 0, "Active")
        today_box, self.today_stat = create_stat_box("📅", 0, "Today")
        
        stats_card.add_widget(total_box)
        stats_card.add_widget(active_box)
        stats_card.add_widget(today_box)
        
        self.layout.add_widget(stats_card)

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
        
        # Check reminders more frequently (every 5 seconds)
        Clock.schedule_interval(self.check_reminders, 5)
        
        print("Enhanced UI built successfully")
        return root

    def show_settings(self, instance):
        """Show settings and permissions dialog"""
        content = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(20))
        
        content.add_widget(Label(
            text="⚙️ Settings & Permissions",
            font_size='22sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.3, 0.5, 1)
        ))
        
        info_text = """For reminders to work properly:

✅ Allow notifications
✅ Allow exact alarms (Android 12+)
✅ Disable battery optimization
✅ Allow app to run in background

The app will request these permissions automatically."""
        
        info_label = Label(
            text=info_text,
            font_size='14sp',
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(180),
            color=(0.3, 0.3, 0.4, 1)
        )
        info_label.bind(size=info_label.setter('text_size'))
        content.add_widget(info_label)
        
        if platform == 'android':
            perm_btn = Button(
                text="📱 Open App Settings",
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=(0.3, 0.6, 0.95, 1),
                color=(1, 1, 1, 1),
                font_size='15sp',
                bold=True
            )
            
            def open_settings(btn):
                try:
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    Intent = autoclass('android.content.Intent')
                    Settings = autoclass('android.provider.Settings')
                    Uri = autoclass('android.net.Uri')
                    
                    activity = PythonActivity.mActivity
                    package_name = activity.getPackageName()
                    
                    intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                    intent.setData(Uri.parse(f"package:{package_name}"))
                    activity.startActivity(intent)
                except Exception as e:
                    print(f"Settings error: {e}")
            
            perm_btn.bind(on_press=open_settings)
            content.add_widget(perm_btn)
        
        restart_btn = Button(
            text="🔄 Restart Service",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.75, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='15sp',
            bold=True
        )
        
        def restart_service(btn):
            start_background_service()
            popup.dismiss()
        
        restart_btn.bind(on_press=restart_service)
        content.add_widget(restart_btn)
        
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=(0.7, 0.7, 0.72, 1),
            color=(1, 1, 1, 1),
            font_size='15sp',
            bold=True
        )
        
        popup = Popup(
            title="",
            content=content,
            size_hint=(0.9, 0.7),
            separator_height=0,
            background_color=(1, 1, 1, 0.98)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def filter_reminders(self, spinner, text):
        self.current_filter = text
        self.refresh_reminder_list()

    def sort_reminders(self, spinner, text):
        self.current_sort = text
        if text == 'Time':
            self.reminders.sort(key=lambda x: (x['time'].hour, x['time'].minute))
        elif text == 'Category':
            self.reminders.sort(key=lambda x: x.get('category', 'Personal'))
        elif text == 'Priority':
            priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
            self.reminders.sort(key=lambda x: priority_order.get(x.get('priority', 'Medium'), 1))
        self.save_reminders()
        self.refresh_reminder_list()

    def load_ringtones(self):
        self.ringtones = {
            'Default System Sound': 'SYSTEM_DEFAULT',
            'Vibrate Only': 'VIBRATE_ONLY'
        }
        
        if platform == 'android':
            self.ringtones['Browse for Sound File...'] = 'BROWSE'

    def browse_ringtone(self, callback):
        if platform == 'android':
            try:
                from jnius import autoclass
                from android import activity
                
                Intent = autoclass('android.content.Intent')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                def on_activity_result(request_code, result_code, intent):
                    if request_code == 1001 and result_code == -1 and intent:
                        uri = intent.getData()
                        if uri:
                            uri_string = uri.toString()
                            print(f"Selected ringtone URI: {uri_string}")
                            callback(uri_string)
                    activity.unbind(on_activity_result=on_activity_result)
                
                activity.bind(on_activity_result=on_activity_result)
                
                intent = Intent(Intent.ACTION_PICK)
                intent.setType("audio/*")
                
                current_activity = PythonActivity.mActivity
                current_activity.startActivityForResult(intent, 1001)
                
            except Exception as e:
                print(f"File browser error: {e}")
                callback('SYSTEM_DEFAULT')

    def update_time(self, dt):
        now = datetime.datetime.now()
        self.time_label.text = now.strftime('%I:%M %p')
        self.date_label.text = now.strftime('%A, %b %d')

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
                            'played': False,
                            'recurring': item.get('recurring', True),
                            'enabled': item.get('enabled', True),
                            'days': item.get('days', list(range(7))),
                            'snooze_until': None,
                            'ringtone': item.get('ringtone', 'Default System Sound'),
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
                'recurring': r.get('recurring', True),
                'enabled': r.get('enabled', True),
                'days': r.get('days', list(range(7))),
                'ringtone': r.get('ringtone', 'Default System Sound'),
                'ringtone_uri': r.get('ringtone_uri', None),
                'category': r.get('category', 'Personal'),
                'priority': r.get('priority', 'Medium'),
                'note': r.get('note', '')
            } for r in self.reminders]
            
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {len(data)} reminders")
        except Exception as e:
            print(f"Save error: {e}")

    def show_add_dialog(self, instance):
        self.editing_index = None
        self.show_reminder_dialog()

    def show_reminder_dialog(self, reminder=None):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(16))
        
        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        
        title_lbl = Label(
            text=("✏️ Edit Reminder" if reminder else "➕ New Reminder"),
            font_size='22sp',
            bold=True,
            size_hint=(1, None),
            height=dp(40),
            color=(0.2, 0.3, 0.5, 1)
        )
        form.add_widget(title_lbl)
        
        text_label = Label(
            text="What should I remind you?",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=dp(25),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        text_label.bind(size=text_label.setter('text_size'))
        form.add_widget(text_label)
        
        text_input = TextInput(
            hint_text="e.g., Take medicine, Call mom...",
            size_hint=(1, None),
            height=dp(50),
            multiline=False,
            background_color=(0.97, 0.98, 0.99, 1),
            foreground_color=(0.2, 0.2, 0.3, 1),
            padding=[dp(14), dp(16)],
            font_size='15sp'
        )
        if reminder:
            text_input.text = reminder['text']
        form.add_widget(text_input)

        cat_label = Label(
            text="Category",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=dp(28),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        cat_label.bind(size=cat_label.setter('text_size'))
        form.add_widget(cat_label)
        
        category_spinner = Spinner(
            text=reminder.get('category', 'Personal') if reminder else 'Personal',
            values=['Work', 'Personal', 'Health', 'Shopping', 'Other'],
            size_hint=(1, None),
            height=dp(45),
            background_color=(0.97, 0.98, 0.99, 1),
            font_size='14sp'
        )
        form.add_widget(category_spinner)

        priority_label = Label(
            text="Priority",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=dp(28),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        priority_label.bind(size=priority_label.setter('text_size'))
        form.add_widget(priority_label)
        
        priority_box = BoxLayout(size_hint=(1, None), height=dp(45), spacing=dp(8))
        
        priority_btns = []
        priorities = [('High', (0.95, 0.3, 0.3, 1)), ('Medium', (0.95, 0.7, 0.2, 1)), ('Low', (0.3, 0.7, 0.95, 1))]
        selected_priority = {'value': reminder.get('priority', 'Medium') if reminder else 'Medium'}
        
        for p_name, p_color in priorities:
            btn = ToggleButton(
                text=p_name,
                group='priority',
                state='down' if (reminder and reminder.get('priority') == p_name) or (not reminder and p_name == 'Medium') else 'normal',
                background_normal='',
                background_down='',
                background_color=p_color if (reminder and reminder.get('priority') == p_name) or (not reminder and p_name == 'Medium') else (0.9, 0.9, 0.92, 1),
                color=(1, 1, 1, 1) if (reminder and reminder.get('priority') == p_name) or (not reminder and p_name == 'Medium') else (0.5, 0.5, 0.55, 1),
                font_size='13sp',
                bold=True
            )
            
            def make_priority_callback(name, color, button):
                def callback(instance):
                    selected_priority['value'] = name
                    for pb in priority_btns:
                        if pb == button:
                            pb.background_color = color
                            pb.color = (1, 1, 1, 1)
                        else:
                            pb.background_color = (0.9, 0.9, 0.92, 1)
                            pb.color = (0.5, 0.5, 0.55, 1)
                return callback
            
            btn.bind(on_press=make_priority_callback(p_name, p_color, btn))
            priority_btns.append(btn)
            priority_box.add_widget(btn)
        
        form.add_widget(priority_box)

        time_label = Label(
            text="⏰ Set Time",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        time_label.bind(size=time_label.setter('text_size'))
        form.add_widget(time_label)
        
        time_box = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(6))
        
        hour = Spinner(
            text=str(reminder['time'].hour % 12 or 12) if reminder else "9",
            values=[str(i) for i in range(1, 13)],
            size_hint=(0.3, 1),
            background_color=(0.97, 0.98, 0.99, 1),
            font_size='16sp'
        )
        
        colon = Label(text=":", size_hint=(0.08, 1), font_size='22sp', bold=True)
        
        # FIXED: Allow every minute, not just 5-minute intervals
        minute = Spinner(
            text=str(reminder['time'].minute).zfill(2) if reminder else "00",
            values=[str(i).zfill(2) for i in range(0, 60)],  # Every minute 00-59
            size_hint=(0.3, 1),
            background_color=(0.97, 0.98, 0.99, 1),
            font_size='16sp'
        )
        
        ampm = Spinner(
            text="PM" if reminder and reminder['time'].hour >= 12 else "AM",
            values=["AM", "PM"],
            size_hint=(0.32, 1),
            background_color=(0.97, 0.98, 0.99, 1),
            font_size='16sp'
        )
        
        time_box.add_widget(hour)
        time_box.add_widget(colon)
        time_box.add_widget(minute)
        time_box.add_widget(ampm)
        form.add_widget(time_box)

        ringtone_label = Label(
            text="🔔 Ringtone",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=dp(28),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        ringtone_label.bind(size=ringtone_label.setter('text_size'))
        form.add_widget(ringtone_label)
        
        selected_ringtone_uri = {'uri': reminder.get('ringtone_uri') if reminder else None}
        
        ringtone_spinner = Spinner(
            text=reminder.get('ringtone', 'Default System Sound') if reminder else 'Default System Sound',
            values=sorted(self.ringtones.keys()),
            size_hint=(1, None),
            height=dp(45),
            background_color=(0.97, 0.98, 0.99, 1),
            font_size='14sp'
        )
        
        def on_ringtone_select(spinner, text):
            if text == 'Browse for Sound File...':
                def on_file_selected(uri):
                    selected_ringtone_uri['uri'] = uri
                    spinner.text = 'Custom Sound'
                self.browse_ringtone(on_file_selected)
        
        ringtone_spinner.bind(text=on_ringtone_select)
        form.add_widget(ringtone_spinner)

        days_label = Label(
            text="📅 Repeat On",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        days_label.bind(size=days_label.setter('text_size'))
        form.add_widget(days_label)
        
        days_box = BoxLayout(size_hint=(1, None), height=dp(65), spacing=dp(3))
        day_names = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        day_checks = []
        
        for i, day in enumerate(day_names):
            cb_box = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(3))
            
            cb = CheckBox(
                active=reminder and i in reminder.get('days', list(range(7))) if reminder else True,
                size_hint=(1, 0.6),
                color=(0.3, 0.6, 0.9, 1)
            )
            
            day_lbl = Label(
                text=day,
                size_hint=(1, 0.4),
                font_size='12sp',
                bold=True,
                color=(0.3, 0.4, 0.6, 1)
            )
            
            cb_box.add_widget(cb)
            cb_box.add_widget(day_lbl)
            day_checks.append(cb)
            days_box.add_widget(cb_box)
        
        form.add_widget(days_box)

        quick_box = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(6))
        
        def select_weekdays():
            for i, cb in enumerate(day_checks):
                cb.active = i < 5
        
        def select_weekend():
            for i, cb in enumerate(day_checks):
                cb.active = i >= 5
        
        def select_all():
            for cb in day_checks:
                cb.active = True
        
        quick_btns = [
            ("Weekdays", select_weekdays, (0.4, 0.6, 0.9, 1)),
            ("Weekend", select_weekend, (0.85, 0.5, 0.3, 1)),
            ("Every Day", select_all, (0.6, 0.4, 0.85, 1))
        ]
        
        for text, func, color in quick_btns:
            btn = Button(
                text=text,
                size_hint=(1, 1),
                background_normal='',
                background_color=color,
                color=(1, 1, 1, 1),
                font_size='12sp',
                bold=True
            )
            btn.bind(on_press=lambda x, f=func: f())
            quick_box.add_widget(btn)
        
        form.add_widget(quick_box)

        note_label = Label(
            text="📝 Note (Optional)",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=dp(28),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        note_label.bind(size=note_label.setter('text_size'))
        form.add_widget(note_label)
        
        note_input = TextInput(
            hint_text="Add any additional details...",
            size_hint=(1, None),
            height=dp(65),
            multiline=True,
            background_color=(0.97, 0.98, 0.99, 1),
            foreground_color=(0.2, 0.2, 0.3, 1),
            padding=[dp(14), dp(12)],
            font_size='14sp'
        )
        if reminder and reminder.get('note'):
            note_input.text = reminder['note']
        form.add_widget(note_input)

        scroll.add_widget(form)
        content.add_widget(scroll)

        btn_box = BoxLayout(size_hint=(1, None), height=dp(52), spacing=dp(10))
        
        cancel_btn = Button(
            text="✕ Cancel",
            background_normal='',
            background_color=(0.7, 0.7, 0.72, 1),
            color=(1, 1, 1, 1),
            font_size='15sp',
            bold=True
        )
        
        save_btn = Button(
            text="💾 Save Reminder",
            background_normal='',
            background_color=(0.2, 0.75, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='15sp',
            bold=True
        )
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(save_btn)
        content.add_widget(btn_box)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.96, 0.94),
            separator_height=0,
            background_color=(0.98, 0.99, 1, 0.98)
        )

        def save_reminder(instance):
            text = text_input.text.strip()
            if not text:
                text_input.hint_text = "⚠️ Please enter reminder text"
                text_input.background_color = (1, 0.9, 0.9, 1)
                return

            h = int(hour.text)
            m = int(minute.text)
            if ampm.text == "PM" and h != 12:
                h += 12
            elif ampm.text == "AM" and h == 12:
                h = 0

            selected_days = [i for i, cb in enumerate(day_checks) if cb.active]
            if not selected_days:
                days_label.text = "⚠️ Select at least one day"
                days_label.color = (0.95, 0.3, 0.3, 1)
                return

            new_reminder = {
                'text': text,
                'time': datetime.time(h, m),
                'played': False,
                'recurring': True,
                'enabled': True,
                'days': sorted(selected_days),
                'snooze_until': None,
                'ringtone': ringtone_spinner.text,
                'ringtone_uri': selected_ringtone_uri['uri'],
                'category': category_spinner.text,
                'priority': selected_priority['value'],
                'note': note_input.text.strip()
            }

            if self.editing_index is not None:
                self.reminders[self.editing_index] = new_reminder
                self.editing_index = None
            else:
                self.reminders.append(new_reminder)
            
            if self.current_sort == 'Time':
                self.reminders.sort(key=lambda x: (x['time'].hour, x['time'].minute))
            
            self.save_reminders()
            self.refresh_reminder_list()
            
            # Restart service to load new reminders
            if platform == 'android':
                Clock.schedule_once(lambda dt: start_background_service(), 0.5)
            
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
            self.reminders[index]['played'] = False
            
            reminder = self.reminders[index]
            reminder_key = f"{index}_{reminder['time'].hour:02d}{reminder['time'].minute:02d}"
            self.triggered_reminders.discard(reminder_key)
            
            self.save_reminders()
            self.refresh_reminder_list()
            
            # Restart service to reload reminders
            if platform == 'android':
                Clock.schedule_once(lambda dt: start_background_service(), 0.5)

    def delete_reminder(self, index):
        if 0 <= index < len(self.reminders):
            content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(22))
            
            icon_label = Label(
                text="🗑️",
                font_size='60sp',
                size_hint=(1, 0.3),
                color=(0.95, 0.4, 0.4, 1)
            )
            content.add_widget(icon_label)
            
            content.add_widget(Label(
                text="Delete this reminder?",
                font_size='19sp',
                bold=True,
                size_hint=(1, 0.18),
                color=(0.3, 0.3, 0.4, 1)
            ))
            
            reminder_text = Label(
                text=self.reminders[index]['text'],
                font_size='15sp',
                color=(0.5, 0.5, 0.55, 1),
                size_hint=(1, 0.22),
                halign='center'
            )
            reminder_text.bind(size=reminder_text.setter('text_size'))
            content.add_widget(reminder_text)
            
            btn_box = BoxLayout(size_hint=(1, 0.3), spacing=dp(12))
            
            cancel_btn = Button(
                text="Cancel",
                background_normal='',
                background_color=(0.7, 0.7, 0.72, 1),
                color=(1, 1, 1, 1),
                font_size='15sp',
                bold=True
            )
            
            delete_btn = Button(
                text="🗑️ Delete",
                background_normal='',
                background_color=(0.95, 0.4, 0.4, 1),
                color=(1, 1, 1, 1),
                font_size='15sp',
                bold=True
            )
            
            btn_box.add_widget(cancel_btn)
            btn_box.add_widget(delete_btn)
            content.add_widget(btn_box)
            
            confirm_popup = Popup(
                content=content,
                size_hint=(0.88, 0.48),
                title="",
                separator_height=0,
                background_color=(1, 1, 1, 0.98)
            )
            
            def do_delete(instance):
                reminder = self.reminders[index]
                reminder_key = f"{index}_{reminder['time'].hour:02d}{reminder['time'].minute:02d}"
                self.triggered_reminders.discard(reminder_key)
                
                del self.reminders[index]
                self.save_reminders()
                self.refresh_reminder_list()
                
                # Restart service to reload reminders
                if platform == 'android':
                    Clock.schedule_once(lambda dt: start_background_service(), 0.5)
                
                confirm_popup.dismiss()
            
            cancel_btn.bind(on_press=confirm_popup.dismiss)
            delete_btn.bind(on_press=do_delete)
            confirm_popup.open()

    def refresh_reminder_list(self):
        self.reminder_list.clear_widgets()
        
        filtered = self.reminders
        if self.current_filter != 'All':
            filtered = [r for r in self.reminders if r.get('category') == self.current_filter]
        
        active = sum(1 for r in self.reminders if r.get('enabled', True))
        total = len(self.reminders)
        
        today = datetime.datetime.now().weekday()
        today_reminders = sum(1 for r in self.reminders if r.get('enabled') and today in r.get('days', []))
        
        self.total_stat.text = str(total)
        self.active_stat.text = str(active)
        self.today_stat.text = str(today_reminders)
        
        if not filtered:
            empty_card = ModernCard(
                bg_color=(0.97, 0.98, 1, 1),
                accent_color=(0.3, 0.6, 0.95, 1)
            )
            empty_card.size_hint_y = None
            empty_card.height = dp(180)
            empty_card.padding = dp(24)
            
            empty_box = BoxLayout(orientation='vertical', spacing=dp(12))
            empty_box.add_widget(Label(
                text="📭",
                font_size='60sp',
                size_hint_y=0.4,
                color=(0.6, 0.7, 0.85, 1)
            ))
            empty_box.add_widget(Label(
                text="No Reminders" if self.current_filter == 'All' else f"No {self.current_filter} Reminders",
                font_size='20sp',
                bold=True,
                size_hint_y=0.3,
                color=(0.3, 0.4, 0.6, 1)
            ))
            empty_box.add_widget(Label(
                text="Tap the green button above to create your first reminder!",
                font_size='14sp',
                size_hint_y=0.3,
                color=(0.5, 0.6, 0.7, 1)
            ))
            
            empty_card.add_widget(empty_box)
            self.reminder_list.add_widget(empty_card)
            return
        
        callbacks = {
            'edit': self.edit_reminder,
            'toggle': self.toggle_reminder,
            'delete': self.delete_reminder
        }
        
        if self.current_sort == 'Category':
            categories = {}
            for idx, r in enumerate(filtered):
                cat = r.get('category', 'Personal')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((idx, r))
            
            for cat in sorted(categories.keys()):
                header = Label(
                    text=f"📂 {cat}",
                    size_hint=(1, None),
                    height=dp(35),
                    font_size='15sp',
                    bold=True,
                    halign='left',
                    color=(0.3, 0.4, 0.6, 1),
                    padding=[dp(8), 0]
                )
                header.bind(size=header.setter('text_size'))
                self.reminder_list.add_widget(header)
                
                for idx, r in categories[cat]:
                    actual_idx = self.reminders.index(r)
                    self.reminder_list.add_widget(ReminderCard(r, actual_idx, callbacks))
        else:
            for idx, r in enumerate(filtered):
                actual_idx = self.reminders.index(r)
                self.reminder_list.add_widget(ReminderCard(r, actual_idx, callbacks))

    def play_ringtone(self, ringtone_name, ringtone_uri=None):
        """Play selected ringtone with proper permissions"""
        try:
            if self.media_player:
                try:
                    self.media_player.stop()
                    self.media_player.release()
                except:
                    pass
                self.media_player = None
            
            if platform == 'android' and ringtone_name != 'Vibrate Only':
                from jnius import autoclass
                
                MediaPlayer = autoclass('android.media.MediaPlayer')
                AudioManager = autoclass('android.media.AudioManager')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                RingtoneManager = autoclass('android.media.RingtoneManager')
                
                activity = PythonActivity.mActivity
                
                self.media_player = MediaPlayer()
                self.media_player.setAudioStreamType(AudioManager.STREAM_ALARM)
                
                try:
                    if ringtone_uri and ringtone_uri not in ['SYSTEM_DEFAULT', 'VIBRATE_ONLY', 'BROWSE']:
                        # Try to use custom ringtone
                        uri = Uri.parse(ringtone_uri)
                        self.media_player.setDataSource(activity, uri)
                        print(f"Playing custom ringtone: {ringtone_uri}")
                    else:
                        # Use default alarm sound
                        default_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                        self.media_player.setDataSource(activity, default_uri)
                        print("Playing default system alarm")
                    
                    self.media_player.setLooping(True)
                    self.media_player.prepare()
                    self.media_player.start()
                    print("Ringtone started playing")
                    
                except Exception as e:
                    print(f"Error with custom ringtone, falling back to default: {e}")
                    # Fallback to default
                    self.media_player = MediaPlayer()
                    self.media_player.setAudioStreamType(AudioManager.STREAM_ALARM)
                    default_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                    self.media_player.setDataSource(activity, default_uri)
                    self.media_player.setLooping(True)
                    self.media_player.prepare()
                    self.media_player.start()
                
        except Exception as e:
            print(f"Ringtone error: {e}")
            import traceback
            traceback.print_exc()

    def stop_ringtone(self):
        """Stop playing ringtone"""
        try:
            if self.media_player:
                self.media_player.stop()
                self.media_player.release()
                self.media_player = None
                print("Ringtone stopped")
        except Exception as e:
            print(f"Stop ringtone error: {e}")

    def show_android_notification(self, reminder):
        """Show Android notification"""
        if platform == 'android':
            try:
                from jnius import autoclass
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')
                NotificationManager = autoclass('android.app.NotificationManager')
                NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
                PendingIntent = autoclass('android.app.PendingIntent')
                Intent = autoclass('android.content.Intent')
                RingtoneManager = autoclass('android.media.RingtoneManager')
                Uri = autoclass('android.net.Uri')
                
                activity = PythonActivity.mActivity
                notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
                
                intent = Intent(activity.getApplicationContext(), PythonActivity)
                intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP)
                pending_intent = PendingIntent.getActivity(activity, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE)
                
                builder = NotificationCompat.Builder(activity, "reminder_channel")
                builder.setContentTitle(f"⏰ {reminder.get('category', 'Reminder')}")
                builder.setContentText(reminder['text'])
                builder.setSmallIcon(activity.getApplicationInfo().icon)
                builder.setContentIntent(pending_intent)
                builder.setPriority(NotificationCompat.PRIORITY_MAX)
                builder.setCategory(NotificationCompat.CATEGORY_ALARM)
                builder.setAutoCancel(True)
                builder.setVibrate([0, 500, 200, 500])
                
                if reminder.get('ringtone') != 'Vibrate Only':
                    ringtone_uri = reminder.get('ringtone_uri')
                    if ringtone_uri and ringtone_uri not in ['SYSTEM_DEFAULT', 'VIBRATE_ONLY', 'BROWSE']:
                        sound_uri = Uri.parse(ringtone_uri)
                    else:
                        sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                    builder.setSound(sound_uri)
                
                notification = builder.build()
                notification_service.notify(1001, notification)
                print("Notification sent!")
                
            except Exception as e:
                print(f"Notification error: {e}")
                import traceback
                traceback.print_exc()

    def check_reminders(self, dt):
        """Check reminders with improved accuracy"""
        try:
            now = datetime.datetime.now()
            current_minute = now.hour * 60 + now.minute
            
            if current_minute == self.last_check_minute:
                return
            
            self.last_check_minute = current_minute
            current_time = now.time().replace(second=0, microsecond=0)
            current_day = now.weekday()
            
            for idx, r in enumerate(self.reminders):
                if not r.get('enabled'):
                    continue
                
                reminder_key = f"{idx}_{r['time'].hour:02d}{r['time'].minute:02d}"
                
                if r.get('snooze_until'):
                    if now >= r['snooze_until']:
                        print(f"Snooze ended for reminder {idx}")
                        r['snooze_until'] = None
                        r['played'] = False
                        self.triggered_reminders.discard(reminder_key)
                    else:
                        continue
                
                if current_day not in r.get('days', list(range(7))):
                    continue
                
                reminder_time = r['time'].replace(second=0, microsecond=0)
                if reminder_time == current_time and not r['played'] and reminder_key not in self.triggered_reminders:
                    print(f"Triggering reminder {idx}: {r['text']}")
                    self.show_alarm(r, idx)
                    r['played'] = True
                    self.triggered_reminders.add(reminder_key)
            
            if current_time.hour == 0 and current_time.minute == 0:
                print("Midnight reset")
                for r in self.reminders:
                    if not r.get('snooze_until'):
                        r['played'] = False
                self.triggered_reminders.clear()
                
        except Exception as e:
            print(f"Check reminders error: {e}")
            import traceback
            traceback.print_exc()

    def snooze_alarm(self, reminder, idx):
        """Snooze the alarm"""
        reminder['snooze_until'] = datetime.datetime.now() + datetime.timedelta(minutes=self.snooze_minutes)
        reminder['played'] = True
        
        reminder_key = f"{idx}_{reminder['time'].hour:02d}{reminder['time'].minute:02d}"
        self.triggered_reminders.discard(reminder_key)
        
        if self.alarm_popup:
            self.alarm_popup.dismiss()
        
        self.stop_ringtone()
        print(f"Snoozed for {self.snooze_minutes} minutes")

    def show_alarm(self, reminder, idx):
        """Show alarm popup with enhanced design"""
        try:
            self.show_android_notification(reminder)
            self.play_ringtone(reminder.get('ringtone', 'Default System Sound'), 
                             reminder.get('ringtone_uri'))
            
            if platform == 'android':
                try:
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    Context = autoclass('android.content.Context')
                    Vibrator = autoclass('android.os.Vibrator')
                    VibrationEffect = autoclass('android.os.VibrationEffect')
                    VERSION = autoclass('android.os.Build$VERSION')
                    
                    activity = PythonActivity.mActivity
                    vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                    
                    if VERSION.SDK_INT >= 26:
                        pattern = [0, 500, 200, 500, 200, 500]
                        effect = VibrationEffect.createWaveform(pattern, 0)
                        vibrator.vibrate(effect)
                    else:
                        vibrator.vibrate([0, 500, 200, 500, 200, 500], 0)
                    print("Vibration triggered")
                except Exception as e:
                    print(f"Vibration error: {e}")
            
            content = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(20))
            
            content.add_widget(Label(
                text="⏰",
                font_size='80sp',
                size_hint=(1, 0.2),
                color=(0.95, 0.35, 0.4, 1)
            ))
            
            content.add_widget(Label(
                text="REMINDER!",
                font_size='30sp',
                bold=True,
                color=(0.95, 0.35, 0.4, 1),
                size_hint=(1, 0.1)
            ))
            
            category = reminder.get('category', 'Personal')
            cat_label = Label(
                text=f"📂 {category}",
                font_size='14sp',
                size_hint=(1, 0.06),
                color=(0.4, 0.5, 0.65, 1),
                bold=True
            )
            content.add_widget(cat_label)
            
            reminder_label = Label(
                text=reminder['text'],
                font_size='19sp',
                size_hint=(1, 0.14),
                color=(0.2, 0.25, 0.35, 1),
                bold=True
            )
            content.add_widget(reminder_label)
            
            if reminder.get('note'):
                note_label = Label(
                    text=f"📝 {reminder['note']}",
                    font_size='14sp',
                    size_hint=(1, 0.1),
                    color=(0.5, 0.55, 0.65, 1),
                    italic=True
                )
                content.add_widget(note_label)
            
            content.add_widget(Label(
                text=datetime.datetime.now().strftime('%I:%M %p'),
                font_size='17sp',
                size_hint=(1, 0.06),
                color=(0.5, 0.55, 0.65, 1)
            ))
            
            snooze_box = BoxLayout(orientation='vertical', size_hint=(1, 0.18), spacing=dp(6))
            snooze_label = Label(
                text=f"😴 Snooze for {self.snooze_minutes} minutes",
                font_size='15sp',
                bold=True,
                size_hint=(1, 0.4),
                color=(0.3, 0.4, 0.6, 1)
            )
            
            slider = Slider(
                min=5,
                max=30,
                value=self.snooze_minutes,
                step=5,
                size_hint=(1, 0.6)
            )
            
            def update_snooze(instance, value):
                self.snooze_minutes = int(value)
                snooze_label.text = f"😴 Snooze for {self.snooze_minutes} minutes"
            
            slider.bind(value=update_snooze)
            
            snooze_box.add_widget(snooze_label)
            snooze_box.add_widget(slider)
            content.add_widget(snooze_box)
            
            btn_box = BoxLayout(size_hint=(1, 0.16), spacing=dp(12))
            
            snooze_btn = Button(
                text="😴 Snooze",
                background_normal='',
                background_color=(0.95, 0.65, 0.25, 1),
                color=(1, 1, 1, 1),
                font_size='17sp',
                bold=True
            )
            
            dismiss_btn = Button(
                text="✓ Dismiss",
                background_normal='',
                background_color=(0.2, 0.75, 0.5, 1),
                color=(1, 1, 1, 1),
                font_size='17sp',
                bold=True
            )
            
            btn_box.add_widget(snooze_btn)
            btn_box.add_widget(dismiss_btn)
            content.add_widget(btn_box)
            
            self.alarm_popup = Popup(
                content=content,
                size_hint=(0.95, 0.8),
                auto_dismiss=False,
                title="",
                separator_height=0,
                background_color=(1, 1, 1, 0.98)
            )
            
            def on_dismiss(instance):
                self.stop_ringtone()
                if platform == 'android':
                    try:
                        from jnius import autoclass
                        PythonActivity = autoclass('org.kivy.android.PythonActivity')
                        Context = autoclass('android.content.Context')
                        Vibrator = autoclass('android.os.Vibrator')
                        
                        activity = PythonActivity.mActivity
                        vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                        vibrator.cancel()
                    except:
                        pass
            
            snooze_btn.bind(on_press=lambda x: self.snooze_alarm(reminder, idx))
            dismiss_btn.bind(on_press=lambda x: self.alarm_popup.dismiss())
            self.alarm_popup.bind(on_dismiss=on_dismiss)
            self.alarm_popup.open()
            
        except Exception as e:
            print(f"Show alarm error: {e}")
            import traceback
            traceback.print_exc()

    def on_pause(self):
        """Handle app going to background"""
        print("App pausing - service should continue running")
        return True

    def on_resume(self):
        """Handle app coming back to foreground"""
        print("App resuming")
        self.refresh_reminder_list()
        self.last_check_minute = -1

    def on_stop(self):
        """Handle app stopping"""
        print("App stopping...")
        self.save_reminders()
        self.stop_ringtone()
        # Service should continue running in background


if __name__ == "__main__":
    print("Starting Enhanced ReminderApp...")
    try:
        ReminderApp().run()
    except Exception as e:
        print(f"App crash: {e}")
        import traceback
        traceback.print_exc()
