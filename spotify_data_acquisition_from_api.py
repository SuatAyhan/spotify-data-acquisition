import requests
import base64
import time
import csv

# Spotify API kimlik bilgileri
client_id = 'b5b1962b7e8a450d854a87687e2f5e9f'
client_secret = 'b0718fca938949eb9245485e8abbf3dc'

# Playlist URL'lerini tanımlıyoruz.
playlist_links = [
    "https://open.spotify.com/playlist/4vSTV61efRmetmaoz95Vet",
    "https://open.spotify.com/playlist/5GhQiRkGuqzpWZSE7OU4Se",
    "https://open.spotify.com/playlist/56r5qRUv3jSxADdmBkhcz7",
    "https://open.spotify.com/playlist/6unJBM7ZGitZYFJKkO0e4P",
]

# Spotify API'ye kimlik doğrulaması yapmak için gerekli olan erişim anahtarını alır
def get_access_token(client_id, client_secret):
    credentials = f"{client_id}:{client_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_data = {
        'grant_type': 'client_credentials',
    }
    auth_headers = {
        'Authorization': f'Basic {base64_credentials}',
    }
    auth_response = requests.post(auth_url, data=auth_data, headers=auth_headers)

    if auth_response.status_code == 200:
        auth_response_data = auth_response.json()
        access_token = auth_response_data['access_token']
        return access_token
    else:
        print(f"Kimlik doğrulama hatası: {auth_response.status_code}")
        return None

def get_playlist_tracks(access_token, playlist_url, csv_writer):
    # Playlist ID'sini çıkarıyoruz.
    playlist_id = playlist_url.split('/')[-1]

    playlist_tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    playlist_tracks_response = requests.get(playlist_tracks_url, headers=headers)

    if playlist_tracks_response.status_code == 200:
        playlist_tracks_data = playlist_tracks_response.json()
        for item in playlist_tracks_data['items']:
            track_info = item['track']
            track_id = track_info['id']
            
            # Audio features bilgilerini çekiyoruz.
            audio_features_url = f'https://api.spotify.com/v1/audio-features/{track_id}'
            audio_features_response = requests.get(audio_features_url, headers=headers)
            
            if audio_features_response.status_code == 200:
                audio_features_data = audio_features_response.json()
                
                # Artist bilgilerini çekiyoruz.
                artist_info = track_info['artists'][0]  
                artist_id = artist_info['id']
                artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
                artist_response = requests.get(artist_url, headers=headers)
                
                if artist_response.status_code == 200:
                    artist_data = artist_response.json()
                    artist_genres = ', '.join(artist_data.get('genres', []))  # genres bilgisi kontrol ediliyor

                    # 'popularity' alanı kontrol ediliyor
                    artist_popularity = artist_data.get('popularity', 'N/A')

                    # Tüm bilgileri çekiyoruz
                    row = [track_info['name'], artist_info['name'], artist_info['uri'], artist_popularity, artist_genres,
                        track_info['duration_ms'], track_info['album']['release_date'], track_info['popularity']]
                    row.extend(list(audio_features_data.values()))
                    
                    csv_writer.writerow(row)
                else:
                    print(f"Artist bilgisi isteği hatası: {artist_response.status_code}")
            else:
                print(f"Audio features bilgisi isteği hatası: {audio_features_response.status_code}")

# CSV dosyasını aç ve başlık satırını yazıyoruz.
with open('playlist_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    header = ['Track Name', 'Artist', 'Artist URI', 'Artist Popularity', 'Artist Genres', 'Track Duration(ms)', 'Release Date', 'Track Popularity']
    header.extend(['Danceability', 'Energy', 'Key', 'Loudness', 'Mode', 'Speechiness', 'Acousticness',
                   'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 'Type','Track ID', 'Uri', 'Track_href', 'Analysis_url', 'Duration_ms', 'Time_signature'])
    csv_writer.writerow(header)

    # İlk token alımı
    access_token = get_access_token(client_id, client_secret)

    # Playlist URL'lerini dolaşıyoruz.
    for playlist_link in playlist_links:
        get_playlist_tracks(access_token, playlist_link, csv_writer)

    # Her bir saatte bir token alıyoruz.
    time.sleep(3600)
    access_token = get_access_token(client_id, client_secret)
