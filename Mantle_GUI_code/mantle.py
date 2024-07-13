import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import tkinter as tk
import subprocess
import re
import time
import threading
from multiprocessing import Process
from tkinter import ttk
from tkinter import messagebox
from tkinter.font import Font
import os
from tkinter import PhotoImage
from PIL import Image, ImageTk

plt.rcParams['font.family'] = 'serif'

# Track Docker process
docker_process = None

global x 

# Initialize data storage for plotting
data_series = {
    'cpu_cstates': {'time': [], 'data': {'C1':[],'C2':[],'C3':[]}},
    'cpu_usage': {'time': [], 'data': [], 'per_core': []},
    'cpu_core_power': {'time': [], 'data': []},
    'cpu_pkg_power': {'time': [], 'data': []},
    'cpu_frequency': {'time': [], 'data': {'current': []}},
    'memory_usage': {'time': [], 'data': {'total': [], 'available': [], 'free': [], 'cached': []}},
    'disk_usage': {'time': [], 'data': {'total': [], 'used': [],'free': []}},
    'temperature': {'time': [], 'data': {}},
    'battery_percent': {'time': [], 'data': []},
    'battery_voltage': {'time': [], 'data': []},
    'nic_power': {'time': [], 'data': []},
    'packet_info': {'time': [], 'data': {'received': [], 'transmitted': []}},
    'system_load': {'time': [], 'data': []},
    'gpu_vddgfx': {'time': [], 'data': []},
    'gpu_ppt': {'time': [], 'data': []},
    'gpu_edge': {'time': [], 'data': []},
    'battery_secs_left': {'time': [], 'data': []},
    'battery_energy': {'time': [], 'data': []},
    'battery_energy_rate': {'time': [], 'data': []},
    'fan_rpm' : {'time': [], 'data': []}
}

interface = ""
windows = {}
def get_wifi_interface():
    try:
        # Run the nmcli command to get the device status
        result = subprocess.run(['nmcli', 'device', 'status'], stdout=subprocess.PIPE, text=True)
        
        # Split the output into lines
        lines = result.stdout.splitlines()
        
        # Iterate over each line and look for the wifi interface
        for line in lines:
            # Split the line into columns based on whitespace
            columns = line.split()
            
            # Check if the type is wifi
            if len(columns) > 1 and columns[1] == 'wifi':
                return columns[0]  # Return the interface name
        
        return None  # Return None if no wifi interface is found
    
    except Exception as e:
        print(f"Error extracting wifi interface: {e}")
        return None

