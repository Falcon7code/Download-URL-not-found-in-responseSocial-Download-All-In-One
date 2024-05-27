import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import requests
import threading
import json
import http.client
import ssl

def fetch_video_details():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a video URL")
        return

    progress_label.config(text="Fetching video details...")
    progress_bar.start()

    def api_call():
        conn = http.client.HTTPSConnection("social-download-all-in-one.p.rapidapi.com", context=ssl._create_unverified_context())

        payload = json.dumps({"url": url})

        headers = {
            'x-rapidapi-key': "eabb72b3d0mshdecf177b50e29dcp1990f2jsn813d42ee3318",
            'x-rapidapi-host': "social-download-all-in-one.p.rapidapi.com",
            'Content-Type': "application/json"
        }

        try:
            conn.request("POST", "/v1/social/autolink", payload, headers)
            res = conn.getresponse()
            data = res.read()
            if res.status != 200:
                error_message = f"HTTP error occurred: {res.status} - {res.reason}\n{data.decode('utf-8')}"
                display_error(error_message)
                return

            video_details = json.loads(data.decode("utf-8"))
            display_video_details(video_details)

            # Extract download URL from the medias list
            medias = video_details.get("medias", [])
            if medias and "url" in medias[0]:
                download_url = medias[0]["url"]
                download_button.config(state=tk.NORMAL)
                download_button.config(command=lambda: download_video(download_url))
            else:
                display_error("Download URL not found in response")
        except Exception as err:
            error_message = f"An error occurred: {err}"
            display_error(error_message)
        finally:
            conn.close()
            progress_bar.stop()
            progress_label.config(text="")

    threading.Thread(target=api_call).start()

def display_video_details(details):
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, json.dumps(details, indent=4))

def display_error(message):
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, message)

def download_video(download_url):
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if not file_path:
        return

    progress_label.config(text="Downloading video...")
    progress_bar.start()

    def download():
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as err:
            error_message = f"An error occurred: {err}"
            display_error(error_message)
        finally:
            progress_bar.stop()
            progress_label.config(text="")

    threading.Thread(target=download).start()

# Setting up the GUI
root = tk.Tk()
root.title("Social Media Video Downloader - All In One")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

# Title Label
title_label = tk.Label(root, text="Social Media Video Downloader", font=("Helvetica", 16, "bold"), bg="#ff0000", fg="#ffffff", borderwidth=2, relief="solid")
title_label.pack(pady=10)

# Frame for URL Entry and Platform Selection
frame = tk.Frame(root, bg="#ffcb05", borderwidth=2, relief="solid")
frame.pack(pady=20)

url_label = tk.Label(frame, text="Enter Video URL:", font=("Helvetica", 12, "bold"), bg="#ffcb05", fg="#000000")
url_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

url_entry = tk.Entry(frame, width=60, font=("Helvetica", 12))
url_entry.grid(row=0, column=1, padx=5, pady=5)

fetch_button = tk.Button(frame, text="Fetch Video Details", font=("Helvetica", 12, "bold"), bg="#3b4cca", fg="#ffffff", command=fetch_video_details)
fetch_button.grid(row=0, column=2, padx=5, pady=5)

download_button = tk.Button(root, text="Download Video", font=("Helvetica", 12, "bold"), bg="#4caf50", fg="#ffffff", state=tk.DISABLED)
download_button.pack(pady=10)

# Progress Indicator
progress_label = tk.Label(root, text="", font=("Helvetica", 10, "italic"), bg="#f0f0f0")
progress_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, mode="indeterminate")
progress_bar.pack(pady=5, fill="x", padx=20)

# Result Display
result_label = tk.Label(root, text="Result:", font=("Helvetica", 12, "bold"), bg="#ffcb05", fg="#000000", borderwidth=2, relief="solid")
result_label.pack(pady=10)

result_text = tk.Text(root, height=20, width=70, font=("Helvetica", 12), wrap="word", borderwidth=2, relief="solid", bg="#ffffff", fg="#000000")
result_text.pack(pady=10)

root.mainloop()
