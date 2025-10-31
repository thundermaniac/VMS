import time
import mysql.connector as mysql
from picamera import PiCamera

import os



# Function to create a MySQL connection
db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "employees"
)


# Function to insert a new video record into the database
def insert_new_video_record(connection, filename, start_time, file_extension, status):
    print("__________________________",connection,filename)
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO recordings (File_name, Start_time, End_time, File_extension, Status,upload_status)
        VALUES (%s, %s, %s, %s, %s,%s)
        """
        values = (filename, start_time, start_time, file_extension, status,'pending')
        cursor.execute(insert_query, values)
        connection.commit()
    except Exception as e:
        print("Error inserting new video record:", e)
        
# Function to update video status in the database
def update_video_ProcessingStatus(connection, status,fromStatus):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE recordings SET Status = %s WHERE Status = %s", (status, fromStatus))
        connection.commit()
    except Exception as e:
        print("Error updating video status:", e)


# Function to update video status in the database
def update_video_status(connection, filename, status,end_time):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE recordings SET Status = %s,End_time=%s WHERE File_name = %s", (status, end_time, filename))
        connection.commit()
    except Exception as e:
        print("Error updating video status:", e)
        
def record_for_duration(camera, duration, filename,  output_extension):
    # Create MySQL connection
    connection = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "employees"
    )
    
    update_video_ProcessingStatus(connection,'Completed', 'Processing')
    start_time=time.time()
    camera.start_recording(filename, format='h264', quality=20, bitrate=750000)
    #run_display_indefinitely('Recording Started')
    print("camera has started")
    # Create MySQL connection
    connection = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "employees"
)

    # Insert a new record into the database with status 'Processing'
    file_name_o = os.path.split(filename)
    
    filename=file_name_o[1]
    
    insert_new_video_record(connection,filename,  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)), output_extension, 'Processing')
    # connection.close()
    start_time = time.time()
    elapsed_time = 0
    # if elapsed_time == duration:
    #     camera.stop_recording()
    while elapsed_time < duration:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        camera.annotate_text = current_time
        camera.wait_recording(1)
        #run_display_indefinitely('Video Recording....')
        #internet_check()
        elapsed_time = time.time() - start_time
    
    camera.stop_recording()
    #run_display_indefinitely('Video Recording Completed....')
    print("camera has stopped")
    end_time=time.time()
    connection = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "employees"
)

    # Update status in the database using filename and status 'Processing'
    update_video_status(connection, filename, 'Completed', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)))
    # connection.close()

    print("Video captured, stored, and data inserted into the database.")
       
        

# Function to capture and store video using Pi Camera
def capture_and_store_video(video_format,output_directory):
    try:
        # Initialize Pi Camera
       
       with PiCamera() as camera:
        camera.resolution = (640,360)  # Set desired resolution
        camera.framerate = 24  # Set desired framerate
        
         # Specify your desired save path
        
        while True:
            timestamp = time.strftime("%d-%m-%Y_%H-%M-%S-%p")
            #print(timestamp)
            out_ex="h264"
            h264_filename = f'{output_directory}{timestamp}.h264'
            print(h264_filename)
            
            # Calculate the remaining time in the current hour
            current_time_struct = time.localtime()
            remaining_minutes = 60 - current_time_struct.tm_min - 1
            remaining_seconds = 60 - current_time_struct.tm_sec
            remaining_time = remaining_minutes * 60 + remaining_seconds
            
            if remaining_time > 0:
                # Record for the remaining time in the current hour
                record_for_duration(camera, remaining_time, h264_filename,  video_format)
                # Insert data into MySQL table
               
            remaining_time = 0
            # Calculate the duration for the next full hour
            next_hour = current_time_struct.tm_hour + 1
            next_hour_duration = (next_hour - current_time_struct.tm_hour) * 60 * 60
            
            # Record for the next full hour
            print(time.localtime(time.time() + remaining_time))
            timestamp = time.strftime("%d-%m-%Y_%H-%M-%S-%p", time.localtime(time.time() + remaining_time))
            # print(timestamp)
            out_ex="h264"
            # h264_filename = f'{output_directory}{timestamp}.{out_ex}'
            h264_filename = f'{output_directory}{timestamp}.h264'
            record_for_duration(camera, next_hour_duration, h264_filename,video_format)
            
            # Insert data into MySQL table
           
            
            
    except Exception as e:
        #run_display_indefinitely('Eception on Video Recording....')
        print("Error capturing and storing video:", e)
        # Handle network issue time calculation
        # ...
    
# Main code execution
if __name__ == "__main__":
    
    output_directory = 'Local_recordings/'
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_directory_parts = os.path.split(script_directory)
    output_directory = os.path.join(output_directory_parts[0], output_directory)
    #output_directory = "/home/hari/recordings"
    #save_path = '/home/hari/recordings2/'
    video_format = 'h264'  # Specify the video format ('h264', 'mp4', etc.)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    print(output_directory)

   
capture_and_store_video(video_format,output_directory)