def get_system_info():
    laptop_info_cmd = "hostnamectl status | grep 'Static hostname'"
    processor_info_cmd = "lscpu | grep -m 1 'Model name'"

    try:
        # Fetch laptop name and model
        laptop_info = subprocess.run(laptop_info_cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)
        
        # Find the line containing 'Static hostname'
        
        laptop_name_model = laptop_info.stdout.strip().split(":")[1].strip()
               
        # Fetch processor name
        processor_info = subprocess.run(processor_info_cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)
        processor_name = processor_info.stdout.strip().split(":")[1].strip()

        return {
            "laptop_name_model": laptop_name_model,
            "processor_name": processor_name
        }
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def get_cpu_cstates():
    c_state_values = {}

    # Run the turbostat command and capture the output
    process = subprocess.Popen(['sudo', 'turbostat', '--interval', '0.5'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    headers = []
    relevant_indices = {}

    while True:
        output = process.stdout.readline()
        if 'CPU' in output:
            headers = output.strip().split()
            # Find indices of relevant C-states (C1%, C2%, C3%)
            relevant_indices = {f'C{i}%': headers.index(f'C{i}%') for i in range(1, 4) if f'C{i}%' in headers}
        elif '-' in output:
            values = output.strip().split()
            for c_state, idx in relevant_indices.items():
                c_state_values[c_state] = float(values[idx])
            break

    process.terminate()


        # Return the latest values
    return c_state_values['C1%'], c_state_values['C2%'], c_state_values['C3%']

# Example usage
# Function to get CPU stats
def get_cpu_stats():
    cpu_stats = {
        'usage_per_core': psutil.cpu_percent(interval=1, percpu=True),
        'total_usage': psutil.cpu_percent(interval=1)
    }
    return cpu_stats

# Function to get CPU power consumption using turbostat with sudo (if needed)
def get_cpu_core_power_consumption():

    start_pwr1 = subprocess.run(['sudo', 'cat', '/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj'], stdout=subprocess.PIPE, text=True)
    energy_start1 = int(start_pwr1.stdout.strip())
    time_start1 = time.time()
    
    # Sleep for a short interval
    time.sleep(1)

    # Final readings
    end_pwr1 = subprocess.run(['sudo', 'cat', '/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj'], stdout=subprocess.PIPE, text=True)
    energy_end1 = int(end_pwr1.stdout.strip())
    time_end1 = time.time()

    # Calculate energy difference
    energy_diff1 = energy_end1 - energy_start1

    # Calculate time difference
    time_diff1 = time_end1 - time_start1

    # Calculate power consumption in watts
    if time_diff1 > 0:
        core_power = (energy_diff1 / (time_diff1*1000000))  # Convert from µJ to W
        return core_power
    else:
        return 0

def get_cpu_pkg_power_consumption():
    start_pwr2 = subprocess.run(['sudo', 'cat', '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj'], stdout=subprocess.PIPE, text=True)
    energy_start2 = int(start_pwr2.stdout.strip())
    time_start2 = int(time.time())
    
    # Sleep for a short interval
    time.sleep(1)

    # Final readings
    end_pwr2 = subprocess.run(['sudo', 'cat', '/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj'], stdout=subprocess.PIPE, text=True)
    energy_end2 = int(end_pwr2.stdout.strip())
    time_end2 = int(time.time())

    # Calculate energy difference
    energy_diff2 = energy_end2 - energy_start2

    # Calculate time difference
    time_diff2 = time_end2 - time_start2

    # Calculate power consumption in watts
    if time_diff2 > 0:
        pkg_power = (energy_diff2 / (time_diff2*1000000 )) # Convert from µJ to W
        return pkg_power
    else:
        return 0       
        
# Function to get CPU frequency
def get_cpu_frequency():
    return psutil.cpu_freq()._asdict()

# Function to get memory stats
def get_memory_stats():
    return psutil.virtual_memory()._asdict()

#Function to get Disk Usage
def get_disk_usage():
        # Get disk usage information for the root partition ('/')
    return psutil.disk_usage('/')._asdict() 
       
# Function to get temperature data from sensors command
def get_temperature_data():
    try:
        result = subprocess.run(['sensors'], stdout=subprocess.PIPE, text=True)
        temp_data = result.stdout
        temp_data = re.findall(r'(\S+):\s+\+?([\d\.]+)°C', temp_data)
        formatted_temp_data = {}
        for sensor, temp in temp_data:
            formatted_temp_data[sensor] = float(temp)
        return formatted_temp_data
    except Exception as e:
        print(f"Error reading temperature data: {e}")
        return {}

# Alternative function to get battery data using upower command
def get_battery_data():
    try:
        global x
        #refresh_command1 = "busctl call org.freedesktop.UPower /org/freedesktop/UPower/devices/battery_BAT0 org.freedesktop.UPower.Device Refresh"
        refresh_command = "sudo udevadm trigger /sys/class/power_supply/BAT0"
        subprocess.run(refresh_command, shell=True, check=True)

        result = subprocess.run(['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'], stdout=subprocess.PIPE, text=True)
        battery_data = result.stdout
        percent = re.search(r'percentage:\s+(\d+)%', battery_data)
        secsleft = re.search(r'time to empty:\s+(\d+.\d+) hours', battery_data)
        minsleft = re.search(r'time to full:\s+(\d+.\d+) ', battery_data)
        if re.search(r'time to full:\s+(\d+.\d+) minutes', battery_data) :
            x=0
        elif re.search(r'time to full:\s+(\d+.\d+) hours', battery_data) :
            x=1
        elif re.search(r'time to empty:\s+(\d+.\d+) minutes', battery_data) :
            x=2
        elif re.search(r'time to empty:\s+(\d+.\d+) hours', battery_data) :
            x=3    
              
        voltage = re.search(r'voltage:\s+(\d+\.\d+) V', battery_data)
        state = re.search(r'state:\s+(\w+)', battery_data)
        energy = re.search(r'energy:\s+(\d+\.\d+) Wh', battery_data)
        energy_rate = re.search(r'energy-rate:\s+(\d+\.\d+) W', battery_data)

        percent = int(percent.group(1)) if percent else None
        secsleft = float(secsleft.group(1)) if secsleft else None
        minsleft = float(minsleft.group(1)) if minsleft else None
        voltage = float(voltage.group(1)) if voltage else None
        status = state.group(1) if state else None
        energy = float(energy.group(1)) if energy else None
        energy_rate = float(energy_rate.group(1)) if energy_rate else None

        return {'percent': percent, 'secsleft': secsleft,'minsleft': minsleft, 'voltage': voltage, 'status': status, 'energy': energy,
            'energy_rate': energy_rate}
    except Exception as e:
        print(f"Error reading battery data: {e}")
        return {'percent': None, 'secsleft': None,'minsleft': None, 'voltage': None, 'status': None, 'energy': None,
            'energy_rate': None}

# Function to get NIC card power consumption (wlp2s0 interface)
def get_nic_power_consumption():
    try:
        interface = get_wifi_interface()
        net_io1 = psutil.net_io_counters(pernic=True)

        if interface in net_io1:
            stats1 = net_io1[interface]
            bytes_received1 = int(stats1.bytes_recv)
            bytes_transmitted1 = int(stats1.bytes_sent)
            
            time.sleep(1)
            
            net_io2 = psutil.net_io_counters(pernic=True)
            stats2 = net_io2[interface]
            bytes_received2 = int(stats2.bytes_recv)
            bytes_transmitted2 = int(stats2.bytes_sent)
            
            bytes_rec_diff = bytes_received2 - bytes_received1
            bytes_trans_diff = bytes_transmitted2- bytes_transmitted1
            
            # Calculate power per byte based on NIC speed
            tx_power = (1003 * 8 * bytes_rec_diff) / (1 * 1000 * 1000)  # 1Mbps transmission consuming 1.3W power
            rx_power = (1000 * 8 * bytes_trans_diff) / (1 * 1000 * 1000)  # 1Mbps receiving consuming 1W power
            
            nic_power = tx_power + rx_power
            return nic_power
        else:
            print(f"Interface {interface} not found.")
            return 0
    except Exception as e:
        print(f"Error reading NIC data transfer: {e}")
        return 0

#Function to get packet info
def get_packet_info():
    try:
        interface = get_wifi_interface()
        net_io = psutil.net_io_counters(pernic=True)
        
        if interface in net_io:
            stats = net_io[interface]
            packets_received = int(stats.packets_recv)
            packets_transmitted = int(stats.packets_sent)
            return packets_received, packets_transmitted
        else:
            print(f"Interface {interface} not found.")
            return 0, 0
    except Exception as e:
        print(f"Error reading NIC packet information: {e}")
        return 0, 0

# Function to get system load
def get_system_load():
    return psutil.getloadavg()[0]*100/ psutil.cpu_count() # Get the 1-minute load average

# Function to get GPU metrics (vddgfx, PPT, edge) from sensors command
def get_gpu_metrics():
    try:
        result = subprocess.run(['sensors'], stdout=subprocess.PIPE, text=True)
        gpu_data = result.stdout

        vddgfx = re.search(r'vddgfx:\s+\+?([\d\.]+)', gpu_data)
        ppt = re.search(r'PPT:\s+([\d\.]+)', gpu_data)
        edge = re.search(r'edge:\s+\+?([\d\.]+)°C', gpu_data)

        vddgfx_value = float(vddgfx.group(1)) if vddgfx else None
        ppt_value = float(ppt.group(1)) if ppt else None
        edge_value = float(edge.group(1)) if edge else None

        return {'vddgfx': vddgfx_value, 'ppt': ppt_value, 'edge': edge_value}

    except Exception as e:
        print(f"Error reading GPU metrics: {e}")
        return {'vddgfx': None, 'ppt': None, 'edge': None}

def get_fan_rpm():
    try:
        # Get fan speed information
        result = subprocess.run(['sensors'], stdout=subprocess.PIPE, text=True)
        fan_data = result.stdout

        fanrpm = re.search(r'Fan:\s+\+?([\d\.]+)', fan_data)
        
        fanrpm_value = int(fanrpm.group(1)) if fanrpm else None
        
        return fanrpm_value

    except Exception as e:
        print(f"Error reading GPU metrics: {e}")
        return 0


# Function to update the plot based on user selection
def update_plot(metric, window, fig, ax):
    current_time = datetime.now().strftime('%H:%M:%S')
    system_info = get_system_info()
    if metric == 'cpu_usage':
        cpu_stats = get_cpu_stats()

        ax.clear()

        # Plot total CPU usage as text at the top of the graph
        ax.text(0.5, 0.95, f'Total CPU Usage: {cpu_stats["total_usage"]}%', horizontalalignment='center', transform=ax.transAxes, fontsize=12)
        if cpu_stats["total_usage"] > 99 :   
            ax.text(0.5, 0.9, f'Thermal Design Power: {get_cpu_pkg_power_consumption()} W', horizontalalignment='center', transform=ax.transAxes, fontsize=12)
        else :
            tdp=0
        # Plot per-core CPU usage as individual bar graphs
        cores = range(len(cpu_stats['usage_per_core']))
        ax.bar(cores, cpu_stats['usage_per_core'], align='center')

        ax.set_xlabel('Core Number →', fontsize=14)
        ax.set_ylabel('CPU Utilization (%) →',fontsize=14)
        ax.set_title('CPU Usage Per Core', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks(cores)  
        ax.set_xticklabels([str(core) for core in cores])  
        ax.text(0.5, 1.1, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.grid(True)
        
        
    elif metric == 'cpu_cstates':
        c1, c2, c3 = get_cpu_cstates()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time']
        cpu_stats = get_cpu_stats()
        data = [c1, c2, c3]
        labels = ['C1', 'C2', 'C3']
        colors = ['maroon', 'cyan', 'orangered']

        ax.clear()
        ax.bar(labels, data, color=colors)
        ax.set_xlabel('C-States →', fontsize=14)
        ax.set_ylabel('Utilization (%) →', fontsize=14)
        if cpu_stats["total_usage"] > 99 :   
            ax.text(0.5, 1.1, f'Thermal Design Power: {get_cpu_pkg_power_consumption()} W', horizontalalignment='center', transform=ax.transAxes, fontsize=12)
        else :
            tdp=0
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor  :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.set_title('CPU C-State Utilization', fontsize =18)
        ax.tick_params(axis='x', labelsize=13)
        ax.tick_params(axis='y', labelsize=13)
        ax.grid(True)
        
    elif metric == 'cpu_core_power':
        cpu_core_power = get_cpu_core_power_consumption()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(cpu_core_power)
        cpu_stats = get_cpu_stats()
        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='lightcoral')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Power (W) →', fontsize=14)
        ax.set_title('CPU Core Power Consumption', fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        if cpu_stats["total_usage"] > 99 :   
            ax.text(0.5, 1.1, f'Thermal Design Power: {get_cpu_core_power_consumption()} W', horizontalalignment='center', transform=ax.transAxes, fontsize=12)
        else :
            tdp=0
        
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)

    elif metric == 'cpu_pkg_power':
        cpu_pkg_power = get_cpu_pkg_power_consumption()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(cpu_pkg_power)
        cpu_stats = get_cpu_stats()
        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='coral')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Power (W) →', fontsize=14)
        ax.set_title('CPU Package Power Consumption', fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        if cpu_stats["total_usage"] > 99 :   
            ax.text(0.5, 1.1, f'Thermal Design Power: {get_cpu_pkg_power_consumption()} W', horizontalalignment='center', transform=ax.transAxes, fontsize=12)
        else :
            tdp=0
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)


    elif metric == 'cpu_frequency':
        cpu_freq = get_cpu_frequency()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data']['current'].append(cpu_freq['current'])

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data']['current'], marker='o', linestyle='-', color='lightgreen')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Frequency (MHz) →', fontsize=14)
        ax.set_title('CPU Frequency (Current)',fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)

    elif metric == 'memory_usage':
        memory_stats = get_memory_stats()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time']
    
       # Extract memory data in GB
        total_gb = memory_stats['total'] / (1024 ** 3)
        used_gb = memory_stats['used'] / (1024 ** 3)
        cached_gb = memory_stats['cached'] / (1024 ** 3)
        available_gb = memory_stats['available'] / (1024 ** 3)
        free_gb = memory_stats['free'] / (1024 ** 3)

        data = [total_gb, used_gb, cached_gb, available_gb, free_gb]
        labels = ['Total', 'Used', 'Cache', 'Available', 'Free']
        colors = ['lightblue', 'lightgreen', 'violet', 'lightcoral', 'lightgrey']

        ax.clear()
        ax.bar(labels, data, color=colors)
        ax.set_xlabel('Memory Type →', fontsize=14)
        ax.set_ylabel('Memory (GB) →', fontsize=14)
        ax.set_title('RAM Memory Usage', fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.grid(True)
        
        
    elif metric == 'disk_usage':
        disk_stats = get_disk_usage()
    
     # Append data only if current time is different from the last recorded time
        if len(data_series['disk_usage']['time']) == 0 or current_time != data_series['disk_usage']['time'][-1]:
            data_series[metric]['time']
            
        total_gb1 = disk_stats['total'] / (1024 ** 3)
        used_gb1 = disk_stats['used'] / (1024 ** 3)
        free_gb1 = disk_stats['free'] / (1024 ** 3)
        
        data = [total_gb1, used_gb1, free_gb1]
        labels = ['Total', 'Used', 'Free']
        colors = ["#0000CD", 'limegreen', 'orange']

        ax.clear()
        ax.bar(labels, data, color=colors)
        ax.set_xlabel('Memory Type →', fontsize=14)
        ax.set_ylabel('Memory (GB) →', fontsize=14)
        ax.set_title('Disk Memory Usage', fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.grid(True)
        
        
    elif metric == 'temperature':
        temp_data = get_temperature_data()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        for sensor, temp in temp_data.items():
            if sensor not in data_series[metric]['data']:
                data_series[metric]['data'][sensor] = []
            data_series[metric]['data'][sensor].append(temp)

        ax.clear()
        for sensor, temp_series in data_series[metric]['data'].items():
            ax.plot(data_series[metric]['time'][-len(temp_series):], temp_series, marker='o', linestyle='-', label=sensor)
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Temperature (°C) →', fontsize=14)
        ax.set_title('Temperature Data', fontsize=18)
        #ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        #ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.legend()
        ax.grid(True)

    elif metric == 'battery_percent':
        battery_data = get_battery_data()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(battery_data['percent'])

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='gold')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Battery Percentage (%) →', fontsize=14)
        ax.set_title('Battery Percentage', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)
        #ax.text(0.5, 1.05, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.95, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        # Display battery state as 'Charging' if status is 'charging'
        if battery_data['status'] == 'charging':
            ax.text(0.5, 0.9, 'State: Charging', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='green')
        elif battery_data['status'] is not None:
            ax.text(0.5, 0.9, f'State: {battery_data["status"].capitalize()}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='red')

    elif metric == 'battery_voltage':
        battery_data = get_battery_data()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(battery_data['voltage'])

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='gold')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Battery Voltage (V) →', fontsize=14)
        ax.set_title('Battery Voltage', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)
        #ax.text(0.5, 1.05, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.95, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        # Display battery state as 'Charging' if status is 'charging'
        if battery_data['status'] == 'charging':
            ax.text(0.5, 0.9, 'State: Charging', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='green')
        elif battery_data['status'] is not None:
            ax.text(0.5, 0.9, f'State: {battery_data["status"].capitalize()}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='red')
        
    elif metric == 'battery_secs_left':
        battery_data = get_battery_data()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
            if battery_data['status'] == 'charging':
                if x ==0:
                    data_series[metric]['data'].append(battery_data['minsleft'])
                    ylabel = "Time to Full Charge (mins) →"
                elif x ==1:
                    data_series[metric]['data'].append(battery_data['minsleft'])
                    ylabel = "Time to Full Charge (hours) →"
                elif x ==2:
                    data_series[metric]['data'].append(battery_data['secsleft'])
                    ylabel = "Time to Empty (mins) →"  
            else:
                ylabel = "Time to Empty (hours) →"
                data_series[metric]['data'].append(battery_data['secsleft'])
        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='gold')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.set_title('Battery Time to Empty/ Full', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)
        #ax.text(0.5, 1.05, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.95, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        # Display battery state as 'Charging' if status is 'charging'
        if battery_data['status'] == 'charging':
            ax.text(0.5, 0.9, 'State: Charging', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='green')
        else:
            ax.text(0.5, 0.9, f'State: {battery_data["status"].capitalize()}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='red')
            
    elif metric == 'battery_energy':
        battery_data = get_battery_data()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(battery_data['energy'])

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='blue')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Energy (Wh) →', fontsize=14)
        ax.set_title('Battery Energy Present', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)
        #ax.text(0.5, 1.05, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='black')
        ax.text(0.5, 0.95, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        # Display battery state as 'Charging' if status is 'charging'
        if battery_data['status'] == 'charging':
            ax.text(0.5, 0.9, 'State: Charging', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='green')
        elif battery_data['status'] is not None:
            ax.text(0.5, 0.9, f'State: {battery_data["status"].capitalize()}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='red')

    elif metric == 'battery_energy_rate':
        battery_data = get_battery_data()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(battery_data['energy_rate'])

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='red')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Energy Rate (W) →', fontsize=14)
        ax.set_title('Battery Energy Rate', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)
        #ax.text(0.5, 1.05, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='black')
        ax.text(0.5, 0.95, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        # Display battery state as 'Charging' if status is 'charging'
        if battery_data['status'] == 'charging':
            ax.text(0.5, 0.9, 'State: Charging', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='green')
        elif battery_data['status'] is not None:
            ax.text(0.5, 0.9, f'State: {battery_data["status"].capitalize()}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='red')
    
    elif metric == 'nic_power':
        nic_power = get_nic_power_consumption()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(nic_power)

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='orange')
        ax.set_xlabel('Time →' , fontsize=14)
        ax.set_ylabel('Power (mW) →', fontsize=14)
        ax.set_title('NIC Power Consumption', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        interface = get_wifi_interface()
        ax.text(0.5, 0.9, f'Wi-Fi Interface: {interface} ', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='red')
        ax.grid(True)
        #ax.text(0.5, 1.05, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='black')
        ax.text(0.5, 0.95, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')

    elif metric == 'packet_info':
    # Example usage of NIC packet plotting
        packets_received, packets_transmitted = get_packet_info()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data']['received'].append(packets_received)
        data_series[metric]['data']['transmitted'].append(packets_transmitted)

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data']['received'], marker='o', linestyle='-', color='blue', label='Packets Received')
        ax.plot(data_series[metric]['time'], data_series[metric]['data']['transmitted'], marker='o', linestyle='-', color='red', label='Packets Transmitted')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Number of Packets →', fontsize=14)
        ax.set_title('NIC Packets (Received and Transmitted)', fontsize=18)
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13) 
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)
        #ax.text(0.5, 1.05, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='black')
        ax.text(0.5,0.95, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=14, color='black')
        interface = get_wifi_interface()
        ax.text(0.5, 0.9, f'Wi-Fi Interface: {interface} ', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='red')
        ax.legend()

    elif metric == 'system_load':
        system_load = get_system_load()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(system_load)

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='lightpink')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Load Average (%)  →', fontsize=14)
        ax.set_title('System Load Average (1 min)', fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)

    elif metric == 'gpu_vddgfx':
        gpu_metrics = get_gpu_metrics()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
            data_series[metric]['data'].append(gpu_metrics['vddgfx'])
            if gpu_metrics['vddgfx'] < 10 : 
                    ylabel='Voltage (V) →'
            elif gpu_metrics['vddgfx'] > 10 :
                    ylabel='Voltage (mV) →'
        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='lightblue')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel(ylabel , fontsize=14)
        ax.set_title('GPU Supply Voltage',fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)

    elif metric == 'gpu_ppt':
        gpu_metrics = get_gpu_metrics()
        if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
            data_series[metric]['time'].append(current_time)
        data_series[metric]['data'].append(gpu_metrics['ppt'])

        ax.clear()
        ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='lightgreen')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Power (W) →', fontsize=14)
        ax.set_title('GPU Package Power Consumption',fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13)  
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.grid(True)

    elif metric == 'gpu_edge':
        gpu_metrics = get_gpu_metrics()
        if gpu_metrics['edge'] is not None:
            if len(data_series[metric]['time']) == 0 or current_time != data_series[metric]['time'][-1]:
                data_series[metric]['time'].append(current_time)
            data_series[metric]['data'].append(gpu_metrics['edge'])

            ax.clear()
            ax.plot(data_series[metric]['time'], data_series[metric]['data'], marker='o', linestyle='-', color='lightcoral')
            ax.set_xlabel('Time →', fontsize=14)
            ax.set_ylabel('Temperature on GPU die Edge (°C) →',fontsize=14)
            ax.set_title('GPU Temperature', fontsize=18)
            ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
            ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
            ax.tick_params(axis='x', labelsize=13) 
            ax.tick_params(axis='y', labelsize=13)  
            ax.grid(True)
            
    elif metric == 'fan_rpm':
        fan_speed = get_fan_rpm()
    
        if len(data_series['fan_rpm']['time']) == 0 or current_time != data_series['fan_rpm']['time'][-1]:
            data_series['fan_rpm']['time'].append(current_time)
        data_series['fan_rpm']['data'].append(fan_speed)
        
        ax.clear()
        ax.plot(data_series['fan_rpm']['time'], data_series['fan_rpm']['data'], marker='o', linestyle='-', color='purple', label='Fan RPM')
        ax.set_xlabel('Time →', fontsize=14)
        ax.set_ylabel('Fan RPM →', fontsize=14)
        ax.set_title('Fan RPM over Time', fontsize=18)
        ax.text(0.5, 0.95, f'Laptop Name :{system_info["laptop_name_model"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.text(0.5, 0.9, f'Processor :{system_info["processor_name"]}', horizontalalignment='center', transform=ax.transAxes, fontsize=12, color='black')
        ax.tick_params(axis='x', labelsize=13)  
        ax.tick_params(axis='y', labelsize=13) 
        ax.set_xticks(data_series['fan_rpm']['time'][::max(1, len(data_series['fan_rpm']['time']) // 10)])  
        ax.grid(True)
        ax.legend()           
           
# Set x-axis labels to show only the first and latest timestamps
    if len(data_series[metric]['time']) > 1:
        ax.set_xticks([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
        ax.set_xticklabels([data_series[metric]['time'][0], data_series[metric]['time'][-1]])
            
    fig.canvas.draw()
    window.after(1000, lambda: update_plot(metric, window, fig, ax))  # Update every second

# Function to create a new Toplevel window and plot
def create_new_window(metric, title):
    # Close the cpu_cstates window if it's open and the new metric is different
    if metric != 'cpu_cstates' and 'cpu_cstates' in windows:
        on_window_close('cpu_cstates')
        
    if metric in windows:
        # Bring the existing window to the front
        windows[metric].deiconify()
        windows[metric].lift()
        return
    window = tk.Toplevel(root)
    window.title(title)
    window.protocol("WM_DELETE_WINDOW", lambda: on_window_close(metric))
    window.lift()
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    windows[metric] = window
    update_plot(metric, window, fig, ax)
    # Bring all open windows to the front
    for win in windows.values():
        win.lift()
# function to handle window close event
def on_window_close(metric):
    if metric in windows:
        windows[metric].destroy()
        del windows[metric]

# function to refresh all plots
def refresh_plots():
    for metric in data_series.keys():
        if metric in windows and windows[metric].winfo_exists():
            fig, ax = plt.subplots(figsize=(10, 6))
            update_plot(metric, windows[metric], fig, ax)
            
def get_display_dimensions():
    try:
        # Run the xdpyinfo command and capture the output
        result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, check=True)
        output = result.stdout
        for line in output.split('\n'):
            if 'dimensions:' in line:
                dimensions = line.split()[1]
                return dimensions
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running xdpyinfo: {e}")
        return None

def start_docker_container(cpu_load, stress_duration):
    global docker_process
    cmd = f"docker run --rm -it stress-cpu {cpu_load} {stress_duration}"
    docker_process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)

# Function to stop the Docker container
def stop_docker_container():
    global docker_process
    if docker_process:
        # Use subprocess to send a docker stop command
        stop_cmd = "docker stop $(docker ps -q --filter ancestor=stress-cpu)"
        subprocess.run(stop_cmd, shell=True)
        docker_process = None
        
# Function to handle Docker container execution button click
def execute_docker():
    cpu_load = cpu_load_entry.get()
    stress_duration = stress_duration_entry.get()
    global docker_process
    docker_process = Process(target=start_docker_container, args=(cpu_load, stress_duration))
    docker_process.start()
        


# Main GUI setup
root = tk.Tk()
root.geometry(get_display_dimensions())  
root.title("MANTLE ©")
root.configure(bg = 'purple')
# Configure the grid layout for the root window
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)


banner_header = (
    " ███╗   ███╗ █████╗ ███╗   ██╗████████╗██╗     ███████╗ ©\n"
    " ████╗ ████║██╔══██╗████╗  ██║╚══██╔══╝██║     ██╔════╝ \n"
    " ██╔████╔██║███████║██╔██╗ ██║   ██║   ██║     █████╗   \n"
    " ██║╚██╔╝██║██╔══██║██║╚██╗██║   ██║   ██║     ██╔══╝   \n"
    " ██║ ╚═╝ ██║██║  ██║██║ ╚████║   ██║   ███████╗███████╗ \n"
    " ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝ \n")
banner_body = (
    " MANTLE © is a comprehensive Power Management tool designed to monitor and display various system metrics "
    " and manage telemetry data in real-time. It provides detailed insights into the overall system statistics "
    " and Power Consumption of various components in system. It can capture your plots, switch mode , and much more\n\n"
    " Features:\n"
    " ✱ CPU Usage and Power Consumption of Core and Package\n"
    " ✱ RAM and Disk Memory usage \n"
    " ✱ Temperature Monitoring and Power Mode Switching \n"
    " ✱ Battery statistics and NIC power consumption\n"
    " ✱ GPU metrics tracking\n\n"
    " Use the Metrics Menu on the left to access and navigate through different metrics and visualize them with real- "
    " time graphs. Customize the appearance with light/dark mode through the Menu bar and explore the intricacies "
    " of your System !"
)

# Configure the grid layout for the root window
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Create a frame to contain the buttons
button_frame = tk.Frame(root, bg='purple',width=300, height=1080, borderwidth=5, relief=tk.RIDGE)  # Color added for clarity
button_frame.pack_propagate(False)
button_frame.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W, padx=10, pady=5)  # Align the frame to the left

# Create a frame for Docker container inputs with a black background
docker_frame = tk.Frame(root, width=400, height=1080, bg='purple', borderwidth=5, relief=tk.RIDGE)  # Half the width of the root window
docker_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its children
docker_frame.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W, padx=10, pady=5)

# Configure the grid layout for docker_frame to center its contents
docker_frame.grid_columnconfigure(0, weight=1)
docker_frame.grid_rowconfigure(0, weight=1)
docker_frame.grid_rowconfigure(1, weight=1)

# Create an upper frame to hold the text display
text_frame = tk.Frame(docker_frame, bg='purple', padx=10, pady=10, borderwidth=3, relief=tk.RIDGE)
text_frame.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

# Add a Text widget for displaying the banner
display_text = tk.Text(text_frame, background='purple', foreground='white', wrap=tk.WORD, height=17, pady=5)
display_text.grid(row=1, column=0, columnspan=2, sticky=tk.W)
display_text.insert(tk.END, banner_header, ('header',))
display_text.insert(tk.END, banner_body, ('body',))
display_text.tag_configure('header', font=('Courier', 16, 'bold'))
display_text.tag_configure('body', font=('MS Serif', 14))
display_text.tag_configure("center")
display_text.tag_add("center", 1.0, "end")
display_text.config(state=tk.DISABLED)
display_text.pack(expand=True, fill=tk.BOTH)

inner_frame = tk.Frame(docker_frame, bg='purple', padx=10, pady=10, borderwidth=1, relief=tk.RIDGE)
inner_frame.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

# header for the inner frame
inner_header = tk.Label(inner_frame, text="System Loading - This enables a Real-Time Simulation of loading the CPU cores, with a \n specified amount in percentage, for a fixed amount of time using a Docker Container\n" , background='purple', foreground='white', font=('MS Serif','16','bold'), width = 20)
inner_header.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.N+tk.S+tk.E, pady=(0, 10))  # Align left

inner_frame.grid_columnconfigure(0, weight=1)
inner_frame.grid_columnconfigure(1, weight=1)
inner_frame.grid_rowconfigure(0, weight=1)
inner_frame.grid_rowconfigure(1, weight=1)
inner_frame.grid_rowconfigure(2, weight=1)
inner_frame.grid_rowconfigure(3, weight=1)
inner_frame.grid_rowconfigure(4, weight=1)

# CPU Load input
cpu_label = tk.Label(inner_frame, text="CPU Load (%)", background='purple', foreground='white', font=('MS Serif', 12, 'bold'))
cpu_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=2)
cpu_load_entry = ttk.Entry(inner_frame, width=10)
cpu_load_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

