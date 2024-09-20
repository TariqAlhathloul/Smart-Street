import os
import platform
import psutil

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_cpu_temperature():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=", "").replace("'C\n", "°C")

def get_platform_info():
    return platform.platform()


def print_system_status():
    print("CPU Usage: ", get_cpu_usage(), "%")
    print("CPU Temperature: ", get_cpu_temperature())
    print("Platform: ", get_platform_info())

print_system_status()