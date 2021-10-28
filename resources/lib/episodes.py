# -*- coding: utf-8 -*-

import os,sys,re,zipfile #,StringIO,urllib2
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
        self.tvdb_key = '2823ED13BBEDEDC8'
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/all/%s.zip' % (self.tvdb_key, '%s', '%s')
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.tvdb_poster = 'http://thetvdb.com/banners/_cache/'


    def tvdb_list(self, meta, episode):
        imdb = meta['imdb']
        meta.update({'episode': episode})
        try:
            if not imdb == '0':
                url = self.tvdb_by_imdb % imdb

                result = client.request(url, timeout='10')
    
                try: tvdb = client.parseDOM(result, 'seriesid')[0]
                except: tvdb = '0'
    
                try: name = client.parseDOM(result, 'SeriesName')[0]
                except: name = '0'
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
    
            url = self.tvdb_info_link % (tvdb, 'hu')
            data = urllib2.urlopen(url, timeout=30).read()
            zip = zipfile.ZipFile(StringIO(data))
            result2 = zip.read('%s.xml' % 'hu').decode()
            zip.close()


            artwork = artwork.split('<Banner>')
            artwork = [i for i in artwork if '<Language>en</Language>' in i and '<BannerType>season</BannerType>' in i]
            artwork = [i for i in artwork if not 'seasonswide' in re.findall('<BannerPath>(.+?)</BannerPath>', i)[0]]


            result = result.split('<Episode>')
            result2 = result2.split('<Episode>')

            item = result[0] ; item2 = result2[0]

            episode = [i for i in result if '<EpisodeNumber>' in i]
            episode = [i for i in episode if '<SeasonNumber>%01d</SeasonNumber>' % int(meta['season']) in i]
            item = [i for i in episode if '<EpisodeNumber>%01d</EpisodeNumber>' % int(meta['episode']) in i]


            locals = [i for i in result2 if '<EpisodeNumber>' in i]

            result = '' ; result2 = ''
        except:
            pass
        
        try:
            if len(item) == 1: item = item[0]
            premiered = client.parseDOM(item, 'FirstAired')[0]
            if premiered == '' or '-00' in premiered: premiered = '0'
            premiered = client.replaceHTMLCodes(premiered)
            premiered = utils.py2_encode(premiered)
            if not premiered == '0': meta.update({'premiered': premiered})

            title = client.parseDOM(item, 'EpisodeName')[0]
            if title == '': title = '0'
            title = client.replaceHTMLCodes(title)
            title = utils.py2_encode(title)
            if not title == '0': meta.update({'title': title})

            try: thumb = client.parseDOM(item, 'filename')[0]
            except: thumb = ''
            if not thumb == '': thumb = self.tvdb_image + thumb
            else: thumb = '0'
            thumb = client.replaceHTMLCodes(thumb)
            thumb = utils.py2_encode(thumb)
            if not thumb == '0': meta.update({'thumb': thumb})

            try: rating = client.parseDOM(item, 'Rating')[0]
            except: rating = ''
            if rating == '': rating = '0'
            rating = client.replaceHTMLCodes(rating)
            rating = utils.py2_encode(rating)
            if not rating == '0': meta.update({'rating': rating})

            try: director = client.parseDOM(item, 'Director')[0]
            except: director = ''
            director = [x for x in director.split('|') if not x == '']
            director = ' / '.join(director)
            if director == '': director = '0'
            director = client.replaceHTMLCodes(director)
            director = utils.py2_encode(director)
            if not director == '0': meta.update({'director': director})

            try: writer = client.parseDOM(item, 'Writer')[0]
            except: writer = ''
            writer = [x for x in writer.split('|') if not x == '']
            writer = ' / '.join(writer)
            if writer == '': writer = '0'
            writer = client.replaceHTMLCodes(writer)
            writer = utils.py2_encode(writer)
            if not writer == '0': meta.update({'writer': writer})

            try:
                local = client.parseDOM(item, 'id')[0]
                local = [x for x in locals if '<id>%s</id>' % str(local) in x][0]
            except:
                local = item

            label = client.parseDOM(local, 'EpisodeName')[0]
            if label == '': label = '0'
            label = client.replaceHTMLCodes(label)
            label = utils.py2_encode(label)
            if not label == '0': 
                meta.update({'label': label})
                meta.update({'title': label})


            try: episodeplot = client.parseDOM(local, 'Overview')[0]
            except: episodeplot = ''
            if episodeplot == '': episodeplot = '0'
            episodeplot = client.replaceHTMLCodes(episodeplot)
            try: episodeplot = utils.py2_encode(episodeplot)
            except: pass
            if not episodeplot == '0': meta.update({'plot': episodeplot})

        except:
            pass

        return meta
