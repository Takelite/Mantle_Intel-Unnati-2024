# Steps To Install Mantle
  
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
