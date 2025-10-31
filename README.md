# VMS Setup Guide

## How to Set Up a Raspberry Pi for the First Time

### Downloading and Installing Raspberry Pi OS
1. Insert a **microSD card** or **reader** into your computer.  
2. Download and install the official **Raspberry Pi Imager**:  
   🔗 [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

---

## How to Install MySQL Database on Raspberry Pi

### Setting up MySQL on Raspberry Pi
```bash
sudo apt update
sudo apt upgrade
```

Install the MySQL server software (MariaDB):
```bash
sudo apt install mariadb-server
```

Secure the MySQL installation:
```bash
sudo mysql_secure_installation
```

Access the MySQL server:
```bash
sudo mysql -u root -p
```

---

## Creating a Database and Table

Example database name: **employees**

### Create Database
```sql
CREATE DATABASE employees;
```

### Create Table
```sql
CREATE TABLE live_video_record (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    File_name VARCHAR(255) NOT NULL,
    Start_time DATETIME NOT NULL,
    End_time DATETIME NOT NULL,
    File_extension VARCHAR(10) NOT NULL,
    Status VARCHAR(20) NOT NULL,
    upload_Status VARCHAR(20) NOT NULL
);
```

---

## Fix for MySQL Error

If you encounter:
```
pymysql.err.InternalError: (1698, "Access denied for user 'root'@'localhost'")
```
Run the following commands:
```sql
USE mysql;
SET PASSWORD FOR 'root'@'localhost' = PASSWORD('YOUR_ROOT_PASSWORD_HERE');
FLUSH PRIVILEGES;
QUIT;
```

---

## Creating a Systemd Service

### Create the Service File
```bash
sudo nano /etc/systemd/system/video_process.service
```

### Add the Following Configuration
```
[Unit]
Description=Video Processing Script Service
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/VMS/video_process.py
WorkingDirectory=/home/pi/VMS/
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Save the file using: **Ctrl + O**, **Enter**, then **Ctrl + X** to exit.

### Reload systemd and Start the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable video_process
sudo systemctl start video_process
sudo systemctl stop video_process
```

---

## Creating a Cron Job for Google Drive Upload

Open crontab:
```bash
crontab -e
```

Add the following lines:
```bash
@reboot /usr/bin/python3 /home/hari/VMS/servicedrive.py
0 * * * * /usr/bin/python3 /home/hari/VMS/servicedrive.py
```

Save the file using **Ctrl + O**, **Enter**, then **Ctrl + X**.

---
