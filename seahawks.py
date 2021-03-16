"""
Created on 04/04/2019

@author: Byungsu (Jay) Jung

This script uses Spotify web api to perform query, load the extracted data in pandas dataframe
and export csv files.
"""
import requests
import json
import base64
import pandas as pd
import config
import os

client_id = config.client_id
client_secret = config.client_secret

# Get token using client_id and client_secret.
def getToken(client_id, client_secret):
    url = 'https://accounts.spotify.com/api/token'
    key_in_bytes = bytes(client_id + ":" + client_secret, encoding='utf-8')
    key_in_base64 = base64.standard_b64encode(key_in_bytes)
    authorization = key_in_base64.decode()
    auth = {'Authorization' : 'Basic {}'.format(authorization)}
    params = {'grant_type' : 'client_credentials' }
    response = requests.post(url, data=params, headers=auth).json()
    access_token = response.get('access_token')
    return (access_token)


# This function takes parameters q(serach words), type(search type), limit(max number of respose)
# and access_token(token used to access Spotify web api) to return json format of response containing the result of search.
def search(q,type,limit, access_token):
    base_url = "https://api.spotify.com/v1/search"
    params = "?q={}&type={}&limit={}".format(q,type,limit)
    url = base_url + params
    headers = {'Authorization ': "Bearer {}".format(access_token)}
    r = requests.get(url, headers=headers)
    json = r.json()
    return(json)

# This function returns item(the actual data extracted using search) from given json.
def item(json, ):
    json = json['']


# A recursive function to flatten json.
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# Return album dataframe of pandas dataframe type with selected data
def album(albums, access_token):
    final = []
    for album in albums:
        album_result = {}
        for key, value in album.items():
            if key in ['id',"album_type", "name", "release_date", 'total_tracks', 'type']:
                album_result[key] = value
            elif key == 'artists':
                artists = value[0]['name']
                if len(value) != 1:
                    for i in range(1,len(value)):
                        artists = artists + (", " + value[i]['name'])
                album_result[key] = artists
            elif key == 'images':
                album_result[key] = value[0]['url']

        final.append(album_result)
    return(pd.DataFrame.from_records(final))

def related_artists_of_artist(artist):
    url = "https://api.spotify.com/v1/artists/{}/related-artists".format(artist)
    headers = {'Authorization ': "Bearer {}".format(access_token)}
    r = requests.get(url, headers=headers)
    json = r.json()
    return(json)

# The artists function takes name of the artist as a input and
# return data of related artists of the given artist
def artists(name, access_token):
    the_artist = search(name,'artist',50, access_token)
    the_artist_id = the_artist['artists']['items'][0]['id']
    related_artists = related_artists_of_artist(the_artist_id)['artists']
    final = []
    for artist in related_artists:
        artist_result = {}
        for key, value in artist.items():
            if key in ['id', "name", "genres", 'popularity']:
                artist_result[key] = value
            elif key == 'followers':
                artist_result[key] = value['total']
            elif key == 'images':
                artist_result[key] = value[0]['url']

        final.append(artist_result)
    return(pd.DataFrame.from_records(final))

def main():
    
    access_token = getToken(client_id, client_secret)

    seahawks_albums_json = search('seahawks','album',50, access_token)
    # Data extracted form Spotify
    album_items = seahawks_albums_json['albums']['items']
    # Remove data that will not be used in future.
    for i in album_items:
        i.pop('available_markets')

    seahawks_album = album(album_items, access_token)

    drake_related_artists = artists('drake', access_token)

    eminem_related_artists = artists('eminem', access_token)

    export_list = [seahawks_album,drake_related_artists,eminem_related_artists]

    file_names =  ["seahawks_album","drake_related_artists","eminem_related_artists"]

    cwd = os.getcwd()

    for i in range(len(export_list)):
        path = cwd + "/{}.csv".format(file_names[i])
        export_list[i].to_csv(path_or_buf= path, header= True)


if __name__ == "__main__":
    main()