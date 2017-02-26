#! /usr/bin/env python3

import twitter
import spotipy
import spotipy.util as spu

import auth as au

#Set whether explicit tracks should be allowed. 
ALLOW_EXPLICIT_SONGS = False

# Set the playlist URI for the playlist to edit.
# Playlist must be owned by the user account who's details are in auth.py
PLAYLIST_ID = "spotify:user:hedzup456:playlist:21dGBWhbLGMOTWGH6vAkIE"

# Set the hashtag to search for - case insensitive.
HASHTAG = "#HEDZREQUESTS"

def auth(scope):
    try:
        token = spu.prompt_for_user_token(au.SPOTIPY_USER, scope, client_id = au.SPOTIPY_CLIENT_ID,
                client_secret = au.SPOTIPY_CLIENT_SECRET, redirect_uri = au.SPOTIPY_REDIRECT)
        return token
    except:
        print("Fuck")



def tweetOut(message, api, parent=None):
    try:
        api.PostUpdate(message, in_reply_to_status_id = parent)
        print("Tweeting: {}".format(message))
    except twitter.error.TwitterError:
        pass

        

def addSongsToPlaylist(playlist, songsToAdd, token):
    if token:
        sp = spotipy.Spotify(auth=token)
        songs = sp.user_playlist_tracks(au.SPOTIPY_USER, playlist_id = playlist)["items"]

        songIDs = [song["track"]["id"] for song in songs]
        songURIs = [song["track"]["uri"] for song in songs]
        

        returnText = ""
        for song in songsToAdd:
            if not(song[0] in songIDs or song[0] in songURIs):
                track = sp.track(song[0])
                if not(track["explicit"]) or ALLOW_EXPLICIT_SONGS:
                    returnText = "@{} - Adding {} by {} to the playlist. \n~Spotibot".format(song[2], track["name"], track["artists"][0]["name"])
                    sp.user_playlist_add_tracks(au.SPOTIPY_USER, playlist, [song[0]])
                else:
                    returnText = "@{} - {} not added due to explicit lyrics. \n~Spotibot".format(song[2], track["name"])
                global api
                tweetOut(returnText, api, parent = song[1])
    else:
        print("Token not valid. Someone fuck up?")

scope = "playlist-modify-public"

token = auth(scope)

songsToAdd = []


api = twitter.Api(consumer_key = au.TWITTER_CONSUMER_KEY, consumer_secret = au.TWITTER_CONSUMER_SECRET,
        access_token_key = au.TWITTER_ACCESS_TOKEN_KEY, access_token_secret = au.TWITTER_ACCESS_TOKEN_SECRET)

requestTweets = api.GetSearch(term = HASHTAG, since = "2017-02-25", result_type = "recent")

for tweet in requestTweets:
    tweetParts = tweet.text.split()
    for part in tweetParts:
        if part[:14].lower() == "spotify:track:":
            songsToAdd.append([part, tweet.id, tweet.user.screen_name])

addSongsToPlaylist(PLAYLIST_ID, songsToAdd, token)
