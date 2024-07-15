[![Python](https://img.shields.io/badge/Python-%FF0000FF.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-%2300D8FF.svg?style=flat&logo=Docker&logoColor=white)](https://www.docker.com/)

# Mantle©: A comprehensive Power Management tool designed to monitor and display various system metrics and manage telemetry data in real-time ⚡🔋
## PS01: Power Manager Telemetry


In the era of 5G and edge computing, the deployment of devices across different locations,has increased, leading to higher power consumption. To adress this issue corporations and governments worldwide have initiated steps to achieve net-zero power consumption. Additionally, the price of electricity is increasing, making it crucial to understand the total power drawn by the system.  

The main objectives of this project include the following -  
    1. Researching and identifying open-source tools for power measurement.  
    2. Identifying and documenting the available knobs in a system to measure power.  
    3. Collect power telemetry data from CPU, memory, NIC, and TDP etc.  
    4. Measure and record system power utilization for CPU, NIC, and TDP based on the input parameter of system utilization percentage.  

## Demonstration of the Project

[Screencast from 2024-07-14 04-22-54.webm](https://github.com/user-attachments/assets/e010fca8-a9d3-4a9c-9f50-9039a4b36d85)

## Features of Mantle
  
### 1. CPU Metrics:
Mantle© provides real-time monitoring of CPU utilization. It displays the percentage of CPU usage for each individual core, allowing users to see which cores are under heavy load and which are idle. This helps in understanding the distribution of processing tasks across the CPU. C-states (idle states) are various levels of CPU idle modes where parts of the CPU can be powered down to save energy. Our GUI visualizes these states, showing the percentage of time the CPU spends in each C-state.  

**Power Consumption:** The tool also measures the power consumption of both individual cores and the entire CPU package (CPU Cores,Cache Memory,Memory Controller,IGP,IHS, etc). This includes tracking how much power each core is using and the overall power usage of the CPU package, giving insights into energy efficiency and potential areas for optimization.   
  
**Thermal Design Power:** of AMD Ryzen 5 5500U is theoretically 15W which is validated by the TDP Value provided by Mantle's plot which is around 14.7W at 100% CPU load.
  
![CPU Metrics](Images/cpu.png)
<div align="center">
 CPU Metric Plots
</div>                                   
  
### 2. RAM and Disk Memory Usage:
Mantle© monitors the system's RAM usage, displaying the amount of memory currently in use versus available memory. This helps in identifying memory-hungry applications and potential memory bottlenecks.  
  
**Disk Usage:** The tool tracks disk usage statistics, showing the amount of disk space used and available. It provides insights into disk performance and storage capacity, helping users manage their data storage more effectively.  

![Memory Metrics](Images/memory.png)
 <div align="center">
 Memory Usage Plots
</div>  
  
### 3. Temperature Monitoring and Power Mode Switching:
Mantle© tracks the temperature of various system components, including the CPU, GPU, and other critical hardware. It displays real-time temperature readings to help users ensure their system is operating within safe thermal limits.  
  
**Power Mode Switching:** The tool allows users to switch between different power modes, such as performance mode, balanced mode, and power-saving mode. This enables users to optimize their system's power consumption based on their current needs, whether they require maximum performance or extended battery life. 
When the CPU is in a relatively idle state (<10% CPU Utilisation), the different power modes consume the following amount of power-  
  - Power Saving: ~6.2W  
  - Balanced: ~7.1W  
  - Performance: ~8.6W  
  
![Power Metrics](Images/temp.png)
 <div align="center">
Temperature Plots
</div>  
  
### 4. Battery Statistics and NIC Power Consumption:
Mantle© provides detailed battery statistics, including battery percentage, time remaining, and power state (whether the system is plugged in or running on battery). This information helps users manage their battery usage and plan for recharging.
  
**NIC Power Consumption:** The tool monitors the power consumption of the Network Interface Card (NIC), which is crucial for understanding the energy impact of network activities. It helps in optimizing network usage to reduce power consumption.

![Battery Metrics](Images/battery.png)
<div align="center">
Battery Usage Plots
</div> 
  
### 5. GPU Metrics Tracking:
Mantle© tracks various GPU metrics, including power consumption, supply voltage and temperature. This provides insights into the performance and power efficiency of the GPU, helping users optimize graphics-intensive tasks and manage thermal performance.  

![GPU Metrics](Images/gpu.png)
<div align="center">
 GPU Metric Plots
</div>  

<BR>  
These features collectively provide a comprehensive view of system performance and power consumption, enabling users to monitor, manage, and optimize their system's efficiency and longevity effectively.

## Usage Of Docker
 Docker is a platform for developing, shipping, and running applications inside lightweight, portable, self-sufficient <img src="https://github.com/user-attachments/assets/6b8e1cdd-2373-4918-86ab-17667d19fe18" width="120" align="right">containers. Containers include everything needed to run an application: the code, runtime, libraries, environment variables, and system tools. 
    Using Docker to containerize your Python GUI application ensures a consistent, portable, and isolated environment. This approach helps mitigate dependency conflicts and eases deployment across different systems. By creating a Dockerfile, building an image, and running a container, you encapsulate your application's environment, making it easier to manage and deploy. 

**Steps to Use Docker with Your GUI Application**  
  
**1. Creating a Dockerfile:** This file will describe the environment needed to run within the GUI application.  
**2. Build the Docker Image:** Using the Dockerfile, build a Docker image that contains the application and its dependencies.  
**3. Run the Container:** Start a container from your image which includes input parameters like percentage CPU Loading and Duration to run the container. The Start button on the GUI will execute the Docker container and stress the CPU based on the input parameters, the stop button can be used to terminate the container before completing its duration
    
## Steps To Install Mantle

Mantle has been designed using Ubuntu 22.04, follow the steps listed below to install Mantle on your system.
  
**1. Install All System Dependencies:**

  - Open the *install dependencies* folder in this github repository and download the *"install_dependencies.sh"* file, in your **current working directory**(For ex. Home). Once downloaded execute the following command in your terminal-
```shell
chmod +x install_dependencies.sh
```

  - Now, execute the *"install_dependencies.sh"* file using the following command-  
```shell
./install_dependencies.sh
```

Now your system dependencies are installed.  
  
**2. Install Docker:**

  - Open the *install docker* folder in this github repository and download the *"Step1-install_docker.sh"* file, in your **current working directory**(For ex. Home). Once downloaded execute the following command in your terminal-
```shell
chmod +x Step1-install_docker.sh
```

  - Now, execute the *"Step1-install_docker.sh"* file using the following command-  
```shell
./Step1-install_docker.sh
```

Now Docker is installed, the next step is to create a Dockerfile. Use the command below to create the Dockerfile.    
```shell
vi Dockerfile
```  
  - Open the *install docker* folder in this github repository and copy the contents of *"Step2-Create Dockerfile"* file and paste it in the newly created Dockerfile using the vi editor. Press escape and use **:wq** to save and exit the vi editor.
  - Once done download *"Step3-install stress-cpu.sh"* from the same folder and **save it as "stress-cpu.sh"** , in your **current working directory**(For ex. Home). 
  - Once saved, execute the following command in your terminal-   
```shell
sudo docker build -t stress-cpu .
```

This step may take a few minutes, so kindly be patient while your system finishes building the Docker Image to run the container.   
  
**3. Download Mantle Application Code:**

  - If all previous dependencies and Docker have been successfully installed, you are now ready to download and execute Mantle's application on your system.
  - Open Mantle_GUI_code folder and download the *"mantle.py"* file in your, **current working directory**(For ex. Home). Execute Mantle using the following command-
```shell
sudo python3 mantle.py
```
**4. Explore Mantle:**

Mantle should now be up and running on your system. Use the Metrics Menu on the left to access and navigate through different metrics and visualize them with real-time graphs. You can use the Docker block to stress your system from 0-100%, for a specified duration. Customize the appearance with light/dark mode through the Menu bar and explore the intricacies of your System !
  
## Tools Used🛠️

Mantle utilises various python libraries and linux tools to present accurate real-time data through concise plots. This is made possible by the following open-source tools-
  
<img src="https://github.com/user-attachments/assets/7f1f890b-1aa0-4b1a-8144-4664ccd6e3fa" width="600" align="center">   
  
### psutil
  - `psutil` (Python System and Process Utilities) is a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network, sensors).
  - It provides APIs for CPU and memory usage, disk I/O, network information, and more.
  - Retrieves sensor data such as temperature and fan speed.
  - Allows management of system processes (e.g., killing processes, querying process details).

### tkinter
  - `tkinter` is the standard GUI toolkit for Python. 
  - Offers widgets (buttons, labels, entry fields, etc.) for building graphical interfaces.
  - It supports event-driven programming paradigm for handling user inputs and events.
  - Provides cross-platform support and is included with Python installations by default.

### turbostat
  - `turbostat` is a Linux command-line tool that reports processor frequency and power statistics.
  - Displays CPU frequency, utilization, temperature, and power metrics.
  - Provides insights into CPU power states (C-states) and Turbo Boost frequencies.
  - Useful for monitoring and optimizing CPU performance and power consumption.

### docker
  - `Docker` is a platform for developing, shipping, and running applications inside containers.
  - Uses containerization to package applications and their dependencies into isolated environments.
  - Provides consistent deployment across different environments (development, testing, production).
  - Facilitates scalability, portability, and efficiency by reducing overhead and ensuring application isolation.

### matplotlib
  - `matplotlib` is a comprehensive plotting library for Python.
  - Supports various types of plots: line plots, bar charts, histograms, scatter plots, etc.
  - Offers extensive customization options for plot aesthetics and labels.
  - Allows creation of static, animated, and interactive visualizations.

### sensors (lm-sensors) 
  - `lm-sensors` (Linux Hardware Monitoring) is a suite of tools and drivers for monitoring hardware sensors.
  - Supports monitoring temperature, voltage, and fan speeds of various hardware components.
  - Provides command-line utilities (`sensors`) for querying sensor data.
  - Helps in monitoring system health and identifying potential hardware issues.

### upower
  - `upower` is a daemon that provides information about power devices and manages power-related operations.
  - Retrieves battery status (charge level, capacity, etc.) and power adapter status.
  - Allows querying power management features such as suspend, hibernate, and power-off.
  - Provides notifications and events related to power changes and device connectivity.

## What It Does 
  
MANTLE © is a comprehensive Power Management tool designed to monitor and display various system metrics  and manage telemetry data in real-time. It provides detailed insights into the overall system statistics  and Power Consumption of various components in system. It can capture your plots, switch mode , and much more
   
 Features:  
 - CPU Usage and Power Consumption of Core and Package  
 - RAM and Disk Memory usage   
 - Temperature Monitoring and Power Mode Switching   
 - Battery statistics and NIC power consumption    
 - GPU metrics tracking  
<img src="https://github.com/Takelite/Mantle_Intel-Unnati-2024/blob/main/Images/gui_light2.png?raw=true" width="1200" align="center">  
Use the Metrics Menu on the left to access and navigate through different metrics and visualize them with real-time graphs. You can use the Docker block to stress your system from 0-100%, for a specified duration. Customize the appearance with light/dark mode through the Menu bar and explore the intricacies of your System !

## Transforming Power Visualisation
    
**Real-Time Monitoring:** Mantle allows users to see real-time data on CPU, GPU, memory, and network usage. This immediate feedback allows them to identify and address power-hungry applications and processes instantly. By monitoring temperatures, users can prevent overheating, ensuring their system operates within safe limits, thereby maintaining performance and preventing hardware damage.
  
**Efficiency Optimization:** Power Mode Switching enables users to switch between different power modes (performance, balanced, and power-saving) based on their current needs, optimizing power consumption for tasks like gaming, video editing, or simple browsing.
Detailed insights into CPU and memory usage help users allocate resources more efficiently, reducing unnecessary power consumption by closing or optimizing poorly performing applications.
  
**Battery Management:** By monitoring battery statistics, users can make informed decisions to extend their battery life, such as reducing screen brightness, disabling unused peripherals, and switching to power-saving modes.
  
**Long-Term Data Analysis:** By storing and analyzing historical data, users can identify long-term trends in power consumption and system performance, enabling them to make proactive adjustments to their setup.
Predictive Maintenance: Regular monitoring can help predict hardware failures before they occur, allowing for timely maintenance and upgrades, thus avoiding downtime and saving costs.
Sustainable Practices:

**Eco-Friendly Computing:** With detailed insights into power consumption, users can adopt more eco-friendly computing practices, such as reducing unnecessary power usage and opting for energy-efficient hardware.
Informed Upgrades: Users can make informed decisions when upgrading their hardware, choosing components that offer better performance-per-watt ratios, thereby reducing their overall carbon footprint.
Enterprise Applications:

**Scalable Monitoring:** For businesses, implementing MANTLE © across multiple systems can lead to significant energy savings at scale. Centralized monitoring and management of power consumption can reduce operational costs and enhance sustainability.

**Research and Development:** Developers and engineers can use the data provided by MANTLE © to innovate new technologies and solutions aimed at further reducing power consumption and enhancing system efficiency.
Integration with IoT: As the Internet of Things (IoT) evolves, integrating MANTLE © with IoT devices can lead to smarter, more efficient homes and workplaces, where devices communicate to optimize power usage collaboratively.
Educational Impact

**Cloud Integration:** Extend the GUI to collect and analyze power data from distributed systems and cloud environments.IoT Integration extends monitoring capabilities to IoT devices and sensors, allowing comprehensive power management across interconnected devices.

In summary, MANTLE © not only provides immediate benefits by optimizing current power usage but also equips users with the tools and insights needed for sustainable, efficient power management in the future. Its impact spans individual users, businesses, and the broader community, contributing to a more energy-efficient and environmentally conscious world.









