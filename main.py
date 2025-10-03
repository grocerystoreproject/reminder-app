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
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.core.window import Window

print("App starting...")

# Set background color
Window.clearcolor = (0.95, 0.96, 0.98, 1)

# Request permissions on Android
if platform == 'android':
    print("Requesting Android permissions...")
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.VIBRATE, 
            Permission.WAKE_LOCK,
            Permission.SCHEDULE_EXACT_ALARM,
            Permission.POST_NOTIFICATIONS
        ])
        print("Permissions requested")
    except Exception as e:
        print(f"Permission error: {e}")


class ModernCard(BoxLayout):
    """Base class for modern card-style widgets"""
    def __init__(self, bg_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(radius=[dp(15)])
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class ReminderCard(ModernCard):
    def __init__(self, reminder, index, callbacks, **kwargs):
        # Determine card color based on status
        if not reminder.get('enabled', True):
            bg_color = (0.9, 0.9, 0.9, 1)  # Gray for disabled
        else:
            bg_color = (1, 1, 1, 1)  # White for enabled
        
        super().__init__(bg_color=bg_color, **kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(15)
        self.spacing = dp(10)
        
        # Top row - Time and toggle
        top_row = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        
        # Time with icon
        time_box = BoxLayout(size_hint_x=0.6)
        time_icon = Label(
            text="🕐",
            font_size='28sp',
            size_hint_x=0.2
        )
        time_text = Label(
            text=reminder['time'].strftime('%I:%M %p'),
            halign='left',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.3, 0.4, 1),
            size_hint_x=0.8
        )
        time_text.bind(size=time_text.setter('text_size'))
        time_box.add_widget(time_icon)
        time_box.add_widget(time_text)
        
        # Status indicator
        status_label = Label(
            text="✓ Active" if reminder.get('enabled') else "○ Off",
            font_size='14sp',
            color=(0.3, 0.7, 0.4, 1) if reminder.get('enabled') else (0.6, 0.6, 0.6, 1),
            size_hint_x=0.4,
            halign='right'
        )
        status_label.bind(size=status_label.setter('text_size'))
        
        top_row.add_widget(time_box)
        top_row.add_widget(status_label)
        
        # Middle row - Reminder text
        text_label = Label(
            text=reminder['text'],
            halign='left',
            valign='top',
            font_size='16sp',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.3,
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
            text=f"📅 {days_text}",
            halign='left',
            font_size='13sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.2
        )
        days_label.bind(size=days_label.setter('text_size'))
        
        # Bottom row - Action buttons
        btn_row = BoxLayout(size_hint_y=0.3, spacing=dp(8))
        
        toggle_btn = Button(
            text="Turn Off" if reminder.get('enabled') else "Turn On",
            background_normal='',
            background_color=(0.3, 0.7, 0.4, 1) if reminder.get('enabled') else (0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='13sp',
            size_hint_x=0.4
        )
        toggle_btn.bind(on_press=lambda x: callbacks['toggle'](index))
        
        edit_btn = Button(
            text="✎ Edit",
            background_normal='',
            background_color=(0.4, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='13sp',
            size_hint_x=0.3
        )
        edit_btn.bind(on_press=lambda x: callbacks['edit'](index))
        
        del_btn = Button(
            text="🗑",
            background_normal='',
            background_color=(0.9, 0.4, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
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
        self.snooze_minutes = 5
        self.triggered_reminders = set()  # Track triggered reminders to avoid duplicates
        
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
        
        self.load_reminders()
        print(f"Loaded {len(self.reminders)} reminders")

        # Main layout
        root = FloatLayout()
        self.layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(15))

        # Modern Header
        header = ModernCard(bg_color=(0.4, 0.6, 0.9, 1))
        header.orientation = 'vertical'
        header.size_hint = (1, None)
        header.height = dp(100)
        header.padding = dp(15)
        
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
        
        time_row = BoxLayout(size_hint_y=0.5)
        self.time_label = Label(
            text="",
            font_size='20sp',
            halign='left',
            color=(1, 1, 1, 0.9)
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        
        self.date_label = Label(
            text="",
            font_size='14sp',
            halign='right',
            color=(1, 1, 1, 0.8)
        )
        self.date_label.bind(size=self.date_label.setter('text_size'))
        
        time_row.add_widget(self.time_label)
        time_row.add_widget(self.date_label)
        
        header.add_widget(title_row)
        header.add_widget(time_row)
        self.layout.add_widget(header)
        
        Clock.schedule_interval(self.update_time, 1)

        # Add button with modern style
        add_btn = Button(
            text="+ Add New Reminder",
            size_hint=(1, None),
            height=dp(55),
            background_normal='',
            background_color=(0.3, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='16sp',
            bold=True
        )
        add_btn.bind(on_press=self.show_add_dialog)
        self.layout.add_widget(add_btn)

        # Stats card
        stats_card = ModernCard(bg_color=(0.98, 0.98, 1, 1))
        stats_card.size_hint = (1, None)
        stats_card.height = dp(60)
        stats_card.padding = dp(15)
        
        self.stats_label = Label(
            text="",
            size_hint=(1, 1),
            halign='left',
            valign='middle',
            font_size='15sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        stats_card.add_widget(self.stats_label)
        self.layout.add_widget(stats_card)

        # Reminder list with scroll
        scroll = ScrollView(size_hint=(1, 1))
        self.reminder_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
            padding=[0, dp(5), 0, dp(10)]
        )
        self.reminder_list.bind(minimum_height=self.reminder_list.setter('height'))
        scroll.add_widget(self.reminder_list)
        self.layout.add_widget(scroll)

        root.add_widget(self.layout)
        
        self.refresh_reminder_list()
        Clock.schedule_interval(self.check_reminders, 30)  # Check every 30 seconds
        
        print("UI built successfully")
        return root

    def update_time(self, dt):
        now = datetime.datetime.now()
        self.time_label.text = now.strftime('%I:%M %p')
        self.date_label.text = now.strftime('%A, %b %d')

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
                            'snooze_until': None
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
                'days': r.get('days', list(range(7)))
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
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))
        
        # Title label
        title_lbl = Label(
            text="Edit Reminder" if reminder else "New Reminder",
            font_size='20sp',
            bold=True,
            size_hint=(1, None),
            height=dp(40),
            color=(0.2, 0.3, 0.4, 1)
        )
        content.add_widget(title_lbl)
        
        # Text input with modern styling
        text_input = TextInput(
            hint_text="What do you want to be reminded about?",
            size_hint=(1, None),
            height=dp(50),
            multiline=False,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.2, 0.2, 0.2, 1),
            cursor_color=(0.4, 0.6, 0.9, 1),
            padding=[dp(10), dp(15)]
        )
        if reminder:
            text_input.text = reminder['text']
        content.add_widget(text_input)

        # Time selection section
        time_label = Label(
            text="⏰ Set Time",
            font_size='16sp',
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        time_label.bind(size=time_label.setter('text_size'))
        content.add_widget(time_label)
        
        time_box = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(5))
        
        hour = Spinner(
            text=str(reminder['time'].hour % 12 or 12) if reminder else "12",
            values=[str(i) for i in range(1, 13)],
            size_hint=(0.3, 1),
            background_color=(0.95, 0.95, 0.95, 1)
        )
        
        minute = Spinner(
            text=str(reminder['time'].minute).zfill(2) if reminder else "00",
            values=[str(i).zfill(2) for i in range(0, 60, 5)],
            size_hint=(0.3, 1),
            background_color=(0.95, 0.95, 0.95, 1)
        )
        
        ampm = Spinner(
            text="PM" if reminder and reminder['time'].hour >= 12 else "AM",
            values=["AM", "PM"],
            size_hint=(0.3, 1),
            background_color=(0.95, 0.95, 0.95, 1)
        )
        
        time_box.add_widget(hour)
        time_box.add_widget(Label(text=":", size_hint=(0.1, 1), font_size='20sp'))
        time_box.add_widget(minute)
        time_box.add_widget(ampm)
        content.add_widget(time_box)

        # Days selection
        days_label = Label(
            text="📅 Repeat on",
            font_size='16sp',
            size_hint=(1, None),
            height=dp(30),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        days_label.bind(size=days_label.setter('text_size'))
        content.add_widget(days_label)
        
        days_box = BoxLayout(size_hint=(1, None), height=dp(60), spacing=dp(3))
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_checks = []
        
        for i, day in enumerate(day_names):
            cb_box = BoxLayout(orientation='vertical', size_hint=(1, 1))
            cb = CheckBox(
                active=reminder and i in reminder.get('days', list(range(7))) if reminder else True,
                size_hint=(1, 0.6),
                color=(0.4, 0.6, 0.9, 1)
            )
            day_lbl = Label(
                text=day,
                size_hint=(1, 0.4),
                font_size='12sp',
                color=(0.3, 0.3, 0.3, 1)
            )
            cb_box.add_widget(cb)
            cb_box.add_widget(day_lbl)
            day_checks.append(cb)
            days_box.add_widget(cb_box)
        content.add_widget(days_box)

        # Quick select buttons
        quick_box = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(5))
        
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
            background_color=(0.85, 0.85, 0.85, 1),
            color=(0.3, 0.3, 0.3, 1),
            font_size='12sp'
        )
        weekday_btn.bind(on_press=lambda x: select_weekdays())
        
        weekend_btn = Button(
            text="Weekend",
            size_hint=(0.33, 1),
            background_normal='',
            background_color=(0.85, 0.85, 0.85, 1),
            color=(0.3, 0.3, 0.3, 1),
            font_size='12sp'
        )
        weekend_btn.bind(on_press=lambda x: select_weekend())
        
        all_btn = Button(
            text="Every day",
            size_hint=(0.34, 1),
            background_normal='',
            background_color=(0.85, 0.85, 0.85, 1),
            color=(0.3, 0.3, 0.3, 1),
            font_size='12sp'
        )
        all_btn.bind(on_press=lambda x: select_all())
        
        quick_box.add_widget(weekday_btn)
        quick_box.add_widget(weekend_btn)
        quick_box.add_widget(all_btn)
        content.add_widget(quick_box)

        # Buttons
        btn_box = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        
        cancel_btn = Button(
            text="Cancel",
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size='15sp'
        )
        
        save_btn = Button(
            text="💾 Save Reminder",
            background_normal='',
            background_color=(0.3, 0.7, 0.4, 1),
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
            size_hint=(0.95, 0.85),
            separator_height=0,
            background_color=(1, 1, 1, 0.95)
        )

        def save_reminder(instance):
            text = text_input.text.strip()
            if not text:
                text_input.hint_text = "⚠ Please enter reminder text"
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
                days_label.text = "⚠ Please select at least one day"
                days_label.color = (0.9, 0.3, 0.3, 1)
                return

            new_reminder = {
                'text': text,
                'time': datetime.time(h, m),
                'played': False,
                'recurring': len(selected_days) > 1 or len(selected_days) < 7,
                'enabled': True,
                'days': sorted(selected_days),
                'snooze_until': None
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
            self.reminders[index]['played'] = False  # Reset played status
            # Remove from triggered set when toggling
            reminder_key = f"{index}_{self.reminders[index]['time']}"
            self.triggered_reminders.discard(reminder_key)
            self.save_reminders()
            self.refresh_reminder_list()

    def delete_reminder(self, index):
        if 0 <= index < len(self.reminders):
            # Confirmation popup
            content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
            content.add_widget(Label(
                text="Delete this reminder?",
                font_size='18sp',
                size_hint=(1, 0.4)
            ))
            content.add_widget(Label(
                text=self.reminders[index]['text'],
                font_size='14sp',
                color=(0.5, 0.5, 0.5, 1),
                size_hint=(1, 0.3)
            ))
            
            btn_box = BoxLayout(size_hint=(1, 0.3), spacing=dp(10))
            
            cancel_btn = Button(
                text="Cancel",
                background_normal='',
                background_color=(0.7, 0.7, 0.7, 1)
            )
            
            delete_btn = Button(
                text="Delete",
                background_normal='',
                background_color=(0.9, 0.4, 0.4, 1),
                color=(1, 1, 1, 1)
            )
            
            btn_box.add_widget(cancel_btn)
            btn_box.add_widget(delete_btn)
            content.add_widget(btn_box)
            
            confirm_popup = Popup(
                content=content,
                size_hint=(0.8, 0.4),
                title=""
            )
            
            def do_delete(instance):
                # Remove from triggered set
                reminder_key = f"{index}_{self.reminders[index]['time']}"
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
        
        self.stats_label.text = f"📊 Total: {total} reminders  |  ✓ Active: {active}  |  ○ Inactive: {total - active}"
        
        if not self.reminders:
            empty_card = ModernCard(bg_color=(0.98, 0.98, 1, 1))
            empty_card.size_hint_y = None
            empty_card.height = dp(150)
            empty_card.padding = dp(20)
            
            empty_box = BoxLayout(orientation='vertical', spacing=dp(10))
            empty_box.add_widget(Label(
                text="📭",
                font_size='48sp',
                size_hint_y=0.5
            ))
            empty_box.add_widget(Label(
                text="No reminders yet",
                font_size='18sp',
                bold=True,
                size_hint_y=0.25,
                color=(0.3, 0.3, 0.3, 1)
            ))
            empty_box.add_widget(Label(
                text="Tap 'Add New Reminder' to create one",
                font_size='14sp',
                size_hint_y=0.25,
                color=(0.5, 0.5, 0.5, 1)
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

    def check_reminders(self, dt):
        try:
            now = datetime.datetime.now()
            current_time = now.time().replace(second=0, microsecond=0)
            current_day = now.weekday()
            
            for idx, r in enumerate(self.reminders):
                if not r.get('enabled'):
                    continue
                
                # Create unique key for this reminder
                reminder_key = f"{idx}_{r['time']}"
                
                # Check snooze
                if r.get('snooze_until'):
                    if now >= r['snooze_until']:
                        r['snooze_until'] = None
                        r['played'] = False
                        self.triggered_reminders.discard(reminder_key)
                    else:
                        continue
                
                if current_day not in r.get('days', list(range(7))):
                    continue
                    
                # Check if reminder should trigger and hasn't been triggered yet
                if r['time'] == current_time and not r['played'] and reminder_key not in self.triggered_reminders:
                    self.show_alarm(r)
                    r['played'] = True
                    self.triggered_reminders.add(reminder_key)
            
            # Reset at midnight
            if current_time.hour == 0 and current_time.minute == 0:
                for r in self.reminders:
                    if not r.get('snooze_until'):
                        r['played'] = False
                self.triggered_reminders.clear()
        except Exception as e:
            print(f"Check reminders error: {e}")
            import traceback
            traceback.print_exc()

    def snooze_alarm(self, reminder):
        """Snooze the alarm for specified minutes"""
        reminder['snooze_until'] = datetime.datetime.now() + datetime.timedelta(minutes=self.snooze_minutes)
        reminder['played'] = True
        if self.alarm_popup:
            self.alarm_popup.dismiss()
        print(f"Snoozed for {self.snooze_minutes} minutes")

    def show_alarm(self, reminder):
        try:
            # Vibrate on Android
            if platform == 'android':
                try:
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    Context = autoclass('android.content.Context')
                    Vibrator = autoclass('android.os.Vibrator')
                    activity = PythonActivity.mActivity
                    vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                    
                    # Vibrate pattern: wait, vibrate, wait, vibrate
                    pattern = [0, 500, 200, 500, 200, 500]
                    if hasattr(vibrator, 'vibrate'):
                        try:
                            vibrator.vibrate(pattern, -1)
                        except:
                            vibrator.vibrate(2000)
                except Exception as e:
                    print(f"Vibration error: {e}")
            
            content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
            
            # Alarm icon
            content.add_widget(Label(
                text="⏰",
                font_size='64sp',
                size_hint=(1, 0.2)
            ))
            
            # Alarm title
            content.add_widget(Label(
                text="REMINDER!",
                font_size='28sp',
                bold=True,
                color=(0.9, 0.3, 0.3, 1),
                size_hint=(1, 0.15)
            ))
            
            # Reminder text
            reminder_label = Label(
                text=reminder['text'],
                font_size='18sp',
                size_hint=(1, 0.2),
                color=(0.2, 0.2, 0.2, 1)
            )
            content.add_widget(reminder_label)
            
            # Time
            content.add_widget(Label(
                text=datetime.datetime.now().strftime('%I:%M %p'),
                font_size='16sp',
                size_hint=(1, 0.1),
                color=(0.5, 0.5, 0.5, 1)
            ))
            
            # Snooze controls
            snooze_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=dp(10))
            snooze_label = Label(
                text=f"Snooze for {self.snooze_minutes} minutes",
                font_size='14sp',
                size_hint=(1, 0.4)
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
                snooze_label.text = f"Snooze for {self.snooze_minutes} minutes"
            
            slider.bind(value=update_snooze)
            
            snooze_box.add_widget(snooze_label)
            snooze_box.add_widget(slider)
            content.add_widget(snooze_box)
            
            # Buttons
            btn_box = BoxLayout(size_hint=(1, 0.15), spacing=dp(10))
            
            snooze_btn = Button(
                text="😴 Snooze",
                background_normal='',
                background_color=(0.95, 0.7, 0.3, 1),
                color=(1, 1, 1, 1),
                font_size='16sp',
                bold=True
            )
            
            dismiss_btn = Button(
                text="✓ Dismiss",
                background_normal='',
                background_color=(0.3, 0.7, 0.4, 1),
                color=(1, 1, 1, 1),
                font_size='16sp',
                bold=True
            )
            
            btn_box.add_widget(snooze_btn)
            btn_box.add_widget(dismiss_btn)
            content.add_widget(btn_box)
            
            self.alarm_popup = Popup(
                content=content,
                size_hint=(0.95, 0.7),
                auto_dismiss=False,
                title="",
                separator_height=0,
                background_color=(1, 1, 1, 0.98)
            )
            
            snooze_btn.bind(on_press=lambda x: self.snooze_alarm(reminder))
            dismiss_btn.bind(on_press=lambda x: self.alarm_popup.dismiss())
            self.alarm_popup.open()
        except Exception as e:
            print(f"Show alarm error: {e}")
            import traceback
            traceback.print_exc()

    def on_pause(self):
        """Allow app to pause without closing"""
        return True

    def on_resume(self):
        """Handle app resume"""
        self.refresh_reminder_list()

    def on_stop(self):
        """Save data when app closes"""
        print("App stopping...")
        self.save_reminders()


if __name__ == "__main__":
    print("Starting ReminderApp...")
    try:
        ReminderApp().run()
    except Exception as e:
        print(f"App crash: {e}")
        import traceback
        traceback.print_exc()