# Stress Duration input
stress_label = tk.Label(inner_frame, text="Stress Duration (s)", background='purple', foreground='white', font=('MS Serif', 12, 'bold'))
stress_label.grid(row=2, column=0, sticky=tk.E, padx=5, pady=3.5)
stress_duration_entry = ttk.Entry(inner_frame, width=10)
stress_duration_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3.5)

# Docker Start button
start_button = tk.Button(inner_frame, text="Start Docker Container", bg="#1C6BA0", foreground='black', font=('MS Serif', 12, 'bold'), command=execute_docker)
start_button.grid(row=4, column=0, pady=(10, 0), padx=5, columnspan=1)

# Docker Stop button
stop_button = tk.Button(inner_frame, text="Stop Docker Container", bg="#1C6BA0", foreground='black', font=('MS Serif', 12, 'bold'), command=stop_docker_container)
stop_button.grid(row=4, column=1, pady=(10, 0), padx=5, columnspan=1)

menu_bar = tk.Menu(root)
menu_bar.config(bg='purple')
# File Menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.config(bg='purple', font=('MS Serif', 12, 'bold'))
file_menu.add_command(label="Refresh", command=lambda: refresh_plots())
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu, font=('MS Serif', 12, 'bold'))
    
# View Menu
view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.config(bg='purple', font=('MS Serif', 12, 'bold'))
view_menu.add_command(label="Dark Mode", command=lambda: switch_mode('dark'))
view_menu.add_command(label="Default Mode", command=lambda: switch_mode('default'))
menu_bar.add_cascade(label="View", menu=view_menu, font=('MS Serif', 12, 'bold'))
    
