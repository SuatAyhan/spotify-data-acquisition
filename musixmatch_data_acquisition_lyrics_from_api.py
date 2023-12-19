import requests
import csv

# Musixmatch API anahtarı
api_key = "api key"

# Musixmatch API kullanarak şarkı ID'sini alıyoruz.
def get_track_id(api_key, track_name, artist_name):
    url = f"https://api.musixmatch.com/ws/1.1/track.search?q_track={track_name}&q_artist={artist_name}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["message"]["header"]["status_code"] == 200:
        track_list = data["message"]["body"]["track_list"]
        if track_list:
            track_id = track_list[0]["track"]["track_id"]
            return track_id
        else:
            print(f"{artist_name} tarafından {track_name} bulunamadı.")
            return None
    else:
        print(f"{artist_name} tarafından {track_name} için track ID alınırken hata oluştu: {data['message']['header']['status_code']}")
        return None

# Musixmatch API kullanarak şarkı sözlerini alıyoruz.
def get_lyrics(api_key, track_id):
    url = f"https://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["message"]["header"]["status_code"] == 200:
        lyrics = data["message"]["body"]["lyrics"]["lyrics_body"]
        return lyrics
    else:
        return None

# CSV dosyasını aç ve başlık satırını yazıyoruz.
input_csv_path = 'playlist_data.csv'  # Bu dosyayı kendi CSV dosyanızın adıyla değiştiriyoruz.
output_csv_path = 'playlist_dataset(lyrics).csv'  # Çıktı dosyasının adını belirtiyoruz.

with open(input_csv_path, 'r', newline='', encoding='utf-8') as input_csv, \
        open(output_csv_path, 'w', newline='', encoding='utf-8') as output_csv:
    
    # Giriş ve çıkış CSV dosyaları için okuma ve yazma nesnelerini oluşturuyoruz.
    input_reader = csv.DictReader(input_csv)
    fieldnames = input_reader.fieldnames + ['Lyrics']  # Yeni sütunu ekliyoruz

    output_writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
    output_writer.writeheader()

    for row in input_reader:
        track_name = row['Track Name']
        artist_name = row['Artist']

        # Track ID'yi alıyoruz.
        track_id = get_track_id(api_key, track_name, artist_name)

        if track_id:
            # Lyrics'i alıyoruz.
            lyrics = get_lyrics(api_key, track_id)

            # Yeni sütunu ekleyip yazıyoruz.
            row['Lyrics'] = lyrics
            output_writer.writerow(row)
