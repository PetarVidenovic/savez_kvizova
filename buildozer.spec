[app]
title = savez_kvizova
package.name = savez_kvizova
package.domain = org.savez.kvizova
source.dir = .
source.include_exts = py,kv,txt,mp3,png
source.include_patterns =
    pitanja_2.txt
    odgovori_2.txt
    tech-quiz-news-loop-274362.mp3
    app_icon.png
    quiz.kv
version = 1.0
requirements = python3,kivy==2.2.1,ffpyplayer,cython==0.29.33
orientation = portrait
fullscreen = 1
icon.filename = app_icon.png
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.allow_backup = False
android.enable_multiprocess = False
android.entrypoint = main.py
android.meta_data =
android.build_tools_version = 33.0.2
android.resource_files = tech-quiz-news-loop-274362.mp3
android.logcat_filters = *

 p4a.branch = develop