# Help Menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.config(bg='purple', font=('MS Serif', 12, 'bold'))
help_menu.add_command(label="About", command=lambda: show_about())
menu_bar.add_cascade(label="Help", menu=help_menu, font=('MS Serif', 12, 'bold'))
    
root.config(menu=menu_bar)

# function to show about dialog
def resize_image(image_path, width, height):
    # Open the image file
    image_path = "pngimg.com - intel_PNG2.png"
    original_image = Image.open(image_path)
    # Resize the image with the aspect ratio preserved
    resized_image = original_image.resize((width, height), Image.LANCZOS)
    # Convert resized image to PhotoImage
    resized_image_tk = ImageTk.PhotoImage(resized_image)
    return resized_image_tk

def show_about():
    about_window = tk.Toplevel()
    about_window.geometry=(get_display_dimensions())
    about_window.config(bg='grey20')
    about_window.title("About")

    # Load and resize the image
    image_path = "pngimg.com - intel_PNG2.png"  
    resized_logo = resize_image(image_path, 550,220)  
    logo_label = tk.Label(about_window, image=resized_logo, bg='grey20')
    logo_label.grid(row=0, column=0, padx=20, pady=20,sticky='nsew')
    
    text = ( 
    " \t\t\t\t\t\t    MANTLE ©\n"
    " \t\t\t\t\t\tVersion 1.4.7_3 \n\n"
    " MANTLE is a comprehensive Power Management tool designed to monitor and display various system metricsand manage telemetry \n"
    " data in real-time.In the era of 5G and edge computing, the deployment of devices across different locations,has increased, leading to\n"
    " higher power consumption. To adress this issue corporations and governments worldwide have initiated steps to achieve net-zero\n"
    " power consumption. Additionally, the price of electricity is increasing, making it crucial to understand the total power drawn \n"
    " by the system.\n"
    " The main objectives of this project include the following -\n\n"
    " 1. Researching and identifying open-source tools for power measurement.\n"
    " 2. Identifying and documenting the available knobs in a system to measure power.\n"
    " 3. Collect power telemetry data from CPU, memory, NIC, and TDP etc.\n"
    " 4. Measure and record system power utilization for CPU, NIC, and TDP based on the input parameter of system utilization percentage.\n\n"
    " To execute this python application in your Linux Systems, kindly follow the steps listed in our github repository -\n 'https://github.com/Takelite/Mantle_Intel-Unnati-2024/tree/main'\n\n"
    " This application has certain dependencies, which if not downloaded pose issues durin runtime, they are -\n"
    " 1. python3 - Install python on your workspace using 'sudo apt install python3'\n"
    " 2. pil - Python imaging library pillow, 'pip3 install Pillow'\n"
    " 3. pip - python package installer, install it using ''sudo apt install python3-pip'\n"
    " 4. psutil library - for system and process utilities, install using 'pip install psutil'\n"
    " 5. matplotlib library - for plotting graphs, install system wide using 'sudo apt install python3-matplotlib'\n"
    " 6 tkinter library - for creating the GUI, install using 'sudo apt-get install python3-tk'\n"
    " 7. turbostat tool - for extracting CPU data, install it using 'sudo apt install linux-tools-common' , it is included in this package\n"
    " 8. ""sensors"" command - for extracting Temperature information, install it using 'sudo apt-get install lm-sensors'\n"
    " 9. ""upower"" command - for extracting Battery data, install it using 'sudo apt-get install upower'\n"
    " 10. ""powerprofilesctl"" command - for enabling different power modes, install it using 'sudo apt install power-profiles-daemon'\n"
    " 11. Docker is a platform for developing, shipping, and running applications inside lightweight, portable, self-sufficient containers. \n To install you can  refer to our github repository'\n"
    " Kindly install these dependencies if not done already, always use 'sudo apt update' before installing\n\n"
    " Developed under the Intel® Unnati Indsutrial Training Program 2024 by 'The Risc Takers' team of Aditya Minocha and Devansh Raut\n"
    " Contact Us : adityaminocha10@gmail.com | devansh.raut03@gmail.com"
    )

    text_label = tk.Label(about_window, text=text, bg='grey20', fg='white', font=('MS Serif', 12, 'bold'),justify=tk.LEFT)
    text_label.grid(row=0, column=1,padx=20, pady=20, sticky='nsew')

    tk.Button(about_window, text="Close", font=('MS Serif', 12, 'bold'), bg='silver', command=about_window.destroy, width = 15, height = 2).grid(row=1, columnspan=2, pady=10)

    about_window.image = resized_logo
    
