import sys, argparse, requests, json, http.server, spotify, asyncio, re
import threading
from http import HTTPStatus
from spotify import User

SPOTIFY_CLIENT_ID = ""
SPOTIFY_CLIENT_SECRET = ""
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_USER_TOKEN = ""
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:54321"
SPOTIFY_ACCESS_TOKEN = ""
httpd = None

class CallBackRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        global SPOTIFY_USER_TOKEN
        path = self.path
        codeparam = path.find("code=")
        if codeparam != -1:
            code = path[codeparam:]
            SPOTIFY_USER_TOKEN = code[5:]
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Length", "0")
            self.end_headers()
        return None

def get_apple_playlist(url):
    result = requests.get(url)
    json_start = result.text.find('{\\"x\\":')
    json_start = result.text.find('{\\"x\\":',json_start+1)
    json_end = result.text.find('"}</script>',json_start)

    jsonstuff = result.text[json_start:json_end].replace('\\"', '"')
    parsed = json.loads(jsonstuff)
    src_playlist = parsed["d"][0]
    playlist = {}
    playlist["name"] = src_playlist["attributes"]["name"]
    tracks = []
    print(f"Tracks for playlist \'{playlist['name']}\':")
    for track in src_playlist['relationships']['tracks']['data']:
        tracks.append(track['attributes'])
        print(f"{track['attributes']['artistName']} - {track['attributes']['name']}")

    playlist["tracks"] = tracks

    return playlist


def run_local_server():
    global httpd
    server_address = ('127.0.0.1', 54321)
    httpd = http.server.HTTPServer(server_address,CallBackRequestHandler)
    httpd.serve_forever()


async def find_spotify_song(client, artist, name, tracknameonly):
    results = await client.search(f"{artist} {name}",types=["track"])
    if results[3] is None or len(results[3]) == 0:
        print(f"A match for {artist} - {name} couldn't be found.")
        return None
    if len(results[3]) > 1:
        for track in results[3]:
            if track.artist.name.lower() in artist.lower() or track.artist.name.lower() in name.lower():
                if tracknameonly in track.name.lower() or name.lower() in track.name.lower():
                    return track
    else:
        return results[3][0]


async def build_spotify_playlist(client, playlist):
    global SPOTIFY_USER_TOKEN
    print("Getting user from token")
    user = await User.from_code(client,SPOTIFY_USER_TOKEN,redirect_uri=SPOTIFY_REDIRECT_URI)
    playlists = await user.get_playlists()
    playlist_exists = False
    s_playlist = None
    for pl in playlists:
        if pl.name == playlist["name"]:
            playlist_exists = True
            s_playlist = pl
            await s_playlist.clear()
            break
    if not playlist_exists:
        s_playlist = await user.create_playlist(playlist["name"])
    for track in playlist["tracks"]:

        tracknameonly = re.sub(r'\(.*?\)','',track['name'])
        tracknameonly = re.sub(r'\[.*?]', '', tracknameonly).strip().lower()
        track['name'] = track['name'].replace('(feat.','')

        searchname = re.sub(r'[^\w ]','', track['name'])

        fixedartist = re.sub(r'[^\w \-]','', track['artistName'])
        track = await find_spotify_song(client, fixedartist, searchname, tracknameonly)
        if track is not None:
            await user.add_tracks(s_playlist, track)
    await client.close()


def main(argv):
    global SPOTIFY_USER_TOKEN
    global httpd
    parser = argparse.ArgumentParser(description="Sync a playlist between Apple Music and Spotify",
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('source', metavar="playlist", type=str,
                             help="Source Apple Music playlist for sync")

    args = parser.parse_args(argv)

    playlist = get_apple_playlist(args.source)

    t = threading.Thread(target=run_local_server)
    t.start()
    print("\nLog into Spotify using the following URL to authorize the app:\n")
    authurl = f"{SPOTIFY_AUTH_URL}?client_id={SPOTIFY_CLIENT_ID}&response_type=code&"
    authurl += f"redirect_uri={SPOTIFY_REDIRECT_URI}&scope=playlist-modify-private%20playlist-modify-public"
    print(authurl)
    input("Press enter when authorization is done.")
    httpd.shutdown()
    t.join()
    print("Starting playlist build steps.")
    if SPOTIFY_USER_TOKEN != "":
        client = spotify.Client(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(build_spotify_playlist(client, playlist))


if __name__ == "__main__":
    main(sys.argv[1:])
