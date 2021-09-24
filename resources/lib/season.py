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


import os,sys,re,json,zipfile,StringIO,urllib,urllib2,urlparse,base64,datetime

from resources.lib import control
from resources.lib import client
from resources.lib import cache



class seasons:
    def __init__(self):
        self.lang = 'hu'
        self.tvdb_key = base64.urlsafe_b64decode('MjgyM0VEMTNCQkVERURDOA==')

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
                name = name.encode('utf-8')
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

            zip = zipfile.ZipFile(StringIO.StringIO(data))
            result = zip.read('%s.xml' % 'en')
            artwork = zip.read('banners.xml')
            zip.close()

            dupe = client.parseDOM(result, 'SeriesName')[0]
            dupe = re.compile('[***]Duplicate (\d*)[***]').findall(dupe)

            if len(dupe) > 0:
                tvdb = str(dupe[0]).encode('utf-8')

                url = self.tvdb_info_link % (tvdb, 'en')
                data = urllib2.urlopen(url, timeout=30).read()

                zip = zipfile.ZipFile(StringIO.StringIO(data))
                result = zip.read('%s.xml' % 'en')
                artwork = zip.read('banners.xml')
                zip.close()

            if not self.lang == 'en':
                url = self.tvdb_info_link % (tvdb, self.lang)
                data = urllib2.urlopen(url, timeout=30).read()

                zip = zipfile.ZipFile(StringIO.StringIO(data))
                result2 = zip.read('%s.xml' % self.lang)
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
            poster = poster.encode('utf-8')

            try: banner = client.parseDOM(item, 'banner')[0]
            except: banner = ''
            if not banner == '': banner = self.tvdb_image + banner
            else: banner = '0'
            banner = client.replaceHTMLCodes(banner)
            banner = banner.encode('utf-8')

            try: fanart = client.parseDOM(item, 'fanart')[0]
            except: fanart = ''
            if not fanart == '': fanart = self.tvdb_image + fanart
            else: fanart = '0'
            fanart = client.replaceHTMLCodes(fanart)
            fanart = fanart.encode('utf-8')
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
            genre = genre.encode('utf-8')
            if not genre == '0': meta.update({'genre': genre})

            try: duration = client.parseDOM(item, 'Runtime')[0]
            except: duration = ''
            if duration == '': duration = '0'
            duration = client.replaceHTMLCodes(duration)
            duration = duration.encode('utf-8')
            if not duration == '0' and meta['duration'] =='0': meta.update({'duration': duration})

            try: rating = client.parseDOM(item, 'Rating')[0]
            except: rating = ''
            if rating == '': rating = '0'
            rating = client.replaceHTMLCodes(rating)
            rating = rating.encode('utf-8')
            if not rating == '0': meta.update({'rating': rating})

            try: votes = client.parseDOM(item, 'RatingCount')[0]
            except: votes = '0'
            if votes == '': votes = '0'
            votes = client.replaceHTMLCodes(votes)
            votes = votes.encode('utf-8')
            if not votes == '0': meta.update({'votes': votes})

            try: mpaa = client.parseDOM(item, 'ContentRating')[0]
            except: mpaa = ''
            if mpaa == '': mpaa = '0'
            mpaa = client.replaceHTMLCodes(mpaa)
            mpaa = mpaa.encode('utf-8')
            if not mpaa == '0': meta.update({'mpaa': mpaa})

            try: cast = client.parseDOM(item, 'Actors')[0]
            except: cast = ''
            cast = [x for x in cast.split('|') if not x == '']
            try: cast = [(x.encode('utf-8'), '') for x in cast]
            except: cast = []
            if cast == []: cast = '0'
            if not cast == '0': meta.update({'cast': cast})

            try: label = client.parseDOM(item2, 'SeriesName')[0]
            except: label = '0'
            label = client.replaceHTMLCodes(label)
            label = label.encode('utf-8')
            if not nabel == '0': meta.update({'label': label})

            try: plot = client.parseDOM(item2, 'Overview')[0]
            except: plot = ''
            if plot == '': plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
            if not plot == '0': meta.update({'plot': plot})
        except:
            pass


        try:
            premiered = client.parseDOM(item, 'FirstAired')[0]
            if premiered == '' or '-00' in premiered: premiered = '0'
            premiered = client.replaceHTMLCodes(premiered)
            premiered = premiered.encode('utf-8')
            if not premiered == '0': meta.update({'premiered': premiered})

            season = '%01d' % int(act_season)
            season = season.encode('utf-8')

            thumb = [i for i in artwork if client.parseDOM(i, 'Season')[0] == season]
            try: thumb = client.parseDOM(thumb[0], 'BannerPath')[0]
            except: thumb = ''
            if not thumb == '': thumb = self.tvdb_image + thumb
            else: thumb = '0'
            thumb = client.replaceHTMLCodes(thumb)
            thumb = thumb.encode('utf-8')

            if thumb == '0': thumb = poster
            if not thumb == '0': meta.update({'thumb': thumb})

        except:
            pass
        return meta
