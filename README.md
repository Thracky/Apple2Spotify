# Apple2Spotify

This is a VERY rough script and set of instructions for "copying" a playlist from Apple Music to Spotify without requiring an Apple Developer account.

Uses spotify.py: https://github.com/mental32/spotify.py

**USE AT YOUR OWN RISK. I TAKE ZERO RESPONSIBILITY FOR YOU MESSING UP YOUR PLAYLISTS!**

## Setup

### Spotify Developer Stuff

#### 1. Create a new application in the Spotify developer dashboard

It's located at https://developer.spotify.com/dashboard/applications

Call the application whatever you want.

#### 2. Add a local callback URL

Go to "Edit Settings" for the new application and add http://127.0.0.1:54321 as a Redirect URI.
- The script runs a webserver temporarily to receive the callback and gets a user authentication token
- You can change the port if you want but make sure you change `SPOTIFY_REDIRECT_URI` in the script to match.

#### 3. Add Spotify users that can access your application

Go to "Users and Access" and add whatever Spotify account(s) you want to create playlists on.

#### 4. Edit the script with your Client ID and Secret

Replace `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in the script with the ID and Secret from the application overview screen

### Python

pip3 install -r requirements.txt

Note that this will grab the "latest" spotify.py which is currently considered to be abandoned so it may disappear at some point.

## Usage

The Apple Music playlist you want to copy must be public. You can get the URL for it through the "Share" option in Music/iTunes.

Playlist URLs will look something like this: `https://music.apple.com/<country code>/playlist/<name>/<some identifier>`

1. Run the script as follows:
   * `python apple2spotify.py <Apple Music playlist URL>`
2. The script grabs the playlist contents from Apple Music and prints it
3. The script prints a Spotify URL for you to use to authorize the application
4. After authorizing the application, your web browser will send a request to the local webserver with the authorization token
5. Once you see the incoming request (which should be printed on the screen), press enter (maybe twice?) to actually create the playlist on Spotify


## Bugs?

Probably. Send a PR or open an issue and make sure you include the Apple Music playlist you're trying to copy. I make no promises that I will fix anything.

I have tried to handle cases that show up frequently in electronic music such as artist features and remixes, but I did it in a really lazy way and it'll likely break on some stuff.

## License

It's a script and a set of instructions, do what you want with it.





