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
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window

print("App starting...")

Window.clearcolor = (0.93, 0.94, 0.96, 1)

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
            
            activity = PythonActivity.mActivity
            notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            
            channel_id = "reminder_channel"
            channel_name = "Reminder Notifications"
            importance = NotificationManager.IMPORTANCE_HIGH
            
            channel = NotificationChannel(channel_id, channel_name, importance)
            channel.setDescription("Notifications for reminders")
            channel.enableVibration(True)
            channel.setVibrationPattern([0, 500, 200, 500])
            
            notification_service.createNotificationChannel(channel)
            print("Notification channel created")
        except Exception as e:
            print(f"Channel creation error: {e}")


def start_background_service():
    """Start the background service for reminders"""
    if platform == 'android':
        try:
            from jnius import autoclass
            PythonService = autoclass('org.kivy.android.PythonService')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            
            activity = PythonActivity.mActivity
            service = PythonService.mService
            
            if service is None:
                service_intent = Intent(activity, PythonService)
                service_intent.putExtra("serviceTitle", "My Reminders")
                service_intent.putExtra("serviceDescription", "Reminder service is running")
                
                activity.startService(service_intent)
                print("Background service started")
            else:
                print("Service already running")
        except Exception as e:
            print(f"Service start error: {e}")


class ModernCard(BoxLayout):
    """Base class for modern card-style widgets"""
    def __init__(self, bg_color=(1, 1, 1, 1), border_color=(0.85, 0.87, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        
        with self.canvas.before:
            Color(0.7, 0.7, 0.7, 0.2)
            self.shadow = RoundedRectangle(radius=[dp(16)])
            
            Color(*border_color)
            self.border = RoundedRectangle(radius=[dp(15)])
            
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(radius=[dp(15)])
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.shadow.pos = (self.pos[0] + dp(2), self.pos[1] - dp(4))
        self.shadow.size = self.size
        
        self.border.pos = self.pos
        self.border.size = self.size
        
        self.bg_rect.pos = (self.pos[0] + dp(1), self.pos[1] + dp(1))
        self.bg_rect.size = (self.size[0] - dp(2), self.size[1] - dp(2))


class ReminderCard(ModernCard):
    def __init__(self, reminder, index, callbacks, **kwargs):
        if not reminder.get('enabled', True):
            bg_color = (0.94, 0.94, 0.96, 1)
            border_color = (0.82, 0.82, 0.85, 1)
        else:
            bg_color = (1, 1, 1, 1)
            border_color = (0.85, 0.9, 0.95, 1)
        
        super().__init__(bg_color=bg_color, border_color=border_color, **kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(140)
        self.padding = dp(16)
        self.spacing = dp(12)
        
        # Top row - Time
        top_row = BoxLayout(size_hint_y=0.3, spacing=dp(12))
        
        time_box = BoxLayout(size_hint_x=0.65, spacing=dp(8))
        time_icon = Label(
            text="[clock]",
            markup=False,
            font_size='32sp',
            size_hint_x=0.15
        )
        time_text = Label(
            text=reminder['time'].strftime('%I:%M %p'),
            halign='left',
            font_size='26sp',
            bold=True,
            color=(0.15, 0.25, 0.45, 1) if reminder.get('enabled') else (0.6, 0.6, 0.6, 1),
            size_hint_x=0.85
        )
        time_text.bind(size=time_text.setter('text_size'))
        time_box.add_widget(time_icon)
        time_box.add_widget(time_text)
        
        # Status indicator
        status_box = BoxLayout(size_hint_x=0.35, orientation='horizontal', spacing=dp(4))
        status_icon = Label(
            text="[check]" if reminder.get('enabled') else "[circle]",
            markup=False,
            font_size='18sp',
            color=(0.2, 0.7, 0.4, 1) if reminder.get('enabled') else (0.6, 0.6, 0.6, 1),
            size_hint_x=0.3
        )
        status_label = Label(
            text="Active" if reminder.get('enabled') else "Off",
            font_size='14sp',
            bold=True,
            color=(0.2, 0.7, 0.4, 1) if reminder.get('enabled') else (0.6, 0.6, 0.6, 1),
            size_hint_x=0.7,
            halign='left'
        )
        status_label.bind(size=status_label.setter('text_size'))
        status_box.add_widget(status_icon)
        status_box.add_widget(status_label)
        
        top_row.add_widget(time_box)
        top_row.add_widget(status_box)
        
        # Reminder text
        text_label = Label(
            text=reminder['text'],
            halign='left',
            valign='top',
            font_size='17sp',
            color=(0.25, 0.25, 0.3, 1) if reminder.get('enabled') else (0.65, 0.65, 0.65, 1),
            size_hint_y=0.28,
            text_size=(None, None)
        )
        text_label.bind(size=lambda *x: setattr(text_label, 'text_size', (text_label.width, None)))
        
        # Days display
        days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        selected_days = reminder.get('days', list(range(7)))
        if len(selected_days) == 7:
            days_text = "Every day"
        elif len(selected_days) == 5 and selected_days == [0, 1, 2, 3, 4]:
            days_text = "Weekdays"
        elif len(selected_days) == 2 and selected_days == [5, 6]:
            days_text = "Weekends"
        else:
            days_text = ", ".join([days_map[d] for d in sorted(selected_days)])
        
        days_label = Label(
            text=f"[calendar] {days_text}",
            markup=False,
            halign='left',
            font_size='14sp',
            color=(0.4, 0.5, 0.6, 1),
            size_hint_y=0.18
        )
        days_label.bind(size=days_label.setter('text_size'))
        
        # Action buttons
        btn_row = BoxLayout(size_hint_y=0.24, spacing=dp(10))
        
        toggle_color = (0.2, 0.7, 0.4, 1) if reminder.get('enabled') else (0.5, 0.5, 0.55, 1)
        toggle_btn = Button(
            text="ON" if reminder.get('enabled') else "OFF",
            background_normal='',
            background_color=toggle_color,
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_x=0.35
        )
        toggle_btn.bind(on_press=lambda x: callbacks['toggle'](index))
        
        edit_btn = Button(
            text="Edit",
            background_normal='',
            background_color=(0.3, 0.55, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_x=0.35
        )
        edit_btn.bind(on_press=lambda x: callbacks['edit'](index))
        
        del_btn = Button(
            text="Delete",
            background_normal='',
            background_color=(0.95, 0.35, 0.35, 1),
            color=(1, 1, 1, 1),
            font_size='14sp',
            bold=True,
            size_hint_x=0.3
        )
        del_btn.bind(on_press=lambda x: callbacks['delete'](index))
        
        btn_row.add_widget(toggle_btn)
        btn_row.add_widget(edit_btn)
        btn_row.add_widget(del_btn)
        
        self.add_widget(top_row)
        self.add_widget(text_label)
        self.add_widget(days_label)
        self.add_widget(btn_row)


class ReminderApp(App):
    def build(self):
        print("Building UI...")
        self.reminders = []
        self.editing_index = None
        self.alarm_popup = None
        self.media_player = None
        self.snooze_minutes = 10
        self.triggered_reminders = set()
        self.last_check_minute = -1
        
        # Setup data directory
        try:
            if platform == 'android':
                self.data_dir = self.user_data_dir
                print(f"Android data dir: {self.data_dir}")
            else:
                self.data_dir = os.path.dirname(os.path.abspath(__file__))
                print(f"Desktop data dir: {self.data_dir}")
            
            self.data_file = os.path.join(self.data_dir, 'reminders.json')
            print(f"Data file: {self.data_file}")
        except Exception as e:
            print(f"Data dir error: {e}")
            self.data_file = 'reminders.json'
        
        create_notification_channel()
        start_background_service()
        
        self.load_ringtones()
        self.load_reminders()
        print(f"Loaded {len(self.reminders)} reminders")

        # Main layout
        root = FloatLayout()
        self.layout = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(16))

        # Header
        header = ModernCard(bg_color=(0.25, 0.5, 0.85, 1), border_color=(0.2, 0.45, 0.8, 1))
        header.orientation = 'vertical'
        header.size_hint = (1, None)
        header.height = dp(110)
        header.padding = dp(18)
        header.spacing = dp(8)
        
        title_row = BoxLayout(size_hint_y=0.45)
        title = Label(
            text="[alarm] My Reminders",
            markup=False,
            font_size='28sp',
            bold=True,
            halign='left',
            color=(1, 1, 1, 1)
        )
        title.bind(size=title.setter('text_size'))
        title_row.add_widget(title)
        
        time_row = BoxLayout(size_hint_y=0.55)
        self.time_label = Label(
            text="",
            font_size='22sp',
            halign='left',
            bold=True,
            color=(1, 1, 1, 0.95)
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        
        self.date_label = Label(
            text="",
            font_size='15sp',
            halign='right',
            color=(1, 1, 1, 0.85)
        )
        self.date_label.bind(size=self.date_label.setter('text_size'))
        
        time_row.add_widget(self.time_label)
        time_row.add_widget(self.date_label)
        
        header.add_widget(title_row)
        header.add_widget(time_row)
        self.layout.add_widget(header)
        
        Clock.schedule_interval(self.update_time, 1)

        # Add button
        add_btn = Button(
            text="+ Add New Reminder",
            size_hint=(1, None),
            height=dp(60),
            background_normal='',
            background_color=(0.2, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        add_btn.bind(on_press=self.show_add_dialog)
        self.layout.add_widget(add_btn)

        # Stats card
        stats_card = ModernCard(bg_color=(0.95, 0.97, 1, 1), border_color=(0.8, 0.85, 0.95, 1))
        stats_card.size_hint = (1, None)
        stats_card.height = dp(65)
        stats_card.padding = dp(18)
        
        self.stats_label = Label(
            text="",
            size_hint=(1, 1),
            halign='left',
            valign='middle',
            font_size='16sp',
            bold=True,
            color=(0.25, 0.35, 0.5, 1)
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        stats_card.add_widget(self.stats_label)
        self.layout.add_widget(stats_card)

        # Reminder list
        scroll = ScrollView(size_hint=(1, 1))
        self.reminder_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(14),
            padding=[0, dp(8), 0, dp(12)]
        )
        self.reminder_list.bind(minimum_height=self.reminder_list.setter('height'))
        scroll.add_widget(self.reminder_list)
        self.layout.add_widget(scroll)

        root.add_widget(self.layout)
        
        self.refresh_reminder_list()
        Clock.schedule_interval(self.check_reminders, 10)
        
        print("UI built successfully")
        return root

    def load_ringtones(self):
        """Load ringtone options"""
        self.ringtones = {
            'Default System Sound': 'SYSTEM_DEFAULT',
            'Vibrate Only': 'VIBRATE_ONLY'
        }
        
        # Add option to browse files
        if platform == 'android':
            self.ringtones['Browse for Sound File'] = 'BROWSE'
        
        print(f"Ringtone options: {len(self.ringtones)}")

    def browse_ringtone(self, callback):
        """Open file picker for ringtone selection"""
        if platform == 'android':
            try:
                from jnius import autoclass, cast
                from android import activity
                
                Intent = autoclass('android.content.Intent')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                def on_activity_result(request_code, result_code, intent):
                    if request_code == 1001 and result_code == -1 and intent:
                        uri = intent.getData()
                        if uri:
                            uri_string = uri.toString()
                            print(f"Selected ringtone: {uri_string}")
                            callback(uri_string)
                
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
        self.date_label.text = now.strftime('%A, %B %d')

    def load_reminders(self):
        try:
            if os.path.exists(self.data_file):
                print(f"Loading from {self.data_file}")
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
                            'ringtone_uri': item.get('ringtone_uri', None)
                        })
                print(f"Loaded {len(self.reminders)} reminders")
            else:
                print("No reminders file found")
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
                'ringtone_uri': r.get('ringtone_uri', None)
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
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(18))
        
        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation='vertical', spacing=dp(14), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        
        title_lbl = Label(
            text="Edit Reminder" if reminder else "New Reminder",
            font_size='24sp',
            bold=True,
            size_hint=(1, None),
            height=dp(45),
            color=(0.2, 0.3, 0.5, 1)
        )
        form.add_widget(title_lbl)
        
        # Text input
        text_label = Label(
            text="Reminder Message",
            font_size='16sp',
            bold=True,
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        text_label.bind(size=text_label.setter('text_size'))
        form.add_widget(text_label)
        
        text_input = TextInput(
            hint_text="What do you want to be reminded about?",
            size_hint=(1, None),
            height=dp(55),
            multiline=False,
            background_color=(0.96, 0.97, 0.99, 1),
            foreground_color=(0.2, 0.2, 0.3, 1),
            padding=[dp(15), dp(18)],
            font_size='16sp'
        )
        if reminder:
            text_input.text = reminder['text']
        form.add_widget(text_input)

        # Time selection
        time_label = Label(
            text="Set Time",
            font_size='16sp',
            bold=True,
            size_hint=(1, None),
            height=dp(35),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        time_label.bind(size=time_label.setter('text_size'))
        form.add_widget(time_label)
        
        time_box = BoxLayout(size_hint=(1, None), height=dp(55), spacing=dp(8))
        
        hour = Spinner(
            text=str(reminder['time'].hour % 12 or 12) if reminder else "9",
            values=[str(i) for i in range(1, 13)],
            size_hint=(0.3, 1),
            background_color=(0.96, 0.97, 0.99, 1),
            font_size='18sp'
        )
        
        colon_label = Label(text=":", size_hint=(0.08, 1), font_size='24sp', bold=True)
        
        minute = Spinner(
            text=str(reminder['time'].minute).zfill(2) if reminder else "00",
            values=[str(i).zfill(2) for i in range(0, 60)],
            size_hint=(0.3, 1),
            background_color=(0.96, 0.97, 0.99, 1),
            font_size='18sp'
        )
        
        ampm = Spinner(
            text="PM" if reminder and reminder['time'].hour >= 12 else "AM",
            values=["AM", "PM"],
            size_hint=(0.32, 1),
            background_color=(0.96, 0.97, 0.99, 1),
            font_size='18sp'
        )
        
        time_box.add_widget(hour)
        time_box.add_widget(colon_label)
        time_box.add_widget(minute)
        time_box.add_widget(ampm)
        form.add_widget(time_box)

        # Ringtone selection
        ringtone_label = Label(
            text="Ringtone",
            font_size='16sp',
            bold=True,
            size_hint=(1, None),
            height=dp(35),
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
            height=dp(50),
            background_color=(0.96, 0.97, 0.99, 1),
            font_size='15sp'
        )
        
        def on_ringtone_select(spinner, text):
            if text == 'Browse for Sound File':
                def on_file_selected(uri):
                    selected_ringtone_uri['uri'] = uri
                    spinner.text = 'Custom Sound'
                self.browse_ringtone(on_file_selected)
        
        ringtone_spinner.bind(text=on_ringtone_select)
        form.add_widget(ringtone_spinner)

        # Days selection
        days_label = Label(
            text="Repeat on Days",
            font_size='16sp',
            bold=True,
            size_hint=(1, None),
            height=dp(35),
            halign='left',
            color=(0.3, 0.4, 0.6, 1)
        )
        days_label.bind(size=days_label.setter('text_size'))
        form.add_widget(days_label)
        
        days_box = BoxLayout(size_hint=(1, None), height=dp(70), spacing=dp(4))
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_checks = []
        
        for i, day in enumerate(day_names):
            cb_box = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(4))
            cb = CheckBox(
                active=reminder and i in reminder.get('days', list(range(7))) if reminder else True,
                size_hint=(1, 0.55),
                color=(0.3, 0.6, 0.9, 1)
            )
            day_lbl = Label(
                text=day,
                size_hint=(1, 0.45),
                font_size='13sp',
                bold=True,
                color=(0.3, 0.4, 0.6, 1)
            )
            cb_box.add_widget(cb)
            cb_box.add_widget(day_lbl)
            day_checks.append(cb)
            days_box.add_widget(cb_box)
        form.add_widget(days_box)

        # Quick select buttons
        quick_box = BoxLayout(size_hint=(1, None), height=dp(45), spacing=dp(8))
        
        def select_weekdays():
            for i, cb in enumerate(day_checks):
                cb.active = i < 5
        
        def select_weekend():
            for i, cb in enumerate(day_checks):
                cb.active = i >= 5
        
        def select_all():
            for cb in day_checks:
                cb.active = True
        
        weekday_btn = Button(
            text="Weekdays",
            size_hint=(0.33, 1),
            background_normal='',
            background_color=(0.4, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True
        )
        weekday_btn.bind(on_press=lambda x: select_weekdays())
        
        weekend_btn = Button(
            text="Weekend",
            size_hint=(0.33, 1),
            background_normal='',
            background_color=(0.85, 0.5, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True
        )
        weekend_btn.bind(on_press=lambda x: select_weekend())
        
        all_btn = Button(
            text="Every Day",
            size_hint=(0.34, 1),
            background_normal='',
            background_color=(0.6, 0.4, 0.85, 1),
            color=(1, 1, 1, 1),
            font_size='13sp',
            bold=True
        )
        all_btn.bind(on_press=lambda x: select_all())
        
        quick_box.add_widget(weekday_btn)
        quick_box.add_widget(weekend_btn)
        quick_box.add_widget(all_btn)
        form.add_widget(quick_box)

        scroll.add_widget(form)
        content.add_widget(scroll)

        # Action buttons
        btn_box = BoxLayout(size_hint=(1, None), height=dp(55), spacing=dp(12))
        
        cancel_btn = Button(
            text="Cancel",
            background_normal='',
            background_color=(0.65, 0.65, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        
        save_btn = Button(
            text="Save",
            background_normal='',
            background_color=(0.2, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        
        btn_box.add_widget(cancel_btn)
        btn_box.add_widget(save_btn)
        content.add_widget(btn_box)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.96, 0.92),
            separator_height=0,
            background_color=(1, 1, 1, 0.98)
        )

        def save_reminder(instance):
            text = text_input.text.strip()
            if not text:
                text_input.hint_text = "Please enter reminder text"
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
                days_label.text = "Select at least one day"
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
                'ringtone_uri': selected_ringtone_uri['uri']
            }

            if self.editing_index is not None:
                self.reminders[self.editing_index] = new_reminder
                self.editing_index = None
            else:
                self.reminders.append(new_reminder)
            
            self.reminders.sort(key=lambda x: (x['time'].hour, x['time'].minute))
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
            self.reminders[index]['played'] = False
            
            reminder = self.reminders[index]
            reminder_key = f"{index}_{reminder['time'].hour:02d}{reminder['time'].minute:02d}"
            self.triggered_reminders.discard(reminder_key)
            
            self.save_reminders()
            self.refresh_reminder_list()
            print(f"Toggled reminder {index} to {'ON' if self.reminders[index]['enabled'] else 'OFF'}")

    def delete_reminder(self, index):
        if 0 <= index < len(self.reminders):
            content = BoxLayout(orientation='vertical', spacing=dp(24), padding=dp(24))
            
            icon_label = Label(
                text="[trash]",
                markup=False,
                font_size='56sp',
                size_hint=(1, 0.3)
            )
            content.add_widget(icon_label)
            
            content.add_widget(Label(
                text="Delete this reminder?",
                font_size='20sp',
                bold=True,
                size_hint=(1, 0.2),
                color=(0.3, 0.3, 0.4, 1)
            ))
            content.add_widget(Label(
                text=self.reminders[index]['text'],
                font_size='16sp',
                color=(0.5, 0.5, 0.5, 1),
                size_hint=(1, 0.2)
            ))
            
            btn_box = BoxLayout(size_hint=(1, 0.3), spacing=dp(12))
            
            cancel_btn = Button(
                text="Cancel",
                background_normal='',
                background_color=(0.65, 0.65, 0.7, 1),
                color=(1, 1, 1, 1),
                font_size='16sp',
                bold=True
            )
            
            delete_btn = Button(
                text="Delete",
                background_normal='',
                background_color=(0.95, 0.35, 0.35, 1),
                color=(1, 1, 1, 1),
                font_size='16sp',
                bold=True
            )
            
            btn_box.add_widget(cancel_btn)
            btn_box.add_widget(delete_btn)
            content.add_widget(btn_box)
            
            confirm_popup = Popup(
                content=content,
                size_hint=(0.85, 0.5),
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
                confirm_popup.dismiss()
            
            cancel_btn.bind(on_press=confirm_popup.dismiss)
            delete_btn.bind(on_press=do_delete)
            confirm_popup.open()

    def refresh_reminder_list(self):
        self.reminder_list.clear_widgets()
        
        active = sum(1 for r in self.reminders if r.get('enabled', True))
        total = len(self.reminders)
        
        self.stats_label.text = f"Total: {total}  |  Active: {active}  |  Inactive: {total - active}"
        
        if not self.reminders:
            empty_card = ModernCard(bg_color=(0.96, 0.97, 1, 1), border_color=(0.85, 0.88, 0.95, 1))
            empty_card.size_hint_y = None
            empty_card.height = dp(170)
            empty_card.padding = dp(24)
            
            empty_box = BoxLayout(orientation='vertical', spacing=dp(14))
            empty_box.add_widget(Label(
                text="[inbox]",
                markup=False,
                font_size='54sp',
                size_hint_y=0.45
            ))
            empty_box.add_widget(Label(
                text="No Reminders Yet",
                font_size='20sp',
                bold=True,
                size_hint_y=0.25,
                color=(0.3, 0.4, 0.6, 1)
            ))
            empty_box.add_widget(Label(
                text="Tap the green button to create one!",
                font_size='15sp',
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
        
        for idx, r in enumerate(self.reminders):
            self.reminder_list.add_widget(ReminderCard(r, idx, callbacks))

    def play_ringtone(self, ringtone_name, ringtone_uri=None):
        """Play selected ringtone"""
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
                
                if ringtone_uri and ringtone_uri != 'SYSTEM_DEFAULT':
                    # Play custom user-selected ringtone
                    uri = Uri.parse(ringtone_uri)
                    self.media_player.setDataSource(activity, uri)
                else:
                    # Play default system alarm
                    default_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                    self.media_player.setDataSource(activity, default_uri)
                
                self.media_player.setLooping(True)
                self.media_player.prepare()
                self.media_player.start()
                print(f"Playing ringtone: {ringtone_name}")
                
        except Exception as e:
            print(f"Ringtone playback error: {e}")
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
            print(f"Error stopping ringtone: {e}")

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
                
                activity = PythonActivity.mActivity
                notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
                
                intent = Intent(activity.getApplicationContext(), PythonActivity)
                intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP)
                pending_intent = PendingIntent.getActivity(activity, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE)
                
                builder = NotificationCompat.Builder(activity, "reminder_channel")
                builder.setContentTitle("Reminder!")
                builder.setContentText(reminder['text'])
                builder.setSmallIcon(activity.getApplicationInfo().icon)
                builder.setContentIntent(pending_intent)
                builder.setPriority(NotificationCompat.PRIORITY_MAX)
                builder.setCategory(NotificationCompat.CATEGORY_ALARM)
                builder.setAutoCancel(True)
                builder.setVibrate([0, 500, 200, 500])
                
                if reminder.get('ringtone') != 'Vibrate Only':
                    default_sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                    builder.setSound(default_sound)
                
                notification = builder.build()
                notification_service.notify(1001, notification)
                print("Notification sent!")
                
            except Exception as e:
                print(f"Notification error: {e}")

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
            
            print(f"Checking reminders at {current_time}, day {current_day}")
            
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
        """Show alarm popup"""
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
                        pattern = [0, 500, 200, 500, 200, 500]
                        vibrator.vibrate(pattern, 0)
                    
                    print("Vibration triggered")
                except Exception as e:
                    print(f"Vibration error: {e}")
            
            content = BoxLayout(orientation='vertical', spacing=dp(18), padding=dp(22))
            
            content.add_widget(Label(
                text="[alarm]",
                markup=False,
                font_size='72sp',
                size_hint=(1, 0.18)
            ))
            
            content.add_widget(Label(
                text="REMINDER!",
                font_size='32sp',
                bold=True,
                color=(0.95, 0.3, 0.35, 1),
                size_hint=(1, 0.12)
            ))
            
            reminder_label = Label(
                text=reminder['text'],
                font_size='20sp',
                size_hint=(1, 0.18),
                color=(0.2, 0.25, 0.35, 1),
                bold=True
            )
            content.add_widget(reminder_label)
            
            content.add_widget(Label(
                text=datetime.datetime.now().strftime('%I:%M %p'),
                font_size='18sp',
                size_hint=(1, 0.08),
                color=(0.5, 0.55, 0.65, 1)
            ))
            
            snooze_box = BoxLayout(orientation='vertical', size_hint=(1, 0.22), spacing=dp(8))
            snooze_label = Label(
                text=f"Snooze for {self.snooze_minutes} minutes",
                font_size='16sp',
                bold=True,
                size_hint=(1, 0.35),
                color=(0.3, 0.4, 0.6, 1)
            )
            
            slider = Slider(
                min=5,
                max=30,
                value=self.snooze_minutes,
                step=5,
                size_hint=(1, 0.65)
            )
            
            def update_snooze(instance, value):
                self.snooze_minutes = int(value)
                snooze_label.text = f"Snooze for {self.snooze_minutes} minutes"
            
            slider.bind(value=update_snooze)
            
            snooze_box.add_widget(snooze_label)
            snooze_box.add_widget(slider)
            content.add_widget(snooze_box)
            
            btn_box = BoxLayout(size_hint=(1, 0.14), spacing=dp(14))
            
            snooze_btn = Button(
                text="Snooze",
                background_normal='',
                background_color=(0.95, 0.65, 0.25, 1),
                color=(1, 1, 1, 1),
                font_size='18sp',
                bold=True
            )
            
            dismiss_btn = Button(
                text="Dismiss",
                background_normal='',
                background_color=(0.2, 0.7, 0.4, 1),
                color=(1, 1, 1, 1),
                font_size='18sp',
                bold=True
            )
            
            btn_box.add_widget(snooze_btn)
            btn_box.add_widget(dismiss_btn)
            content.add_widget(btn_box)
            
            self.alarm_popup = Popup(
                content=content,
                size_hint=(0.96, 0.75),
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

    def on_pause(self):
        return True

    def on_resume(self):
        self.refresh_reminder_list()
        self.last_check_minute = -1

    def on_stop(self):
        print("App stopping...")
        self.save_reminders()
        self.stop_ringtone()


if __name__ == "__main__":
    print("Starting ReminderApp...")
    try:
        ReminderApp().run()
    except Exception as e:
        print(f"App crash: {e}")
        import traceback
        traceback.print_exc()
