import pyinsane2
import tkinter as tk
import os
import time
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

scan_count = 0
stop_scan_flag = False  # Flag that controlls the scanning loop
scan_thread = None

def scan_image():
    global scan_count, stop_scan_flag

    while not stop_scan_flag:
        pyinsane2.init()
        try:
            devices = pyinsane2.get_devices()
            if not devices:
                print("No scanners found.")
                return

            scanner = devices[0]
            print(f"Using scanner: {scanner.name}")

            output_file = f"image ({scan_count}).png"

            scan_session = scanner.scan(multiple=False)
            while not stop_scan_flag:
                try:
                    scan_session.scan.read()
                except EOFError:
                    break

            if not stop_scan_flag:
                image = scan_session.images[0]
                image.save(output_file)
                print(f"Image saved as {output_file}")
                scan_count += 1

            time.sleep(8)

        except pyinsane2.SaneException as e:
            print(f"An error occurred: {e}")

        pyinsane2.exit()

def send_email(sender_email, app_password, receiver_email, subject, body, directory):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        all_files = os.listdir(directory)
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
        image_paths = [file for file in all_files if os.path.splitext(file)[1].lower() in image_extensions]

        for image_path in image_paths:
            with open(os.path.join(directory, image_path), "rb") as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', filename=image_path)
                msg.attach(img)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print("Error sending email:", str(e))

def scan_button_click():
    global scan_thread
    if scan_thread is None or not scan_thread.is_alive():
        scan_thread = threading.Thread(target=scan_image)
        scan_thread.start()

def stop_button_click():
    global stop_scan_flag
    stop_scan_flag = True
    sender_email = "YOUR EMAIL"
    app_password = "YOUR GMAIL APP PASSWORD"
    receiver_email = "RECIPIENT EMAIL "
    subject = "Images Attached"
    body = "test"
    directory = os.getcwd()
    send_email(sender_email, app_password, receiver_email, subject, body, directory)

def clear_images():
    global scan_count
    for filename in os.listdir():
        if filename.startswith("image"):
            os.remove(filename)
    scan_count = 0

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scanner App")

    scan_button = tk.Button(root, text="Scan Image", command=scan_button_click)
    scan_button.pack(padx=40, pady=10)

    stop_button = tk.Button(root, text="Stop Scan", command=stop_button_click)
    stop_button.pack(padx=40, pady=5)

    clear_button = tk.Button(root, text="Clear Images", command=clear_images)
    clear_button.pack(padx=40, pady=5)

    root.mainloop()
