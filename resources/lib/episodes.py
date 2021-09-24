# -*- coding: utf-8 -*-

import os,sys,re,zipfile,StringIO,urllib2,base64

from resources.lib import control
from resources.lib import client
from resources.lib import cache


class seasons:
    def __init__(self):
        self.tvdb_key = base64.urlsafe_b64decode('MjgyM0VEMTNCQkVERURDOA==')
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
    
            url = self.tvdb_info_link % (tvdb, 'hu')
            data = urllib2.urlopen(url, timeout=30).read()
                    
            zip = zipfile.ZipFile(StringIO.StringIO(data))
            result2 = zip.read('%s.xml' % 'hu')
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
            premiered = premiered.encode('utf-8')
            if not premiered == '0': meta.update({'premiered': premiered})

            title = client.parseDOM(item, 'EpisodeName')[0]
            if title == '': title = '0'
            title = client.replaceHTMLCodes(title)
            title = title.encode('utf-8')
            if not title == '0': meta.update({'title': title})

            try: thumb = client.parseDOM(item, 'filename')[0]
            except: thumb = ''
            if not thumb == '': thumb = self.tvdb_image + thumb
            else: thumb = '0'
            thumb = client.replaceHTMLCodes(thumb)
            thumb = thumb.encode('utf-8')
            if not thumb == '0': meta.update({'thumb': thumb})

            try: rating = client.parseDOM(item, 'Rating')[0]
            except: rating = ''
            if rating == '': rating = '0'
            rating = client.replaceHTMLCodes(rating)
            rating = rating.encode('utf-8')
            if not rating == '0': meta.update({'rating': rating})

            try: director = client.parseDOM(item, 'Director')[0]
            except: director = ''
            director = [x for x in director.split('|') if not x == '']
            director = ' / '.join(director)
            if director == '': director = '0'
            director = client.replaceHTMLCodes(director)
            director = director.encode('utf-8')
            if not director == '0': meta.update({'director': director})

            try: writer = client.parseDOM(item, 'Writer')[0]
            except: writer = ''
            writer = [x for x in writer.split('|') if not x == '']
            writer = ' / '.join(writer)
            if writer == '': writer = '0'
            writer = client.replaceHTMLCodes(writer)
            writer = writer.encode('utf-8')
            if not writer == '0': meta.update({'writer': writer})

            try:
                local = client.parseDOM(item, 'id')[0]
                local = [x for x in locals if '<id>%s</id>' % str(local) in x][0]
            except:
                local = item

            label = client.parseDOM(local, 'EpisodeName')[0]
            if label == '': label = '0'
            label = client.replaceHTMLCodes(label)
            label = label.encode('utf-8')
            if not label == '0': 
                meta.update({'label': label})
                meta.update({'title': label})


            try: episodeplot = client.parseDOM(local, 'Overview')[0]
            except: episodeplot = ''
            if episodeplot == '': episodeplot = '0'
            episodeplot = client.replaceHTMLCodes(episodeplot)
            try: episodeplot = episodeplot.encode('utf-8')
            except: pass
            if not episodeplot == '0': meta.update({'plot': episodeplot})

        except:
            pass

        return meta
