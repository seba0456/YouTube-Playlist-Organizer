import re
import os
import difflib
from time import time
from pytube import YouTube, Playlist
from tqdm import tqdm
import configparser
from datetime import datetime

today = datetime.today().strftime("%Y-%m-%d")


config = configparser.ConfigParser()
config.read('config.ini')
min_similarity = float(config.get('main', 'min_similarity'))
can_download_video=int(config.get('main', 'download_video'))
can_download_music=int(config.get('main', 'download_music'))
backup_playlist=int(config.get('main', 'backup_playlist'))
playlist_link = input("Enter YouTube playlist link:")
p=Playlist(playlist_link)
playlist_name=p.title
playlist_save = f"{playlist_name}_{today}.txt"
playlist = Playlist(playlist_link)
print("Opening", playlist_name)

video_links = Playlist(playlist_link).video_urls

def download_video(url, folder='Videos'):
    yt = YouTube(url)
    video = yt.streams.filter(file_extension='mp4').first()
    if not os.path.exists(folder):
        os.makedirs(folder)
    video.download(folder)

def download_audio(url, folder='Music'):
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).first()
    if not os.path.exists(folder):
        os.makedirs(folder)
    audio.download(folder)

def get_similar_titles(title1, title2, link1,link2):
    title1 = re.sub(r'[^\w\s]', '', title1.lower())
    title2 = re.sub(r'[^\w\s]', '', title2.lower())
    ratio = difflib.SequenceMatcher(None, title1, title2).ratio()
    return ratio

video_titles = []
saved_video_links = []
invalid_video_links = []
start = time()
for link in tqdm(video_links):
    try:
        video_title = YouTube(link).title
        video_titles.append(video_title)
        saved_video_links.append(link)
    except Exception as e:
        invalid_video_links.append(link)

print(f'Time taken: {time() - start}')
print("Comparing titles...")
similar_titles = []
for i in tqdm(range(len(video_titles))):
    for j in range(i+1, len(video_titles)):
        similarity = get_similar_titles(video_titles[i], video_titles[j], saved_video_links[i], saved_video_links[j])
        if similarity >= min_similarity:
            similar_titles.append((video_titles[i], video_titles[j], similarity, saved_video_links[i], saved_video_links[j]))
print(20*"_")
similar_titles = sorted(similar_titles, key=lambda x: x[2], reverse=True)
if similar_titles:
    print("Comprising ", len(video_titles), ",", len(invalid_video_links), "title(s) are invalid.")
    print("Found ", len(similar_titles), "similar tiles, saving them to similar_titles.txt")
    with open("similar_titles.txt", "w", encoding='utf-8') as file:
        file.seek(0)
        file.truncate()
        file.write("Titles that are very similar:\n")
        for title1, title2, similarity, link1, link2 in similar_titles:
            file.write(f'{title1} and {title2}, similarity: {similarity:.2f}, {link1}, to {link2}\n')
else:
    print('No similar titles found.')
if len(invalid_video_links) > 0:
    print("Found ", len(invalid_video_links), "invalid video links, saving them to invalid_links.txt")
    with open("Invalid_links.txt", "w", encoding='utf-8') as file:
        file.seek(0)
        file.truncate()
        file.write("Titles that are very similar:\n")
        for i in invalid_video_links:
            file.write(f'{i}\n')
print(20*"_")
if can_download_video == 1 or can_download_music == 1:
    if can_download_music == 1:
        print("Downloading ", len(saved_video_links), "audio file(s).")
        downloaded_files = 0
        wrong_links = []
        for i in tqdm(saved_video_links):
            try:
                download_audio(i)
                downloaded_files += 1
            except:
                print("bug")
                continue
        print("Downloaded ", downloaded_files, "file(s).")
        if len(saved_video_links) != downloaded_files:
            print("Couldn't download ", len(saved_video_links) - downloaded_files, "file(s).")
            for i in wrong_links:
                print(i)
        print(20 * "_")
    if can_download_video == 1:
        print("Downloading ", len(saved_video_links), "video file(s).")
        downloaded_files=0
        wrong_links=[]
        for i in tqdm(saved_video_links):
            try:
                download_video(i)
                downloaded_files+=1
            except:
                wrong_links.append(i)
                continue
        print("Downloaded ", downloaded_files, "file(s).")
        if len(saved_video_links) != downloaded_files:
            print("Couldn't download ", len(saved_video_links)-downloaded_files, "file(s).")
            for i in wrong_links:
                print(i)
        print(20 * "_")
if backup_playlist == 1:
    print("Creating playlist backup...")
    with open(playlist_save, "w", encoding='utf-8') as file:
        file.seek(0)
        file.truncate()
        file.write("Videos in playlist:\n")
        for saved_video_links, video_titles in zip(saved_video_links, video_titles):
            file.write(video_title + (5 * " ") + saved_video_links + "\n")



print("Done.")