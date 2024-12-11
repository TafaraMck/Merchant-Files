import os
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox
from googleapiclient.discovery import build

# Set up CustomTkinter appearance
ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("dark-blue")  # Base theming (we'll customize further)


# Function to fetch video descriptions
def get_video_descriptions(api_key, channel_id):
    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # Step 1: Fetch video IDs
        video_ids = []
        next_page_token = None
        while True:
            request = youtube.search().list(
                part="id",
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            # Collect video IDs
            video_ids.extend(
                item["id"]["videoId"]
                for item in response['items']
                if "videoId" in item['id']
            )

            # Check if there are more pages
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        # Step 2: Fetch full details for videos
        descriptions = []
        for i in range(0, len(video_ids), 50):  # API allows max 50 IDs per request
            video_request = youtube.videos().list(
                part="snippet",
                id=",".join(video_ids[i:i+50])
            )
            video_response = video_request.execute()

            for video in video_response["items"]:
                title = video["snippet"]["title"]
                video_id = video["id"]
                description = video["snippet"]["description"]
                descriptions.append({
                    "title": title,
                    "video_id": video_id,
                    "description": description
                })

        return descriptions
    except Exception as e:
        return str(e)




# Function to save descriptions to text files
def save_descriptions_to_txt(descriptions, folder):
    os.makedirs(folder, exist_ok=True)
    for video in descriptions:
        sanitized_title = re.sub(r'[\\/*?:\"<>|]', '', video['title'])
        file_name = f"{folder}/{sanitized_title}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"Video Title: {video['title']}\n")
            file.write(f"Video ID: {video['video_id']}\n")
            file.write(f"Description:\n{video['description']}\n")


# Function triggered by the UI
def fetch_and_save():
    api_key = api_key_entry.get().strip()
    channel_id = channel_id_entry.get().strip()
    folder = filedialog.askdirectory()

    if not api_key or not channel_id:
        messagebox.showerror("Error", "API Key and Channel ID are required!")
        return

    if not folder:
        messagebox.showerror("Error", "Please select a folder to save files.")
        return

    feedback_label.configure(text="Fetching video descriptions...")
    root.update_idletasks()

    result = get_video_descriptions(api_key, channel_id)
    if isinstance(result, str):  # Check if an error occurred
        messagebox.showerror("Error", result)
    else:
        save_descriptions_to_txt(result, folder)
        messagebox.showinfo("Success", "Video descriptions saved successfully!")

    feedback_label.configure(text="")


# CustomTkinter UI setup
root = ctk.CTk()
root.title("YouTube Video Description Downloader")
root.geometry("500x300")

# Add logo
root.iconbitmap("logo.ico")  # Ensure logo.ico is in the same directory

# Set custom YouTube theme colors
root.configure(bg="#181818")  # YouTube's dark background color


# Title
title_label = ctk.CTkLabel(root, text="YouTube Video Description Downloader",
                           text_color="#FF0000",  # YouTube red
                           font=("Arial", 18, "bold"))
title_label.pack(pady=20)

# API Key Entry
api_key_label = ctk.CTkLabel(root, text="API Key:", text_color="#FFFFFF", font=("Arial", 12))
api_key_label.pack(anchor="w", padx=20)
api_key_entry = ctk.CTkEntry(root, width=400)
api_key_entry.pack(padx=20, pady=10)

# Channel ID Entry
channel_id_label = ctk.CTkLabel(root, text="Channel ID:", text_color="#FFFFFF", font=("Arial", 12))
channel_id_label.pack(anchor="w", padx=20)
channel_id_entry = ctk.CTkEntry(root, width=400)
channel_id_entry.pack(padx=20, pady=10)

# Fetch and Save Button
fetch_button = ctk.CTkButton(root, text="Fetch and Save Descriptions", command=fetch_and_save,
                             fg_color="#FF0000", hover_color="#D32F2F",  # YouTube red
                             text_color="#FFFFFF", font=("Arial", 14, "bold"))
fetch_button.pack(pady=20)

# Feedback Label
feedback_label = ctk.CTkLabel(root, text="", text_color="#AAAAAA", font=("Arial", 10))
feedback_label.pack(pady=10)

# Run the app
root.mainloop()
