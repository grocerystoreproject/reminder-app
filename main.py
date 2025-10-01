import os
import datetime
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView


class ReminderApp(App):
    def build(self):
        self.reminders = []  # store reminders
        self.current_sound = None
        self.current_reminder = None

        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Reminder text input
        self.text_input = TextInput(hint_text="Enter reminder text", size_hint=(1, 0.1))
        self.layout.add_widget(self.text_input)

        # Time selectors with AM/PM toggle
        time_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.hour_input = Spinner(text="12", values=[str(i).zfill(2) for i in range(1, 13)])
        self.min_input = Spinner(text="00", values=[str(i).zfill(2) for i in range(0, 60)])
        self.ampm_input = Spinner(text="AM", values=["AM", "PM"])
        time_layout.add_widget(self.hour_input)
        time_layout.add_widget(Label(text=":"))
        time_layout.add_widget(self.min_input)
        time_layout.add_widget(self.ampm_input)
        self.layout.add_widget(time_layout)

        # Ringtone selection
        self.file_label = Label(text="No ringtone selected", size_hint=(1, 0.1))
        self.layout.add_widget(self.file_label)
        self.ringtone_path = None
        file_btn = Button(text="Choose Ringtone", size_hint=(1, 0.1))
        file_btn.bind(on_press=self.open_filechooser)
        self.layout.add_widget(file_btn)

        # Add reminder button
        add_btn = Button(text="Add Reminder", size_hint=(1, 0.1))
        add_btn.bind(on_press=self.add_reminder)
        self.layout.add_widget(add_btn)

        # Scrollable list of reminders
        scroll = ScrollView(size_hint=(1, 0.5))
        self.reminder_list = BoxLayout(orientation="vertical", size_hint_y=None)
        self.reminder_list.bind(minimum_height=self.reminder_list.setter('height'))
        scroll.add_widget(self.reminder_list)
        self.layout.add_widget(scroll)

        # Check reminders every second
        Clock.schedule_interval(self.check_reminders, 1)

        return self.layout

    def open_filechooser(self, instance):
        chooser = FileChooserIconView(path=os.path.expanduser("~"))
        popup = Popup(title="Select Ringtone", content=chooser, size_hint=(0.9, 0.9))

        def select_file(instance, touch):
            if chooser.selection:
                self.ringtone_path = chooser.selection[0]
                self.file_label.text = f"Ringtone: {os.path.basename(self.ringtone_path)}"
                popup.dismiss()

        chooser.bind(on_submit=select_file)
        popup.open()

    def add_reminder(self, instance):
        text = self.text_input.text.strip()
        hour = int(self.hour_input.text)
        minute = int(self.min_input.text)
        ampm = self.ampm_input.text

        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

        reminder_time = datetime.time(hour, minute)
        if text and self.ringtone_path:
            reminder = {
                "text": text,
                "time": reminder_time,
                "ringtone": self.ringtone_path,
                "played": False,
                "recurring": True,
            }
            self.reminders.append(reminder)

            lbl = Label(
                text=f"{text} at {reminder_time.strftime('%I:%M %p')} ({os.path.basename(self.ringtone_path)}) [Daily]",
                size_hint_y=None,
                height=30
            )
            self.reminder_list.add_widget(lbl)

            self.text_input.text = ""
            self.file_label.text = "No ringtone selected"
            self.ringtone_path = None

    def check_reminders(self, dt):
        now = datetime.datetime.now().time().replace(second=0, microsecond=0)
        for reminder in self.reminders:
            if reminder["time"] == now and not reminder["played"]:
                threading.Thread(target=self.play_sound, args=(reminder,)).start()
                reminder["played"] = True

        # Reset daily
        if now.hour == 0 and now.minute == 0:
            for reminder in self.reminders:
                reminder["played"] = False

    def play_sound(self, reminder):
        self.current_reminder = reminder
        self.current_sound = SoundLoader.load(reminder["ringtone"])
        if self.current_sound:
            self.current_sound.loop = True
            self.current_sound.play()

            # Popup with STOP/SNOOZE
            box = BoxLayout(orientation="vertical", spacing=10, padding=10)
            box.add_widget(Label(text=f"Reminder: {reminder['text']}"))

            btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
            stop_btn = Button(text="STOP Alarm")
            snooze_btn = Button(text="SNOOZE 5 min")
            stop_btn.bind(on_press=self.stop_alarm)
            snooze_btn.bind(on_press=self.snooze_alarm)
            btn_layout.add_widget(stop_btn)
            btn_layout.add_widget(snooze_btn)

            box.add_widget(btn_layout)

            popup = Popup(title="Alarm!", content=box, size_hint=(0.8, 0.5))
            popup.open()
            self.alarm_popup = popup

    def stop_alarm(self, instance):
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None
        if hasattr(self, "alarm_popup"):
            self.alarm_popup.dismiss()

    def snooze_alarm(self, instance):
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None
        if hasattr(self, "alarm_popup"):
            self.alarm_popup.dismiss()

        if self.current_reminder:
            snooze_time = (datetime.datetime.combine(datetime.date.today(), self.current_reminder["time"])
                           + datetime.timedelta(minutes=5)).time()
            self.current_reminder["time"] = snooze_time
            self.current_reminder["played"] = False


if __name__ == "__main__":
    ReminderApp().run()
