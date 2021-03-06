# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import os,sys,re,json,zipfile,datetime

from resources.lib import control
from resources.lib import client
from resources.lib import cache
from resources.lib import utils

if sys.version_info[0] == 3:
    from io import BytesIO as StringIO
    from urllib import request as urllib2
else:
    from StringIO import StringIO
    import urllib2



class seasons:
    def __init__(self):
        self.lang = 'hu'
        self.tvdb_key = '2823ED13BBEDEDC8'

        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key, '%s', '%s')
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'


    def tvdb_list(self, meta, act_season):
        imdb = meta['imdb']

        try:
            if not imdb == '0':
                url = self.tvdb_by_imdb % imdb

                result = client.request(url, timeout='10')

                try: tvdb = client.parseDOM(result, 'seriesid')[0]
                except: tvdb = '0'

                try: name = client.parseDOM(result, 'SeriesName')[0]
                except: name = '0'
                name = utils.py2_encode(name)
                if not name == '0': meta.update({'tvshowtitle': name})
                dupe = re.compile('[***]Duplicate (\d*)[***]').findall(name)
                if len(dupe) > 0: tvdb = str(dupe[0])

                if tvdb == '': tvdb = '0'
        except:
            return meta


        try:
            if tvdb == '0': return meta

            url = self.tvdb_info_link % (tvdb, 'en')
            data = urllib2.urlopen(url, timeout=30).read()

            zip = zipfile.ZipFile(StringIO(data))
            result = zip.read('%s.xml' % 'en').decode()
            artwork = zip.read('banners.xml').decode()
            zip.close()

            dupe = client.parseDOM(result, 'SeriesName')[0]
            dupe = re.compile('[***]Duplicate (\d*)[***]').findall(dupe)

            if len(dupe) > 0:
                tvdb = utils.py2_encode(str(dupe[0]))

                url = self.tvdb_info_link % (tvdb, 'en')
                data = urllib2.urlopen(url, timeout=30).read()

                zip = zipfile.ZipFile(StringIO(data))
                result = zip.read('%s.xml' % 'en').decode()
                artwork = zip.read('banners.xml').decode()
                zip.close()

            if not self.lang == 'en':
                url = self.tvdb_info_link % (tvdb, self.lang)
                data = urllib2.urlopen(url, timeout=30).read()

                zip = zipfile.ZipFile(StringIO(data))
                result2 = zip.read('%s.xml' % self.lang).decode()
                zip.close()
            else:
                result2 = result

            artwork = artwork.split('<Banner>')
            artwork = [i for i in artwork if '<Language>en</Language>' in i and '<BannerType>season</BannerType>' in i]
            artwork = [i for i in artwork if not 'seasonswide' in re.findall('<BannerPath>(.+?)</BannerPath>', i)[0]]


            result = result.split('<Episode>')
            result2 = result2.split('<Episode>')

            item = result[0] ; item2 = result2[0]

            result = '' ; result2 = ''

            try: poster = client.parseDOM(item, 'poster')[0]
            except: poster = ''
            if not poster == '': poster = self.tvdb_image + poster
            else: poster = '0'
            poster = client.replaceHTMLCodes(poster)
            poster = utils.py2_encode(poster)

            try: banner = client.parseDOM(item, 'banner')[0]
            except: banner = ''
            if not banner == '': banner = self.tvdb_image + banner
            else: banner = '0'
            banner = client.replaceHTMLCodes(banner)
            banner = utils.py2_encode(banner)

            try: fanart = client.parseDOM(item, 'fanart')[0]
            except: fanart = ''
            if not fanart == '': fanart = self.tvdb_image + fanart
            else: fanart = '0'
            fanart = client.replaceHTMLCodes(fanart)
            fanart = utils.py2_encode(fanart)
            if not fanart == '0': meta.update({'fanart': fanart})

            if not poster == '0': pass
            elif not fanart == '0': poster = fanart
            elif not banner == '0': poster = banner

            if not banner == '0': pass
            elif not fanart == '0': banner = fanart
            elif not poster == '0': banner = poster
            
            if not poster == '0': meta.update({'poster': poster})
            if not banner == '0': meta.update({'banner': banner})

            try: genre = client.parseDOM(item, 'Genre')[0]
            except: genre = ''
            genre = [x for x in genre.split('|') if not x == '']
            genre = ' / '.join(genre)
            if genre == '': genre = '0'
            genre = client.replaceHTMLCodes(genre)
            genre = utils.py2_encode(genre)
            if not genre == '0': meta.update({'genre': genre})

            try: duration = client.parseDOM(item, 'Runtime')[0]
            except: duration = ''
            if duration == '': duration = '0'
            duration = client.replaceHTMLCodes(duration)
            duration = utils.py2_encode(duration)
            if not duration == '0' and meta['duration'] =='0': meta.update({'duration': duration})

            try: rating = client.parseDOM(item, 'Rating')[0]
            except: rating = ''
            if rating == '': rating = '0'
            rating = client.replaceHTMLCodes(rating)
            rating = utils.py2_encode(rating)
            if not rating == '0': meta.update({'rating': rating})

            try: votes = client.parseDOM(item, 'RatingCount')[0]
            except: votes = '0'
            if votes == '': votes = '0'
            votes = client.replaceHTMLCodes(votes)
            votes = utils.py2_encode(votes)
            if not votes == '0': meta.update({'votes': votes})

            try: mpaa = client.parseDOM(item, 'ContentRating')[0]
            except: mpaa = ''
            if mpaa == '': mpaa = '0'
            mpaa = client.replaceHTMLCodes(mpaa)
            mpaa = utils.py2_encode(mpaa)
            if not mpaa == '0': meta.update({'mpaa': mpaa})

            try: cast = client.parseDOM(item, 'Actors')[0]
            except: cast = ''
            cast = [x for x in cast.split('|') if not x == '']
            try: cast = [(utils.py2_encode(x), '') for x in cast]
            except: cast = []
            if cast == []: cast = '0'
            if not cast == '0': meta.update({'cast': cast})

            try: label = client.parseDOM(item2, 'SeriesName')[0]
            except: label = '0'
            label = client.replaceHTMLCodes(label)
            label = utils.py2_encode(label)
            if not nabel == '0': meta.update({'label': label})

            try: plot = client.parseDOM(item2, 'Overview')[0]
            except: plot = ''
            if plot == '': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = utils.py2_encode(plot)
            if not plot == '0': meta.update({'plot': plot})
        except:
            pass


        try:
            premiered = client.parseDOM(item, 'FirstAired')[0]
            if premiered == '' or '-00' in premiered: premiered = '0'
            premiered = client.replaceHTMLCodes(premiered)
            premiered = utils.py2_encode(premiered)
            if not premiered == '0': meta.update({'premiered': premiered})

            season = '%01d' % int(act_season)
            season = utils.py2_encode(season)

            thumb = [i for i in artwork if client.parseDOM(i, 'Season')[0] == season]
            try: thumb = client.parseDOM(thumb[0], 'BannerPath')[0]
            except: thumb = ''
            if not thumb == '': thumb = self.tvdb_image + thumb
            else: thumb = '0'
            thumb = client.replaceHTMLCodes(thumb)
            thumb = utils.py2_encode(thumb)

            if thumb == '0': thumb = poster
            if not thumb == '0': meta.update({'thumb': thumb})

        except:
            pass
        return meta
