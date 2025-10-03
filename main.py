import os
import json
import datetime
import threading
from functools import partial
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.snackbar import Snackbar

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    request_permissions([
        Permission.VIBRATE,
        Permission.WAKE_LOCK,
        Permission.RECEIVE_BOOT_COMPLETED,
        Permission.SCHEDULE_EXACT_ALARM,
        Permission.POST_NOTIFICATIONS,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_MEDIA_AUDIO
    ])

KV = '''
BoxLayout:
    orientation: "vertical"
    padding: "10dp"
    spacing: "10dp"

    MDLabel:
        text: "⏰ ReminderApp"
        halign: "center"
        font_style: "H4"

    MDLabel:
        id: time_label
        halign: "center"
        font_style: "H6"

    MDTextField:
        id: reminder_text
        hint_text: "Enter reminder text"
        mode: "rectangle"

    BoxLayout:
        size_hint_y: None
        height: "40dp"
        spacing: "5dp"

        MDTextField:
            id: hour
            hint_text: "HH"
            mode: "rectangle"

        MDLabel:
            text: ":"

        MDTextField:
            id: minute
            hint_text: "MM"
            mode: "rectangle"

        MDTextField:
            id: ampm
            hint_text: "AM/PM"
            mode: "rectangle"

    MDRaisedButton:
        text: "Select Ringtone"
        on_release: app.open_filemanager()

    MDSwitch:
        id: repeat_switch
        active: True

    MDRaisedButton:
        text: "Add Reminder"
        on_release: app.add_reminder()

    MDLabel:
        id: reminder_count
        halign: "center"

    MDBoxLayout:
        id: reminder_list
        orientation: "vertical"
'''

class ReminderApp(MDApp):
    def build(self):
        self.reminders = []
        self.current_sound = None
        self.current_reminder = None
        self.ringtone_path = None
        self.default_ringtones = [
            os.path.join("assets/ringtones/ring1.mp3"),
            os.path.join("assets/ringtones/ring2.mp3")
        ]

        if platform == 'android':
            from android.storage import primary_external_storage_path
            self.storage_path = primary_external_storage_path()
            self.data_file = os.path.join(self.user_data_dir, 'reminders.json')
        else:
            self.storage_path = os.path.expanduser("~")
            self.data_file = os.path.join(os.path.dirname(__file__), 'reminders.json')

        self.load_reminders()
        self.file_manager = MDFileManager(select_path=self.select_ringtone, exit_manager=self.exit_file_manager)
        self.root = Builder.load_string(KV)
        Clock.schedule_interval(self.update_time, 1)
        Clock.schedule_interval(self.check_reminders, 1)
        self.refresh_reminder_list()
        return self.root

    def update_time(self, dt):
        now = datetime.datetime.now()
        self.root.ids.time_label.text = now.strftime('%I:%M:%S %p')

    def load_reminders(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        hour, minute = map(int, item['time'].split(':'))
                        reminder = {
                            'text': item['text'],
                            'time': datetime.time(hour, minute),
                            'ringtone': item['ringtone'],
                            'played': False,
                            'recurring': item.get('recurring', True),
                            'enabled': item.get('enabled', True)
                        }
                        self.reminders.append(reminder)
        except Exception as e:
            print(f"Error loading reminders: {e}")

    def save_reminders(self):
        try:
            data = []
            for reminder in self.reminders:
                data.append({
                    'text': reminder['text'],
                    'time': reminder['time'].strftime('%H:%M'),
                    'ringtone': reminder['ringtone'],
                    'recurring': reminder.get('recurring', True),
                    'enabled': reminder.get('enabled', True)
                })
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving reminders: {e}")

    def open_filemanager(self):
        self.file_manager.show(self.storage_path)

    def select_ringtone(self, path):
        self.ringtone_path = path
        Snackbar(text=f"Selected: {os.path.basename(path)}").open()
        self.file_manager.close()

    def exit_file_manager(self, *args):
        self.file_manager.close()

    def add_reminder(self):
        text = self.root.ids.reminder_text.text.strip()
        hour_text = self.root.ids.hour.text.strip()
        minute_text = self.root.ids.minute.text.strip()
        ampm = self.root.ids.ampm.text.strip().upper()

        if not text:
            Snackbar(text="Enter reminder text!").open()
            return

        if not self.ringtone_path:
            self.ringtone_path = self.default_ringtones[0]

        hour = int(hour_text)
        minute = int(minute_text)
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

        reminder_time = datetime.time(hour, minute)
        for r in self.reminders:
            if r['time'] == reminder_time:
                Snackbar(text="Reminder already exists at this time!").open()
                return

        reminder = {
            "text": text,
            "time": reminder_time,
            "ringtone": self.ringtone_path,
            "played": False,
            "recurring": self.root.ids.repeat_switch.active,
            "enabled": True
        }
        self.reminders.append(reminder)
        self.reminders.sort(key=lambda x: (x['time'].hour, x['time'].minute))
        self.save_reminders()
        self.refresh_reminder_list()
        self.root.ids.reminder_text.text = ""
        self.root.ids.hour.text = ""
        self.root.ids.minute.text = ""
        self.root.ids.ampm.text = ""
        self.ringtone_path = None
        self.root.ids.repeat_switch.active = True
        Snackbar(text=f"Reminder set for {reminder_time.strftime('%I:%M %p')}").open()

    def refresh_reminder_list(self):
        self.root.ids.reminder_list.clear_widgets()
        for r in self.reminders:
            if not r.get('enabled', True):
                continue
            self.root.ids.reminder_list.add_widget(
                OneLineListItem(text=f"{r['text']} - {r['time'].strftime('%I:%M %p')}")
            )
        self.root.ids.reminder_count.text = f"Active Reminders: {len([r for r in self.reminders if r.get('enabled', True)])}"

    def check_reminders(self, dt):
        now = datetime.datetime.now().time().replace(second=0, microsecond=0)
        for r in self.reminders:
            if r['enabled'] and r['time'] == now and not r['played']:
                threading.Thread(target=self.play_sound, args=(r,), daemon=True).start()
                r['played'] = True
        if now.hour == 0 and now.minute == 0:
            for r in self.reminders:
                if r.get('recurring', True):
                    r['played'] = False

    def play_sound(self, reminder):
        self.current_reminder = reminder
        if platform == 'android':
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
        dialog = MDDialog(
            title="⏰ ALARM!",
            text=reminder['text'],
            buttons=[
                MDFlatButton(text="SNOOZE", on_release=self.snooze_alarm),
                MDFlatButton(text="STOP", on_release=self.stop_alarm)
            ]
        )
        dialog.open()

    def stop_alarm(self, instance):
        if self.current_sound:
            self.current_sound.stop()
        instance.parent.parent.dismiss()

    def snooze_alarm(self, instance):
        if self.current_sound:
            self.current_sound.stop()
        instance.parent.parent.dismiss()
        if self.current_reminder:
            current_time = datetime.datetime.combine(datetime.date.today(), self.current_reminder['time'])
            snooze_time = (current_time + datetime.timedelta(minutes=5)).time()
            self.current_reminder['time'] = snooze_time
            self.current_reminder['played'] = False
            self.current_reminder['recurring'] = False
            self.save_reminders()
            self.refresh_reminder_list()
            Snackbar(text=f"Snoozed until {snooze_time.strftime('%I:%M %p')}").open()

if __name__ == "__main__":
    ReminderApp().run()
