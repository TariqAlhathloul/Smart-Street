import os
import platform
import psutil
import streamlit as st

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_cpu_temperature():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=", "").replace("'C\n", "°C")

def get_platform_info():
    return platform.platform()

totalmem = os.totalmem()
freemem = os.freemem()
usedmem = totalmem - freemem

def main():
    st.title("Raspberry Pi System Information")

    st.header("CPU Usage")
    st.text(f"{get_cpu_usage()}%")

    st.header("CPU Temperature")
    st.text(get_cpu_temperature())

    st.header("Memeory Usage RAM")
    st.text(f"Total Memory: {totalmem}")

    st.header("Platform Info")
    st.text(get_platform_info())

if __name__ == "__main__":
    main()