# function to switch between dark and light mode
def switch_mode(mode):

    if mode == 'dark':
        plt.rcParams['axes.facecolor'] = "#696969"  # Light grey
        plt.rcParams['figure.facecolor'] = "#696969"  # Light grey
        display_text.config(state=tk.NORMAL)
        menu_bar.config(bg='black', fg='white', activebackground='black', activeforeground='white')
        root.config(bg='black' if mode == 'dark' else 'white')
        file_menu.config(bg='black')
        view_menu.config(bg='black')
        help_menu.config(bg='black')
        button_frame.config(bg ='black')
        inner_frame.config(bg ='black')
        text_frame.config(bg ='black')
        docker_frame.config(bg ='black')
        inner_frame.config(bg ='black')
        inner_header.config(bg ='black')
        display_text.config(bg ='black')                
        cpu_label.config(background = 'gray10', foreground = 'white')
        stress_label.config(background = 'gray10', foreground = 'white')
        for menu in [file_menu, view_menu, help_menu]:
            menu.config(bg='black', fg='white', activebackground='black', activeforeground='white')
            for item in menu.winfo_children():
                item.config(bg='black', fg='white', activebackground='black', activeforeground='white')
                
    else:
        plt.rcParams['axes.facecolor'] = 'white'  # Purple
        plt.rcParams['figure.facecolor'] = 'white'  # Purple
        display_text.config(state=tk.NORMAL)
        menu_bar.config(bg='purple', fg='black', activebackground='white', activeforeground='black')
        root.config(bg='purple' if mode == 'dark' else 'white')
        file_menu.config(bg='purple')
        view_menu.config(bg='purple')
        help_menu.config(bg='purple')
        button_frame.config(bg='purple')
        docker_frame.config(bg='purple')
        inner_frame.config(bg ='purple')
        text_frame.config(bg ='purple')
        inner_header.config(bg ='purple')
        #text_header.config(bg ='purple')
        inner_frame.config(bg='purple')
        display_text.config(bg ='purple') 
        cpu_label.config(background = 'purple', foreground = 'white')
        stress_label.config(background = 'purple', foreground ='white')
        for menu in [file_menu, view_menu, help_menu]:
            menu.config(bg='purple', fg='black', activebackground='purple', activeforeground='black')
            for item in menu.winfo_children():
                item.config(bg='purple', fg='black', activebackground='purple', activeforeground='black')

    # Update the style of the root window
    root.config(bg='black' if mode == 'dark' else 'purple')
    display_text.config(state=tk.DISABLED)

    # Close all existing graph windows
    for window in windows.values():
        window.destroy()
    windows.clear()
            


