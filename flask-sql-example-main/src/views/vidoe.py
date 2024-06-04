from flask import Flask, request, jsonify
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# YouTube API credentials
YOUTUBE_API_KEY = 'AIzaSyBbHzvYtqGXEgtiBge0WfWGuL227faoaUY'

# YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    response = search_youtube(query)
    return jsonify(response)

def search_youtube(query):
    request = youtube.search().list(
        part="snippet",
        maxResults=5,
        q=query,
        type="video"
    )
    response = request.execute()
    results = []
    for item in response.get('items', []):
        video = {
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        }
        results.append(video)
    return results

if __name__ == "__main__":
    app.run(port=5001, debug=True)
