import time
import threading
import subprocess
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import arabic_reshaper
from bidi.algorithm import get_display
import tkinter as tk
from tkinter import simpledialog

# تنظیم فونت پیش‌فرض برای matplotlib به Tahoma
rcParams['font.family'] = 'Tahoma'
rcParams['font.size'] = 12

# تابع برای دریافت IP‌ها از کاربر با استفاده از یک پنجره گرافیکی
def get_ips():
    root = tk.Tk()
    root.withdraw()  # مخفی کردن پنجره اصلی
    ip_input = simpledialog.askstring("Input", "لطفاً IP‌ها را وارد کنید، آنها را با کاما جدا کنید:")
    if ip_input:
        return ip_input.split(",")
    else:
        return []

# دریافت IP‌ها از کاربر
ips = get_ips()
if not ips:
    print("هیچ IP وارد نشد. برنامه خاتمه یافت.")
    exit(1)

# تابع برای پینگ کردن IP‌ها
def ping_ips():
    while True:
        responses = []
        for ip in ips:
            response = subprocess.run(["ping", "-n", "1", "-w", "500", ip], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
            responses.append(response.returncode == 0)
        ping_results.append(responses)
        if len(ping_results) > max_display_time:
            ping_results.pop(0)
        time.sleep(1)

# تنظیمات اولیه برای نمودار
fig, ax = plt.subplots()
ping_results = []
max_display_time = 100  # حداکثر تعداد نقاط زمانی که در نمودار نمایش داده می‌شود

# تابع برای به‌روزرسانی نمودار
def update_graph(i):
    ax.clear()
    # استفاده از arabic_reshaper و bidi برای پشتیبانی از حروف فارسی و عربی
    xlabel = arabic_reshaper.reshape("زمان (ثانیه)")
    ylabel = arabic_reshaper.reshape("وضعیت (پاسخ دارد/ندارد)")
    xlabel = get_display(xlabel)
    ylabel = get_display(ylabel)
    
    ax.set_title("PHOENIX Monitoring", fontname='Tahoma', loc='right')
    ax.set_xlabel(xlabel, fontname='Tahoma', loc='right')
    ax.set_ylabel(ylabel, fontname='Tahoma', loc='top')

    times = list(range(len(ping_results)))
    for idx, ip in enumerate(ips):
        ax.plot(times, [result[idx] for result in ping_results], label=ip)

    ax.set_xlim(left=max(0, len(ping_results) - max_display_time), right=len(ping_results))
    ax.set_ylim(-0.1, 1.1)
    
    # تنظیم فونت و استفاده از arabic_reshaper و bidi برای برچسب‌ها
    labels = [get_display(arabic_reshaper.reshape(ip)) for ip in ips]
    ax.legend(labels=labels, prop={'family': 'Tahoma'}, loc='upper right')

# شروع پینگ کردن IP‌ها در یک ترد جداگانه
ping_thread = threading.Thread(target=ping_ips)
ping_thread.daemon = True
ping_thread.start()

# شروع رسم نمودار به صورت پویا
ani = animation.FuncAnimation(fig, update_graph, interval=500, save_count=100, cache_frame_data=False)

# نمایش نمودار به صورت زنده
plt.show()
