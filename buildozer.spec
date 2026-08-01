[app]
title = MARZ-X
package.name = marzxclient
package.domain = org.marz

requirements = python3,kivy,requests,pyjnius,android

android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30

android.permissions = INTERNET, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE, WAKE_LOCK, SYSTEM_ALERT_WINDOW, POST_NOTIFICATIONS

android.gradle_dependencies = androidx.core:core:1.12.0, androidx.appcompat:appcompat:1.6.1

[buildozer]
log_level = 2
warn_on_root = 1