# Exit button function
def exit_program():
    for window in windows.values():
        window.destroy()
    windows.clear()
    root.quit()

def pwr_saving():
    try:
        # Execute the command to set the power profile to power saving
        subprocess.run(['powerprofilesctl', 'set', 'power-saver'], check=True)
        messagebox.showinfo("Success !", "Power profile set to Power-Saving Mode.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to set power profile: {e}")
    except FileNotFoundError:
        messagebox.showerror("Error", "powerprofilesctl is not installed or not found in PATH.")

def pwr_balanced():
    try:
        # Execute the command to set the power profile to balanced
        subprocess.run(['powerprofilesctl', 'set', 'balanced'], check=True)
        messagebox.showinfo("Success !", "Power profile set to Balanced Mode.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to set power profile: {e}")
    except FileNotFoundError:
        messagebox.showerror("Error", "powerprofilesctl is not installed or not found in PATH.")
def pwr_performance():
    try:
        # Execute the command to set the power profile to performance
        subprocess.run(['powerprofilesctl', 'set', 'performance'], check=True)
        messagebox.showinfo("Success !", "Power profile set to Performance Mode.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to set power profile: {e}")
    except FileNotFoundError:
        messagebox.showerror("Error", "powerprofilesctl is not installed or not found in PATH.")
