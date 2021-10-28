# -*- coding: utf-8 -*-

import os,sys,re,json
from resources.lib import client, utils

if sys.version_info[0] == 3:
    import urllib.parse as urlparse
else:
    import urlparse



class movies:
    def __init__(self):
        tmdb_key = '20b20b26503726a44d5b3788e074a66a'
        omdbapi_key = 'ef3f1e99'
        self.trakt_info_link = 'http://api-v2launch.trakt.tv/movies/%s'
        self.trakt_lang_link = 'http://api-v2launch.trakt.tv/movies/%s/translations/%s'
        self.imdb_info_link = 'http://www.omdbapi.com/?i=%s&plot=full&r=json&apikey=%s' % ('%s', omdbapi_key)
        self.tmdb_info_link = 'https://api.themoviedb.org/3/movie/%s/images?api_key=%s&language=hu&include_image_language=hu,null'  % ('%s', tmdb_key)
        self.tmdb_image = 'https://image.tmdb.org/t/p/w500'

    def super_info(self, meta):
        try:
            imdb = meta['imdb']
            url = self.imdb_info_link % imdb

            item = client.request(url, timeout='10')
            item = json.loads(item)

            year = item['Year']
            year = utils.py2_encode(year)
            if not year == '0': meta.update({'year': year})

            imdb = item['imdbID']
            if imdb == None or imdb == '' or imdb == 'N/A': imdb = '0'
            imdb = utils.py2_encode(imdb)
            if not imdb == '0': meta.update({'imdb': imdb, 'code': imdb})

            premiered = item['Released']
            if premiered == None or premiered == '' or premiered == 'N/A': premiered = '0'
            premiered = re.findall('(\d*) (.+?) (\d*)', premiered)
            try: premiered = '%s-%s-%s' % (premiered[0][2], {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}[premiered[0][1]], premiered[0][0])
            except: premiered = '0'
            premiered = utils.py2_encode(premiered)
            if not premiered == '0': meta.update({'premiered': premiered})

            genre = item['Genre']
            if genre == None or genre == '' or genre == 'N/A': genre = '0'
            genre = genre.replace(', ', ' / ')
            genre = utils.py2_encode(genre)
            if not genre == '0': meta.update({'genre': genre})

            rating = item['imdbRating']
            if rating == None or rating == '' or rating == 'N/A' or rating == '0.0': rating = '0'
            rating = utils.py2_encode(rating)
            if not rating == '0': meta.update({'rating': rating})

            votes = item['imdbVotes']
            try: votes = str(format(int(votes),',d'))
            except: pass
            if votes == None or votes == '' or votes == 'N/A': votes = '0'
            votes = utils.py2_encode(votes)
            if not votes == '0': meta.update({'votes': votes})

            mpaa = item['Rated']
            if mpaa == None or mpaa == '' or mpaa == 'N/A': mpaa = '0'
            mpaa = utils.py2_encode(mpaa)
            if not mpaa == '0': meta.update({'mpaa': mpaa})

            director = item['Director']
            if director == None or director == '' or director == 'N/A': director = '0'
            director = director.replace(', ', ' / ')
            director = re.sub(r'\(.*?\)', '', director)
            director = ' '.join(director.split())
            director = utils.py2_encode(director)
            if not director == '0': meta.update({'director': director})

            writer = item['Writer']
            if writer == None or writer == '' or writer == 'N/A': writer = '0'
            writer = writer.replace(', ', ' / ')
            writer = re.sub(r'\(.*?\)', '', writer)
            writer = ' '.join(writer.split())
            writer = utils.py2_encode(writer)
            if not writer == '0': meta.update({'writer': writer})

            cast = item['Actors']
            if cast == None or cast == '' or cast == 'N/A': cast = '0'
            cast = [x.strip() for x in cast.split(',') if not x == '']
            try: cast = [(utils.py2_encode(x), '') for x in cast]
            except: cast = []
            if cast == []: cast = '0'
            if not cast == '0': meta.update({'cast': cast})

            plot = item['Plot']
            if plot == None or plot == '' or plot == 'N/A': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = utils.py2_encode(plot)
            if not plot == '0' and meta['plot'] == '0': meta.update({'plot': plot})

            try:
                url = self.trakt_info_link % imdb
                
                item = self.getTrakt(url)
                item = json.loads(item)
                
                tmdb = '0'
                try: tmdb = item['ids']['tmdb']
                except: pass
            
                if tmdb == '0': raise Exception()
                
                url = self.tmdb_info_link % tmdb
                item = client.request(url)
                item = json.loads(item)
            
                try: poster = item['posters'][0]['file_path']
                except: poster = ''
                if not poster == '': poster = self.tmdb_image + poster
                else: poster = '0'
                poster = utils.py2_encode(poster)
                if not poster == '0': meta.update({'poster': poster})
    
                try: fanart = item['backdrops'][0]['file_path']
                except: fanart = ''
                if not fanart == '': fanart = self.tmdb_image + fanart
                else: fanart = '0'
                if fanart == '0' and not poster == '0': fanart = poster
                try: fanart = utils.py2_encode(fanart)
                except: pass
                if not fanart == '0': meta.update({'fanart': fanart})
            except:
                pass

            url = self.trakt_lang_link % (imdb, 'hu')

            item = self.getTrakt(url)
            item = json.loads(item)[0]

            plot = item['overview']
            if plot == None or plot == '': plot = '0'
            try: plot = utils.py2_encode(plot)
            except: pass
            if not plot == '0': meta.update({'plot': plot})
        except:
            pass
        return meta

    def getTrakt(self, url):
        try:
            url = urlparse.urljoin('http://api-v2launch.trakt.tv', url)
    
            headers = {'Content-Type': 'application/json', 'trakt-api-key': '03a3443d7d3d3e66f949cfd4adfda59ed7e22d182bd0c1e3a0d7e3383c3a209f', 'trakt-api-version': '2'}

            result = client.request(url, post=None, headers=headers)
            return result
    
        except:
            pass