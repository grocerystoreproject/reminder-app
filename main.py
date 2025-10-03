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
from kivy.uix.switch import Switch
from kivy.uix.checkbox import CheckBox
from kivy.utils import platform

print("App starting...")

# Request permissions on Android
if platform == 'android':
    print("Requesting Android permissions...")
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.VIBRATE, Permission.WAKE_LOCK])
        print("Permissions requested")
    except Exception as e:
        print(f"Permission error: {e}")


class ReminderCard(BoxLayout):
    def __init__(self, reminder, index, callbacks, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 80
        self.padding = 10
        self.spacing = 10
        
        # Left side - info
        info_box = BoxLayout(orientation='vertical', size_hint_x=0.6)
        
        status = "[ON]" if reminder.get('enabled', True) else "[OFF]"
        text_lbl = Label(
            text=f"{status} {reminder['text']}", 
            halign='left', valign='top',
            font_size='14sp'
        )
        text_lbl.bind(size=text_lbl.setter('text_size'))
        
        time_lbl = Label(
            text=reminder['time'].strftime('%I:%M %p'),
            halign='left', valign='bottom',
            font_size='16sp', bold=True
        )
        time_lbl.bind(size=time_lbl.setter('text_size'))
        
        info_box.add_widget(text_lbl)
        info_box.add_widget(time_lbl)
        
        # Right side - buttons
        btn_box = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=5)
        
        toggle_btn = Button(
            text="ON" if reminder.get('enabled') else "OFF",
            size_hint_y=0.33
        )
        toggle_btn.bind(on_press=lambda x: callbacks['toggle'](index))
        
        edit_btn = Button(text="Edit", size_hint_y=0.33)
        edit_btn.bind(on_press=lambda x: callbacks['edit'](index))
        
        del_btn = Button(text="Delete", size_hint_y=0.34)
        del_btn.bind(on_press=lambda x: callbacks['delete'](index))
        
        btn_box.add_widget(toggle_btn)
        btn_box.add_widget(edit_btn)
        btn_box.add_widget(del_btn)
        
        self.add_widget(info_box)
        self.add_widget(btn_box)