def get_screen_dpi():
    try:
        # Run xdpyinfo command and capture output
        result = subprocess.run(['xdpyinfo'], stdout=subprocess.PIPE, text=True)
        
        # Extract DPI value from xdpyinfo output
        for line in result.stdout.splitlines():
            if 'resolution' in line:
                dpi_str = line.split()[1]  # Extract the DPI value
                dpi_value = int(dpi_str.split('x')[0])  # Extract the horizontal DPI value
                return dpi_value
    except Exception as e:
        print(f"Error fetching DPI: {e}")
        return None        
# Function to create buttons 
def create_button(text, metric, title):

    button = tk.Button(button_frame, text=text, width=20, height=1, pady=3.5, command=lambda m=metric, t=title: create_new_window(m, t), bg="#1C6BA0", fg='black', font=('MS Serif', 12, 'bold'))
    button.pack(fill=tk.X, padx=3, pady=3)
   
# Create buttons for different metrics with improved styling
buttons = [
    ('CPU C-States', 'cpu_cstates', 'CPU C-States'),
    ('CPU Usage', 'cpu_usage', 'CPU Usage'),
    ('CPU Core Power', 'cpu_core_power', 'CPU Core Power Consumption'),
    ('CPU Package Power', 'cpu_pkg_power', 'CPU Package Power Consumption'),
    ('CPU Frequency', 'cpu_frequency', 'CPU Frequency'),
    ('RAM Memory Usage', 'memory_usage', 'RAM Memory Usage'),
    ('Disk Memory Usage', 'disk_usage' , 'Disk Memory Usage'),
    ('Temperature Sensors', 'temperature', 'Temperature Data'),
    ('Battery Percentage', 'battery_percent', 'Battery Percentage'),
    ('Battery Voltage', 'battery_voltage', 'Battery Voltage'),
    ('Battery Time to Empty', 'battery_secs_left', 'Battery Time to Empty'),
    ('Battery Energy', 'battery_energy', 'Battery Energy Present'),
    ('Battery Energy Consumption Rate ', 'battery_energy_rate', 'Battery Energy Rate'), 
    ('NIC Power', 'nic_power', 'NIC Power Consumption'),
    ('Packets Information' , 'packet_info' , ' NIC Packets (Received and Transmitted'),
    ('System Load Average', 'system_load', 'System Load Average (1 min)'),
    ('GPU Voltage', 'gpu_vddgfx', 'GPU VDDGFX Voltage'),
    ('GPU Package Power Tracking', 'gpu_ppt', 'GPU PPT'),
    ('GPU Temperature', 'gpu_edge', 'GPU Temperature'),
    ('Processor Fan RPM', 'fan_rpm' , 'Fan RPM over Time')
]

for button_text, metric_name, window_title in buttons:
    create_button(button_text, metric_name, window_title)

# Create exit button
exit_button = tk.Button(button_frame, text='Exit', width=20, pady=2.5, command=exit_program, bg='red', fg='white', font=('MS Serif', 12, 'bold'))
exit_button.pack(fill=tk.X, padx=3, pady=2)

pwrsave_button = tk.Button(button_frame, text='Power Saving Mode',width=23, height=2, padx=12, pady=2, command=pwr_saving, bg="#228B22", fg='black', font=('MS Serif', 12, 'bold'))
pwrsave_button.pack(side=tk.LEFT, padx=3,pady=2)

balance_button= tk.Button(button_frame, text='Balanced Mode', width=23, height=2, padx=12, pady=2, command=pwr_balanced, bg='silver', fg='black', font=('MS Serif', 12, 'bold'))
balance_button.pack(side=tk.LEFT, padx=3,pady=2)

perf_button= tk.Button(button_frame, text='Performance Mode', width=23, height=2, padx=12,pady=2, command=pwr_performance, bg="#CB6D51", fg='black', font=('MS Serif', 12, 'bold'))
perf_button.pack(side=tk.LEFT, padx=3,pady=2)


root.mainloop()

