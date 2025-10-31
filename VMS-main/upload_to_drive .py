import os
import pymysql
import requests
from queue import Queue
import shutil
import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
script_directory = os.path.dirname(os.path.abspath(__file__))
output_directory = 'Local_recordings'
output_directory_parts = os.path.split(script_directory)
output_directory = os.path.join(output_directory_parts[0], output_directory)
internet_check_url = 'http://www.google.com'
script_directory = os.path.dirname(os.path.abspath(__file__))
def create_mysql_connection():
    print("Creating MySQL connection...")
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='employees'
    )
def get_pending_videos(connection):
    print("Fetching pending videos...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM recordings WHERE upload_status = 'pending' AND Status = 'Completed' ORDER BY ID ASC")
            return cursor.fetchall()
    except Exception as e:
        print("Error fetching pending videos:", e)
        return []
def update_cloud_status(connection, video_id, status):
    print(f"Updating cloud status for video {video_id} to {status}...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE recordings SET upload_status = %s WHERE ID = %s", (status, video_id))
            connection.commit()
            print("Cloud status updated.")
    except Exception as e:
        print("Error updating cloud status:", e)
def get_folder_space_info(folder_path):
  
    stat = os.statvfs(folder_path)
    block_size = stat.f_frsize
    total_blocks = stat.f_blocks
    free_blocks = stat.f_bfree
    total_space_bytes = block_size * total_blocks
    free_space_bytes = block_size * free_blocks
    used_space_bytes = total_space_bytes - free_space_bytes
    total_space_gb = total_space_bytes / (1024 ** 3)  # Convert to GB
    total_space_mb = total_space_bytes / (1024 ** 2)  # Convert to MB
    free_space_gb = free_space_bytes / (1024 ** 3)  # Convert to GB
    free_space_mb = free_space_bytes / (1024 ** 2)  # Convert to MB
    used_space_gb = used_space_bytes / (1024 ** 3)  # Convert to GB
    used_space_mb = used_space_bytes / (1024 ** 2)  # Convert to MB
    return total_space_gb, total_space_mb, free_space_gb, free_space_mb, used_space_gb, used_space_mb
def upload_to_google_drive(file_path, file_name,video_id):
        print(f"Copying file {file_name} to /home/hari/Desktop/GoogleDrive/recorded_video...")
        try:
            connection = create_mysql_connection()
            destination_directory = '/home/hari/Desktop/GoogleDrive/recorded_video'
            destination_path = os.path.join(destination_directory, file_name)
            shutil.copy(file_path, destination_path)
            print(f"File {file_name} copied to {destination_directory}.")
            update_cloud_status(connection, video_id, 'Upload Complete')
            connection.close()
        except Exception as e:
            print("Error copying file:", e)
def send_email(subject, message, total_space_gb, used_space_gb):
      # Set the sender email and password and recipient email
    from_email_addr = "mailto:cosai.product2@gmail.com"
    from_email_pass = "pnabtsuflkrkupup"
    to_email_addr = "mailto:haran0594@gmail.com"
    # Create an EmailMessage object
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    # Create the HTML content for the email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            / Define your CSS styles here /
            body {{
                font-family: Arial, sans-serif;
                background-color: #F0F0F0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #007BFF;
            }}
            p {{
                color: #333333;
            }}
            img {{
                max-width: 100%;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <img src="https://i.ibb.co/Rbzxn8z/logo.jpg" alt="Logo" />
                    <h1>Google Drive Space Alert</h1>
                    <p>{message}</p>
                    <p>Total Space: {total_space_gb:.2f} GB</p>
                    <p>Used Space: {used_space_gb:.2f} GB</p>
                    <p>Your storage is low: {total_space_gb - used_space_gb:.2f} GB remaining</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    # Rest of the code remains the same
    # Set the HTML content as the email body
    msg.set_content(html_content, subtype="html")
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        # Login to the SMTP server
        server.login(from_email_addr, from_email_pass)
        # Send the email
        server.send_message(msg)
        print("Gmail sent successfully")
    except Exception as e:
        print("Error sending Email:", e)
    finally:
        # Disconnect from the SMTP server
        server.quit()
def process_video_queue(queue):
    while not queue.empty():
        video_id, file_path = queue.get()
        print(video_id)
        try:
            print("Wait upload and status starting")
            upload_to_google_drive(file_path, os.path.basename(file_path), video_id) 
        except Exception as e:
            print("Error uploading video:", e)
def check_internet_connection(url, timeout=2):
    print("Checking internet connection...")
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False
def run_entire_code():
    print("Running the entire code...")
    internet_on = check_internet_connection(internet_check_url, timeout=3)
    if internet_on:
        print("Internet connection is available.")
        connection = create_mysql_connection()
        try:
            video_queue = Queue()
            pending_videos = get_pending_videos(connection)
            for video in pending_videos:
                video_id, file_name = video[0], video[1]
                file_path = os.path.join(output_directory, file_name)
                video_queue.put((video_id, file_path))
            #process_video_queue(video_queue)
            # Calculate total_space_gb and used_space_gb
            desti_folder = '/home/hari/Desktop/GoogleDrive'
            total_space_gb, total_space_mb, free_space_gb, free_space_mb, used_space_gb, used_space_mb = get_folder_space_info(desti_folder)
            free_space_percentage = (free_space_gb / total_space_gb) * 100
            # if free_space_percentage <= 20:  # 80% full
            #     message_content = "Dear user, this is a Google Drive space alert! Please free up some space."
            #     send_email("Google Drive Space Alert", message_content, total_space_gb, used_space_gb)
            
            if free_space_percentage <=10:
                message_content = "Dear user, this is a Google Drive space alert! Storage Too space."
                send_email("Google Drive Space Alert", message_content, total_space_gb, used_space_gb)
                #print('1st condition')
            elif 20 >= free_space_percentage:
                process_video_queue(video_queue)
                message_content = "Dear user, this is a Google Drive space alert! Please free up some space."
                send_email("Google Drive Space Alert", message_content, total_space_gb, used_space_gb)
                #print('2nd condition')
            else:
                process_video_queue(video_queue)
                #print('3rd condition')   
        finally:
            connection.close()
    else:
        print("No Internet connection. Video processing cannot be performed.")
if __name__ == '__main__':
    run_entire_code()