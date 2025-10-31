import subprocess

# Define the rclone mount command
rclone_command = ["rclone", "mount", "GoogleDrive:", "/home/hari/Desktop/GoogleDrive/"]

# Run the rclone command using subprocess
try:
    subprocess.run(rclone_command, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
