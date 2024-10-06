import os
import psutil
# to debug the raspberry pi temperature while inferencing
#we can use the vcgencmd command to get the temperature of the raspberry pi but we need to use the os module to run the command

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_cpu_temperature():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=", "").replace("'C\n", "°C")


def print_system_status():
    print("CPU Usage: ", get_cpu_usage(), "%")
    print("CPU Temperature: ", get_cpu_temperature())


if __name__ == "__main__":
    print_system_status()