import os
import json
import datetime
import threading
from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.VIBRATE, Permission.WAKE_LOCK, Permission.RECEIVE_BOOT_COMPLETED,
        Permission.SCHEDULE_EXACT_ALARM, Permission.POST_NOTIFICATIONS,
        Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_MEDIA_AUDIO
    ])


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            Color(*kwargs.get('bg_color', (0.2, 0.6, 0.9, 1)))
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0)
        self.cursor_color = (0.2, 0.6, 0.9, 1)
        self.foreground_color = (0.2, 0.2, 0.2, 1)
        with self.canvas.before:
            Color(0.95, 0.97, 0.99, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
            Color(0.8, 0.85, 0.9, 1)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 10), width=1.2)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 10)


class ReminderCard(BoxLayout):
    def __init__(self, reminder, index, callbacks, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 110
        self.padding = [10, 8]
        self.spacing = 5
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            Color(0.85, 0.9, 0.95, 0.3)
            self.shadow = RoundedRectangle(pos=(self.x, self.y-3), size=self.size, radius=[15])
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Top row
        top = BoxLayout(size_hint_y=0.35, spacing=8)
        status = "🔔" if reminder.get('enabled', True) else "🔕"
        text_lbl = Label(
            text=f"{status} {reminder['text']}", 
            size_hint_x=0.65, halign='left', valign='middle',
            color=(0.2, 0.3, 0.4, 1), font_size='16sp', bold=True
        )
        text_lbl.bind(size=text_lbl.setter('text_size'))
        
        time_lbl = Label(
            text=reminder['time'].strftime('%I:%M %p'),
            size_hint_x=0.35, halign='right',
            color=(0.2, 0.6, 0.9, 1), font_size='18sp', bold=True
        )
        time_lbl.bind(size=time_lbl.setter('text_size'))
        top.add_widget(text_lbl)
        top.add_widget(time_lbl)
        
        # Middle row - days and repeat info
        middle = BoxLayout(size_hint_y=0.3, spacing=5)
        days_str = self.get_days_string(reminder.get('days', []))
        repeat_str = "Daily" if reminder.get('recurring') else "Once"
        if days_str:
            repeat_str = days_str
        
        info_lbl = Label(
            text=f"Repeat: {repeat_str}",
            size_hint_x=0.65, halign='left',
            color=(0.5, 0.5, 0.5, 1), font_size='13sp'
        )
        info_lbl.bind(size=info_lbl.setter('text_size'))
        middle.add_widget(info_lbl)
        
        # Bottom row
        bottom = BoxLayout(size_hint_y=0.35, spacing=5)
        ringtone = os.path.basename(reminder['ringtone'])
        if len(ringtone) > 20:
            ringtone = ringtone[:17] + "..."
        
        ring_lbl = Label(
            text=f"🎵 {ringtone}",
            size_hint_x=0.4, halign='left',
            color=(0.5, 0.5, 0.5, 1), font_size='13sp'
        )
        ring_lbl.bind(size=ring_lbl.setter('text_size'))
        
        edit_btn = RoundedButton(
            text="Edit", size_hint_x=0.2,
            bg_color=(0.5, 0.7, 0.9, 1),
            color=(1, 1, 1, 1), font_size='13sp'
        )
        edit_btn.bind(on_press=lambda x: callbacks['edit'](index, x))
        
        toggle_btn = RoundedButton(
            text="ON" if reminder.get('enabled') else "OFF",
            size_hint_x=0.2,
            bg_color=(0.2, 0.8, 0.3, 1) if reminder.get('enabled') else (0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1), font_size='13sp'
        )
        toggle_btn.bind(on_press=lambda x: callbacks['toggle'](index, x))
        
        del_btn = RoundedButton(
            text="Delete", size_hint_x=0.2,
            bg_color=(0.95, 0.4, 0.4, 1),
            color=(1, 1, 1, 1), font_size='13sp'
        )
        del_btn.bind(on_press=lambda x: callbacks['delete'](index, x))
        
        bottom.add_widget(ring_lbl)
        bottom.add_widget(edit_btn)
        bottom.add_widget(toggle_btn)
        bottom.add_widget(del_btn)
        
        self.add_widget(top)
        self.add_widget(middle)
        self.add_widget(bottom)
    
    def get_days_string(self, days):
        if not days or len(days) == 7:
            return ""
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return ", ".join([day_names[d] for d in sorted(days)])
    
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.shadow.pos = (self.x, self.y - 3)
        self.shadow.size = self.size


class ReminderApp(App):
    def build(self):
        self.reminders = []
        self.current_sound = None
        self.current_reminder = None
        self.available_ringtones = []
        self.editing_index = None
        
        # Scan ringtones
        ringtone_dir = "assets/ringtones"
        if os.path.exists(ringtone_dir):
            for file in os.listdir(ringtone_dir):
                if file.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                    self.available_ringtones.append(os.path.join(ringtone_dir, file))
        if not self.available_ringtones:
            self.available_ringtones = ["default.mp3"]

        if platform == 'android':
            from android.storage import primary_external_storage_path
            self.data_file = os.path.join(self.user_data_dir, 'reminders.json')
        else:
            self.data_file = os.path.join(os.path.dirname(__file__), 'reminders.json')

        self.load_reminders()

        root = FloatLayout()
        with root.canvas.before:
            Color(0.94, 0.96, 0.98, 1)
            self.bg = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)

        self.layout = BoxLayout(orientation="vertical", padding=[20, 30, 20, 20], spacing=15)

        # Header
        header = BoxLayout(size_hint=(1, None), height=60, spacing=10)
        title = Label(text="Reminders", font_size='32sp', size_hint=(0.6, 1),
                     halign='left', color=(0.2, 0.3, 0.4, 1), bold=True)
        title.bind(size=title.setter('text_size'))
        self.time_label = Label(text="", font_size='20sp', size_hint=(0.4, 1),
                               halign='right', color=(0.4, 0.5, 0.6, 1))
        self.time_label.bind(size=self.time_label.setter('text_size'))
        header.add_widget(title)
        header.add_widget(self.time_label)
        self.layout.add_widget(header)
        Clock.schedule_interval(self.update_time, 1)

        # Quick action buttons
        quick_actions = BoxLayout(size_hint=(1, None), height=50, spacing=8)
        add_quick = RoundedButton(text="Quick Add", bg_color=(0.2, 0.7, 0.5, 1),
                                 color=(1, 1, 1, 1), font_size='15sp')
        add_quick.bind(on_press=self.quick_add_reminder)
        sort_btn = RoundedButton(text="Sort", bg_color=(0.5, 0.6, 0.8, 1),
                                color=(1, 1, 1, 1), font_size='15sp')
        sort_btn.bind(on_press=self.sort_reminders)
        quick_actions.add_widget(add_quick)
        quick_actions.add_widget(sort_btn)
        self.layout.add_widget(quick_actions)

        # Search bar
        self.search_input = RoundedTextInput(
            hint_text="Search reminders...",
            size_hint=(1, None), height=45,
            multiline=False, font_size='15sp', padding=[15, 12]
        )
        self.search_input.bind(text=self.filter_reminders)
        self.layout.add_widget(self.search_input)

        # Stats
        self.stats_label = Label(
            text="", size_hint=(1, None), height=30,
            halign='left', color=(0.4, 0.5, 0.6, 1), font_size='14sp'
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        self.layout.add_widget(self.stats_label)

        # Reminders list
        scroll = ScrollView(size_hint=(1, 1))
        self.reminder_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=12)
        self.reminder_list.bind(minimum_height=self.reminder_list.setter('height'))
        scroll.add_widget(self.reminder_list)
        self.layout.add_widget(scroll)

        # FAB
        fab = RoundedButton(
            text="+", size_hint=(None, None), size=(60, 60),
            pos_hint={'right': 0.95, 'y': 0.03},
            bg_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1),
            font_size='32sp', bold=True
        )
        fab.bind(on_press=self.show_add_dialog)

        root.add_widget(self.layout)
        root.add_widget(fab)
        
        self.refresh_reminder_list()
        Clock.schedule_interval(self.check_reminders, 1)
        return root

    def update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def update_time(self, dt):
        now = datetime.datetime.now()
        self.time_label.text = now.strftime('%I:%M %p')

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
                            'ringtone': item['ringtone'],
                            'played': False,
                            'recurring': item.get('recurring', True),
                            'enabled': item.get('enabled', True),
                            'days': item.get('days', list(range(7))),
                            'snooze_count': item.get('snooze_count', 0),
                            'vibrate': item.get('vibrate', True),
                            'notes': item.get('notes', '')
                        })
        except Exception as e:
            print(f"Load error: {e}")

    def save_reminders(self):
        try:
            data = [{
                'text': r['text'], 'time': r['time'].strftime('%H:%M'),
                'ringtone': r['ringtone'], 'recurring': r.get('recurring', True),
                'enabled': r.get('enabled', True), 'days': r.get('days', list(range(7))),
                'snooze_count': r.get('snooze_count', 0),
                'vibrate': r.get('vibrate', True), 'notes': r.get('notes', '')
            } for r in self.reminders]
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")

    def show_add_dialog(self, instance):
        self.editing_index = None
        self.show_reminder_dialog()

    def show_reminder_dialog(self, reminder=None):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        # Text input
        text_input = RoundedTextInput(
            hint_text="Reminder text", size_hint=(1, None), height=50,
            multiline=False, font_size='15sp', padding=[15, 15]
        )
        if reminder:
            text_input.text = reminder['text']
        content.add_widget(text_input)

        # Time
        time_box = BoxLayout(size_hint=(1, None), height=50, spacing=5)
        hour = Spinner(
            text=str(reminder['time'].hour % 12 or 12) if reminder else "12",
            values=[str(i).zfill(2) for i in range(1, 13)], size_hint=(0.25, 1)
        )
        minute = Spinner(
            text=str(reminder['time'].minute).zfill(2) if reminder else "00",
            values=[str(i).zfill(2) for i in range(0, 60)], size_hint=(0.25, 1)
        )
        ampm = Spinner(
            text="PM" if reminder and reminder['time'].hour >= 12 else "AM",
            values=["AM", "PM"], size_hint=(0.25, 1)
        )
        time_box.add_widget(Label(text="Time:", size_hint=(0.25, 1)))
        time_box.add_widget(hour)
        time_box.add_widget(Label(text=":", size_hint=(0.1, 1)))
        time_box.add_widget(minute)
        time_box.add_widget(ampm)
        content.add_widget(time_box)

        # Ringtone
        ringtone_box = BoxLayout(size_hint=(1, None), height=50)
        ringtone_names = [os.path.basename(r) for r in self.available_ringtones]
        current_ringtone = os.path.basename(reminder['ringtone']) if reminder else ringtone_names[0]
        ringtone = Spinner(text=current_ringtone, values=ringtone_names, size_hint=(1, 1))
        ringtone_box.add_widget(ringtone)
        content.add_widget(ringtone_box)

        # Days selector
        days_label = Label(text="Repeat on:", size_hint=(1, None), height=30, halign='left')
        days_label.bind(size=days_label.setter('text_size'))
        content.add_widget(days_label)
        
        days_box = BoxLayout(size_hint=(1, None), height=40, spacing=5)
        day_names = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        day_checks = []
        for i, day in enumerate(day_names):
            cb_box = BoxLayout(orientation='vertical', size_hint=(1, 1))
            cb = CheckBox(active=reminder and i in reminder.get('days', list(range(7))) if reminder else True)
            cb_box.add_widget(Label(text=day, size_hint=(1, 0.5), font_size='12sp'))
            cb_box.add_widget(cb)
            day_checks.append(cb)
            days_box.add_widget(cb_box)
        content.add_widget(days_box)

        # Vibrate toggle
        vib_box = BoxLayout(size_hint=(1, None), height=40)
        vib_box.add_widget(Label(text="Vibrate:", halign='left'))
        vib_switch = Switch(active=reminder.get('vibrate', True) if reminder else True)
        vib_box.add_widget(vib_switch)
        content.add_widget(vib_box)

        # Notes
        notes_input = RoundedTextInput(
            hint_text="Notes (optional)", size_hint=(1, None), height=60,
            multiline=True, font_size='14sp', padding=[15, 10]
        )
        if reminder:
            notes_input.text = reminder.get('notes', '')
        content.add_widget(notes_input)

        # Buttons
        btn_box = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        save_btn = RoundedButton(text="Save", bg_color=(0.2, 0.7, 0.5, 1), color=(1, 1, 1, 1))
        cancel_btn = RoundedButton(text="Cancel", bg_color=(0.6, 0.6, 0.6, 1), color=(1, 1, 1, 1))
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

        popup = Popup(title="Add Reminder" if not reminder else "Edit Reminder",
                     content=content, size_hint=(0.95, 0.85), background='', separator_height=0)

        def save_reminder(instance):
            text = text_input.text.strip()
            if not text:
                self.show_snackbar("Enter reminder text")
                return

            h = int(hour.text)
            m = int(minute.text)
            if ampm.text == "PM" and h != 12:
                h += 12
            elif ampm.text == "AM" and h == 12:
                h = 0

            selected_days = [i for i, cb in enumerate(day_checks) if cb.active]
            if not selected_days:
                self.show_snackbar("Select at least one day")
                return

            ringtone_path = next((r for r in self.available_ringtones if os.path.basename(r) == ringtone.text), self.available_ringtones[0])

            new_reminder = {
                'text': text, 'time': datetime.time(h, m),
                'ringtone': ringtone_path, 'played': False,
                'recurring': len(selected_days) > 1, 'enabled': True,
                'days': selected_days, 'snooze_count': 0,
                'vibrate': vib_switch.active, 'notes': notes_input.text.strip()
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
            self.show_snackbar("Reminder saved")

        save_btn.bind(on_press=save_reminder)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def quick_add_reminder(self, instance):
        now = datetime.datetime.now()
        quick_time = (now + datetime.timedelta(minutes=5)).time()
        self.reminders.append({
            'text': 'Quick Reminder',
            'time': quick_time.replace(second=0, microsecond=0),
            'ringtone': self.available_ringtones[0],
            'played': False, 'recurring': False, 'enabled': True,
            'days': [now.weekday()], 'snooze_count': 0,
            'vibrate': True, 'notes': ''
        })
        self.save_reminders()
        self.refresh_reminder_list()
        self.show_snackbar(f"Quick reminder set for {quick_time.strftime('%I:%M %p')}")

    def edit_reminder(self, index, instance):
        if 0 <= index < len(self.reminders):
            self.editing_index = index
            self.show_reminder_dialog(self.reminders[index])

    def toggle_reminder(self, index, instance):
        if 0 <= index < len(self.reminders):
            self.reminders[index]['enabled'] = not self.reminders[index].get('enabled', True)
            self.save_reminders()
            self.refresh_reminder_list()

    def delete_reminder(self, index, instance):
        if 0 <= index < len(self.reminders):
            del self.reminders[index]
            self.save_reminders()
            self.refresh_reminder_list()
            self.show_snackbar("Reminder deleted")

    def sort_reminders(self, instance):
        options = ["Time (Ascending)", "Time (Descending)", "Name (A-Z)", "Name (Z-A)"]
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        for opt in options:
            btn = RoundedButton(
                text=opt, size_hint=(1, None), height=50,
                bg_color=(0.5, 0.6, 0.8, 1), color=(1, 1, 1, 1)
            )
            content.add_widget(btn)
        
        popup = Popup(title="Sort By", content=content, size_hint=(0.8, 0.5))
        
        def apply_sort(sort_type):
            if "Time (Ascending)" in sort_type:
                self.reminders.sort(key=lambda x: (x['time'].hour, x['time'].minute))
            elif "Time (Descending)" in sort_type:
                self.reminders.sort(key=lambda x: (x['time'].hour, x['time'].minute), reverse=True)
            elif "Name (A-Z)" in sort_type:
                self.reminders.sort(key=lambda x: x['text'].lower())
            elif "Name (Z-A)" in sort_type:
                self.reminders.sort(key=lambda x: x['text'].lower(), reverse=True)
            self.save_reminders()
            self.refresh_reminder_list()
            popup.dismiss()
        
        for i, btn in enumerate(content.children[::-1]):
            btn.bind(on_press=lambda x, opt=options[i]: apply_sort(opt))
        
        popup.open()

    def filter_reminders(self, instance, text):
        self.refresh_reminder_list(filter_text=text.lower())

    def refresh_reminder_list(self, filter_text=""):
        self.reminder_list.clear_widgets()
        
        filtered = [r for r in self.reminders if filter_text in r['text'].lower()] if filter_text else self.reminders
        
        active = sum(1 for r in filtered if r.get('enabled', True))
        total = len(filtered)
        upcoming = sum(1 for r in filtered if r.get('enabled') and not r['played'])
        
        self.stats_label.text = f"Active: {active}/{total}  |  Upcoming: {upcoming}"
        
        if not filtered:
            empty = Label(text="No reminders found", size_hint_y=None, height=100,
                         font_size='16sp', color=(0.6, 0.6, 0.6, 1))
            self.reminder_list.add_widget(empty)
            return
        
        callbacks = {
            'edit': self.edit_reminder,
            'toggle': self.toggle_reminder,
            'delete': self.delete_reminder
        }
        
        for idx, r in enumerate(filtered):
            actual_idx = self.reminders.index(r)
            self.reminder_list.add_widget(ReminderCard(r, actual_idx, callbacks))

    def check_reminders(self, dt):
        now = datetime.datetime.now()
        current_time = now.time().replace(second=0, microsecond=0)
        current_day = now.weekday()
        
        for r in self.reminders:
            if not r.get('enabled'):
                continue
            if current_day not in r.get('days', list(range(7))):
                continue
            if r['time'] == current_time and not r['played']:
                threading.Thread(target=self.play_sound, args=(r,), daemon=True).start()
                r['played'] = True
        
        if current_time.hour == 0 and current_time.minute == 0:
            for r in self.reminders:
                r['played'] = False
                r['snooze_count'] = 0

    def play_sound(self, reminder):
        self.current_reminder = reminder
        if platform == 'android' and reminder.get('vibrate', True):
            try:
                from android import vibrate
                vibrate(1)
            except:
                pass
        
        self.current_sound = SoundLoader.load(reminder['ringtone'])
        if self.current_sound:
            self.current_sound.loop = True
            self.current_sound.volume = 1.0
            self.current_sound.play()
        
        Clock.schedule_once(lambda dt: self.show_alarm(reminder), 0)

    def show_alarm(self, reminder):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        with content.canvas.before:
            Color(1, 1, 1, 1)
            alarm_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[25])
        content.bind(pos=lambda i, v: setattr(alarm_bg, 'pos', i.pos))
        content.bind(size=lambda i, v: setattr(alarm_bg, 'size', i.size))
        
        content.add_widget(Label(text="ALARM", font_size='28sp', bold=True, color=(0.2, 0.6, 0.9, 1), size_hint=(1, 0.15)))
        content.add_widget(Label(text=reminder['text'], font_size='20sp', color=(0.3, 0.3, 0.3, 1), size_hint=(1, 0.25)))
        if reminder.get('notes'):
            content.add_widget(Label(text=reminder['notes'], font_size='14sp', color=(0.5, 0.5, 0.5, 1), size_hint=(1, 0.15)))
        content.add_widget(Label(text=datetime.datetime.now().strftime('%I:%M %p'), font_size='18sp', color=(0.5, 0.5, 0.5, 1), size_hint=(1, 0.15)))
        
        btns = BoxLayout(size_hint=(1, 0.3), spacing=10)
        stop = RoundedButton(text="STOP", bg_color=(0.95, 0.4, 0.4, 1), color=(1, 1, 1, 1), font_size='16sp