class ReminderApp(App):
    def build(self):
        print("Building UI...")
        self.reminders = []
        self.editing_index = None
        self.alarm_popup = None
        
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
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint=(1, None), height=50)
        title = Label(text="Reminder App", font_size='24sp', bold=True, halign='left')
        title.bind(size=title.setter('text_size'))
        
        self.time_label = Label(text="", font_size='18sp', halign='right')
        self.time_label.bind(size=self.time_label.setter('text_size'))
        
        header.add_widget(title)
        header.add_widget(self.time_label)
        self.layout.add_widget(header)
        
        Clock.schedule_interval(self.update_time, 1)

        # Add button
        add_btn = Button(
            text="Add Reminder",
            size_hint=(1, None),
            height=50
        )
        add_btn.bind(on_press=self.show_add_dialog)
        self.layout.add_widget(add_btn)

        # Stats
        self.stats_label = Label(
            text="", 
            size_hint=(1, None), 
            height=30,
            halign='left'
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        self.layout.add_widget(self.stats_label)

        # Reminder list
        scroll = ScrollView(size_hint=(1, 1))
        self.reminder_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        self.reminder_list.bind(minimum_height=self.reminder_list.setter('height'))
        scroll.add_widget(self.reminder_list)
        self.layout.add_widget(scroll)

        root.add_widget(self.layout)
        
        self.refresh_reminder_list()
        Clock.schedule_interval(self.check_reminders, 10)  # Check every 10 seconds
        
        print("UI built successfully")
        return root

    def update_time(self, dt):
        now = datetime.datetime.now()
        self.time_label.text = now.strftime('%I:%M %p')

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
                            'days': item.get('days', list(range(7)))
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
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Text input
        text_input = TextInput(
            hint_text="Reminder text", 
            size_hint=(1, None), 
            height=50,
            multiline=False
        )
        if reminder:
            text_input.text = reminder['text']
        content.add_widget(text_input)

        # Time selection
        time_box = BoxLayout(size_hint=(1, None), height=50, spacing=5)
        
        hour = Spinner(
            text=str(reminder['time'].hour % 12 or 12) if reminder else "12",
            values=[str(i) for i in range(1, 13)], 
            size_hint=(0.3, 1)
        )
        
        minute = Spinner(
            text=str(reminder['time'].minute).zfill(2) if reminder else "00",
            values=[str(i).zfill(2) for i in range(0, 60, 5)], 
            size_hint=(0.3, 1)
        )
        
        ampm = Spinner(
            text="PM" if reminder and reminder['time'].hour >= 12 else "AM",
            values=["AM", "PM"], 
            size_hint=(0.3, 1)
        )
        
        time_box.add_widget(Label(text="Time:", size_hint=(0.1, 1)))
        time_box.add_widget(hour)
        time_box.add_widget(minute)
        time_box.add_widget(ampm)
        content.add_widget(time_box)

        # Days selection
        days_label = Label(text="Repeat on days:", size_hint=(1, None), height=30)
        content.add_widget(days_label)
        
        days_box = BoxLayout(size_hint=(1, None), height=40, spacing=2)
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_checks = []
        
        for i, day in enumerate(day_names):
            cb_box = BoxLayout(orientation='vertical', size_hint=(1, 1))
            cb = CheckBox(
                active=reminder and i in reminder.get('days', list(range(7))) if reminder else True,
                size_hint=(1, 0.7)
            )
            cb_box.add_widget(Label(text=day, size_hint=(1, 0.3), font_size='10sp'))
            cb_box.add_widget(cb)
            day_checks.append(cb)
            days_box.add_widget(cb_box)
        content.add_widget(days_box)

        # Buttons
        btn_box = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

        popup = Popup(
            title="Add Reminder" if not reminder else "Edit Reminder",
            content=content, 
            size_hint=(0.9, 0.8)
        )

        def save_reminder(instance):
            text = text_input.text.strip()
            if not text:
                print("No text entered")
                return

            h = int(hour.text)
            m = int(minute.text)
            if ampm.text == "PM" and h != 12:
                h += 12
            elif ampm.text == "AM" and h == 12:
                h = 0

            selected_days = [i for i, cb in enumerate(day_checks) if cb.active]
            if not selected_days:
                print("No days selected")
                return

            new_reminder = {
                'text': text, 
                'time': datetime.time(h, m),
                'played': False,
                'recurring': len(selected_days) > 1, 
                'enabled': True,
                'days': selected_days
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
            self.save_reminders()
            self.refresh_reminder_list()

    def delete_reminder(self, index):
        if 0 <= index < len(self.reminders):
            del self.reminders[index]
            self.save_reminders()
            self.refresh_reminder_list()

    def refresh_reminder_list(self):
        self.reminder_list.clear_widgets()
        
        active = sum(1 for r in self.reminders if r.get('enabled', True))
        total = len(self.reminders)
        
        self.stats_label.text = f"Total: {total} | Active: {active}"
        
        if not self.reminders:
            empty = Label(
                text="No reminders yet.\nTap 'Add Reminder' to create one.",
                size_hint_y=None, 
                height=100,
                font_size='16sp'
            )
            self.reminder_list.add_widget(empty)
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
            
            for r in self.reminders:
                if not r.get('enabled'):
                    continue
                if current_day not in r.get('days', list(range(7))):
                    continue
                if r['time'] == current_time and not r['played']:
                    self.show_alarm(r)
                    r['played'] = True
            
            # Reset at midnight
            if current_time.hour == 0 and current_time.minute == 0:
                for r in self.reminders:
                    r['played'] = False
        except Exception as e:
            print(f"Check reminders error: {e}")

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
                    vibrator.vibrate(2000)  # Vibrate for 2 seconds
                except Exception as e:
                    print(f"Vibration error: {e}")
            
            content = BoxLayout(orientation='vertical', spacing=20, padding=20)
            
            content.add_widget(Label(
                text="ALARM!", 
                font_size='32sp', 
                bold=True, 
                size_hint=(1, 0.2)
            ))
            
            content.add_widget(Label(
                text=reminder['text'], 
                font_size='20sp', 
                size_hint=(1, 0.3)
            ))
            
            content.add_widget(Label(
                text=datetime.datetime.now().strftime('%I:%M %p'), 
                font_size='18sp', 
                size_hint=(1, 0.2)
            ))
            
            dismiss_btn = Button(
                text="DISMISS", 
                size_hint=(1, 0.3),
                font_size='18sp'
            )
            content.add_widget(dismiss_btn)
            
            self.alarm_popup = Popup(
                content=content, 
                size_hint=(0.9, 0.5),
                auto_dismiss=False
            )
            
            dismiss_btn.bind(on_press=lambda x: self.alarm_popup.dismiss())
            self.alarm_popup.open()
        except Exception as e:
            print(f"Show alarm error: {e}")

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        print("App stopping...")


if __name__ == "__main__":
    print("Starting ReminderApp...")
    try:
        ReminderApp().run()
    except Exception as e:
        print(f"App crash: {e}")
        import traceback
        traceback.print_exc()
