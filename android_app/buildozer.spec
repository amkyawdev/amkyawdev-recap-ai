[app]

# App name and package
title = Recap AI
package.name = recapai
package.domain = com.amkyawdev

# App icon
icon = icon.png

# Source directories
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Requirements
requirements = python3,kivy==2.2.0,kivymd,httpx,aiofiles

# Android specific
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA
android.archs = arm64-v8a,armeabi-v7a
android.minapi = 21
android.ndk_api = 21

# Kivy
fullscreen = 0
orientation = all

# Window
window_title = Recap AI

[buildozer]

# Log level
log_level = 2

# Build target
target = android

# Android SDK
android.sdk = 27
android.ndk = 25b

# Development mode
dev_mode = True

# Bundle
android.bundle = False

# Release (set to False for debug)
android.release = False
