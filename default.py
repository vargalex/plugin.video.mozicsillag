# -*- coding: utf-8 -*-
import xbmc, xbmcgui, urllib, urlparse, json, re, xbmcplugin, os, base64, datetime
from resources.lib import client, control, cache, metacache
from resources.lib.BeautifulSoup import BeautifulStoneSoup
import urlresolver

current_year = datetime.datetime.now().strftime("%Y")

REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        sys.path.append("C:\\Users\\User\\.p2\\pool\\plugins\\org.python.pydev_4.4.0.201510052309\\pysrc")
        import pydevd # with the addon script.module.pydevd, only use `import pydevd`
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)


csillag_url = control.setting('mcs_url')
addon_handle = int(sys.argv[1])

def just_removed():
    control.infoDialog(u'A keresett vide\u00F3t elt\u00E1vol\u00EDtott\u00E1k!')
    return

def setviewmode(mode):
    mainview = int(control.setting('mainview'))
    streamview = int(control.setting('streamview'))

    if mode == 'main_folder':
        if mainview == 1:
            mainview = 502
        elif mainview == 2:
            mainview = 51
        elif mainview == 3:
            mainview = 500
        elif mainview == 4:
            mainview = 501
        elif mainview == 5:
            mainview = 508
        elif mainview == 6:
            mainview = 504
        elif mainview == 7:
            mainview = 503
        elif mainview == 8:
            mainview = 515    
        else:
            mainview = 0
        return(mainview)
        #xbmc.executebuiltin('Container.SetViewMode(%s)' %mainview)
    elif mode == 'movie_folder':
        if streamview == 1:
            streamview = 502
        elif streamview == 2:
            streamview = 51
        elif streamview == 3:
            streamview = 500
        elif streamview == 4:
            streamview = 501
        elif streamview == 5:
            streamview = 508
        elif streamview == 6:
            streamview = 504
        elif streamview == 7:
            streamview = 503
        elif streamview == 8:
            streamview = 515
        else:
            streamview = 0
        return(streamview)            
        #xbmc.executebuiltin('Container.SetViewMode(%s)' %streamview)
 
    return

def rootFolder():
    addDir('Filmek',                     'filmek-online', 1, '', '', 'film', 1, '', '', '','','')
    addDir('Sorozatok',                  'sorozatok-online', 1, '', '', 'sorozat', 1, '', '', '','','')
    addDir('Keresés',                    '', 7, '', '', '', 1, '', '', '','','')
    return

def categoryFolder():
    addDir('Legfrissebb',                url, 2, '', '', description, 1, '/legfrissebb', '', 'not', '','')
    addDir('Legnézettebb',               url, 2, '', '', description, 1, '/legnezettebb', '', 'not', '','')
    addDir('Legjobbra értékelt',         url, 2, '', '', description, 1, '/legjobbra-ertekelt', '', 'not', '','')
    addDir('Kategóriák',                 url, 12, '', '', description, 1, '', '', '', '','')
    return

def searchFolder():
    addDir('Filmek',                    '', 5, '', '', 'film', 1, '', '', '','','')
    addDir('Sorozatok',                    '', 5, '', '', 'sorozat', 1, '', '', '','','')

def listak():     
    i = urlparse.urljoin(csillag_url, url + category + '?page=' + str(page))
    items, next = getMovies(i)
    listMovies(items, description)
    if next == True:
        addDir('[COLOR green]Következő oldal[/COLOR]', url, 2, '', '', description, page + 1, category, '', '', '','')

    viewmode = setviewmode('main_folder')
    if viewmode != 0:
        xbmc.executebuiltin('Container.SetViewMode(%s)' %viewmode)
    return

def kategoriak():
    if description == 'film':
        url2 = 'filmek-online/'
    else:
        url2 = 'sorozatok-online/'
    i = client.request(csillag_url)
    r = client.parseDOM(i, 'ul', {'class': 'dropdown dropdown-wrapper'})
    r = [i for i in r if url2 in i]
    links = client.parseDOM(r, 'a', ret='href')
    genres = client.parseDOM(r, 'strong')
    result = zip(genres, links)
    for i in result:
        title = BeautifulStoneSoup(i[0], convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        title = (title.text).encode("UTF-8")
        addDir(title, i[1], 2, '', '', description, 1, '', '', '', '', '')
    return
    

def kereses(search_text, page, description):
    type = '1' if description == 'film' else '0'
    search_url = 'search_term=' + search_text + '&search_type=' + type + '&search_where=0&search_rating_start=1&search_rating_end=10&search_year_from=1900&search_year_to=' + current_year
    search_url = base64.b64encode(search_url)
    query = urlparse.urljoin(csillag_url, '/kereses/' + search_url + '?page=' + str(page))
    items, next = getMovies(query)
    listMovies(items, description)

    if next == True:
        addDir('[COLOR green]Következő oldal[/COLOR]', '', 6, '', '', description, page + 1, search_text, '', '', '','')

    viewmode = setviewmode('main_folder')
    if viewmode != 0:
        xbmc.executebuiltin('Container.SetViewMode(%s)' %viewmode)
    return

def forrasok_Film():
    hosts, youtube_id, meta = getMoviesource(url, name, iconimage)
    if len(hosts) == 0: return
    hostDict = getConstants()
    
    if not youtube_id == '0':
        addFile('[COLOR orange]' + name + ' - ' + 'ELŐZETES''[/COLOR]', youtube_id, 13, {'title': name, 'thumb': meta['thumb'], 'fanart': meta['fanart'], 'plot': meta['plot']})
    
    for item in hosts:
        try:
            link = client.parseDOM(item, 'a', ret='href')[-1]           
            link = urlparse.urljoin(meta['url'], link)
            host = client.parseDOM(item, 'a', ret='title')[0]
            quality = host.split()[2]         
            host = host.split()[0]
            if '/HU.png' in item: lang = '[COLOR green]SZINKRON[/COLOR]'
            elif '/EN_HU.png' or '/SUB_HU.png' in item: lang = '[COLOR red]FELIRAT[/COLOR]'
            elif '/EN.png' or '/SUB_EN.png' or '/MAS.png' in item: lang = '[COLOR yellow]NINCS FELIRAT[/COLOR]'
            if host.lower().split('.')[0] in hostDict:
                addFile('[COLOR blue]' + (quality.upper()).encode('utf-8') + '[/COLOR]' + ' | ' + lang + ' | ' + (host.upper()).encode('utf-8'), link, 4, meta)
        except:
            pass
        
    viewmode = setviewmode('movie_folder')
    if viewmode != 0:
        xbmc.executebuiltin('Container.SetViewMode(%s)' %viewmode)
    return

def getMoviesource(url, title, poster):
    result = client.request(url)
    
    try: plot = (client.parseDOM(result, 'p')[0]).replace('\n','').strip()
    except: plot = '0'
    plot = BeautifulStoneSoup(plot, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    plot = (plot.text).encode("UTF-8")
    
    try: imdb_id = re.compile('imdb.com/title/(tt[0-9]+)').findall(result)[0]
    except: imdb_id = '0'
    
    try:
        youtube_id = client.parseDOM(result, 'div', attrs={'class': 'flex-video'})[0]
        youtube_id = re.compile('youtube.com/v|embed/(.+?(?=\?|"|\'))').findall(youtube_id)[0]
    except: youtube_id = '0'
    
    try:
        duration = client.parseDOM(result, 'ul', attrs={'class': 'small-block-grid-2 movie-details'})[0]
        duration = client.parseDOM(duration, 'li')[0]
        duration = int(re.compile('([0-9]+)\s*?perc').findall(duration)[0]) * 60
        duration = str(duration)
    except: duration = '0'
    
    hosts = []      
    try:
        hosts_url = client.parseDOM(result, 'div', attrs={'class': 'small-12 medium-7 small-centered columns'})[0]    
        hosts_url = client.parseDOM(hosts_url, 'a', ret='href')[0]    
        hosts = client.request(hosts_url)
        hosts = client.parseDOM(hosts, 'div', attrs={'class': 'links_holder.*?'})[0]
        hosts = client.parseDOM(hosts, 'div', attrs={'class': 'panel'})
        filter = []
        filter += [i for i in hosts if 'DVDRip' in i]
        filter += [i for i in hosts if 'TVRip' in i]
        filter += [i for i in hosts if (not 'TVRip' in i) and (not 'DVDRip' in i)]
        hosts = filter
        
        filter = []
        filter += [i for i in hosts if '/HU.png' in i]
        filter += [i for i in hosts if ('/EN_HU.png' in i) or ('/SUB_HU.png' in i)]
        filter += [i for i in hosts if ('/EN.png' in i) or ('/SUB_EN.png' in i) or ('/MAS.png' in i)]
        hosts = filter
    except:
        pass  
    
    parsed = urlparse.urlparse(hosts_url)
    domain = parsed.scheme + "://" + parsed.netloc
    
    meta = {'imdb': imdb_id, 'plot': plot, 'duration': duration, 'title': name, 'label': name, 'poster': poster, 'fanart': poster, 'thumb': poster, 'url': domain}
    try:
        meta = metacache.get(get_meta, 720, meta, 'movie')
    except: pass
    
    return (hosts, youtube_id, meta)

def forrasok_Sorozat():
    hostDict = getConstants()
    metadata = json.loads(meta)
    
    hosts = client.parseDOM(url, 'div', attrs={'class': 'panel\s*?'})
    filter = []
    filter += [i for i in hosts if 'DVDRip' in i]
    filter += [i for i in hosts if 'TVRip' in i]
    filter += [i for i in hosts if (not 'TVRip' in i) and (not 'DVDRip' in i)]
    hosts = filter
    
    filter = []
    filter += [i for i in hosts if '/HU.png' in i]
    filter += [i for i in hosts if ('/EN_HU.png' in i) or ('/SUB_HU.png' in i)]
    filter += [i for i in hosts if ('/EN.png' in i) or ('/SUB_EN.png' in i) or ('/MAS.png' in i)]
    hosts = filter

    for item in hosts:
        try:
            link = client.parseDOM(item, 'a', ret='href')[-1]           
            link = urlparse.urljoin(metadata['url'], link)
            host = client.parseDOM(item, 'a', ret='title')[0]
            quality = host.split()[2]         
            host = host.split()[0]
            if '/HU.png' in item: lang = '[COLOR green]SZINKRON[/COLOR]'
            elif '/EN_HU.png' or '/SUB_HU.png' in item: lang = '[COLOR red]FELIRAT[/COLOR]'
            elif '/EN.png' or '/SUB_EN.png' or '/MAS.png' in item: lang = '[COLOR yellow]NINCS FELIRAT[/COLOR]'
            if host.lower().split('.')[0] in hostDict:
                addFile('[COLOR blue]' + (quality.upper()).encode('utf-8') + '[/COLOR]' + ' | ' + lang + ' | ' + (host.upper()).encode('utf-8'), link, 4, metadata)
        except:
            pass
                
    viewmode = setviewmode('movie_folder')
    if viewmode != 0:
        xbmc.executebuiltin('Container.SetViewMode(%s)' %viewmode)
    return


def open_search_panel():
    search_text = ''
    keyb = xbmc.Keyboard('' , 'Keresés')
    keyb.doModal()
 
    if (keyb.isConfirmed()):
        search_text = keyb.getText()
        kereses(search_text, 1, description)
        return
    
##########

def getMovies(url):
    result = client.request(url)
    items = client.parseDOM(result, 'div', attrs={'class': 'large-12 columns'})[0]
    items = client.parseDOM(items, 'li')
    items = [i for i in items if 'movie-holder' in i]
    try:
        if not "(0)'>&raquo;<" in client.parseDOM(result, 'ul', attrs={'class': 'pagination'})[0]: next = True
        else: next = False
    except: next = False
    return (items, next)

def listMovies(items, type):
    for item in items:
        try:
            link = client.parseDOM(item, 'a', ret='href')[0]
            img = client.parseDOM(item, 'div', attrs={'class': 'image'})[0]
            img = client.parseDOM(img, 'img', ret='data-original')[0]
            img = urlparse.urljoin(csillag_url, img)
            if type == 'film':
                title = client.parseDOM(item, 'div', attrs={'class': 'cover-surface'})[0]
                title = client.parseDOM(title, 'strong')[0]
                title = BeautifulStoneSoup(title, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
                title = (title.text).encode("UTF-8")
                addDir(title, link, 3, img, control.addonFanart(), '', 1, '', '', '', '','')
            elif type == 'sorozat':
                title = client.parseDOM(item, 'div', attrs={'class': 'title'})[0]
                title = (client.parseDOM(title, 'h2')[0]).replace('\n','').strip()
                title = BeautifulStoneSoup(title, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
                title = (title.text).encode("UTF-8")
                title = re.compile('(.*)\:\s(.*)').findall(title)[0]
                addDir(title[0]  + ' : ' + '[COLOR yellow]' + title[1] + '[/COLOR]', link, 9, img, control.addonFanart(), '', 1, '', '', '', title[0],'')       
        except:
            pass
    return

def Episodes():
    try:
        try: season = re.compile('\]([0-9]+).*?évad').findall(name)[0]
        except: season= '1'
        episodes, youtube_id, meta = getEpisodes(url, season, iconimage)
        if len(episodes) == 0: return
        
        if not youtube_id == '0':
            addFile('[COLOR orange]' + name + ' - ' + 'ELŐZETES''[/COLOR]', youtube_id, 13, {'title': name, 'thumb': meta['thumb'], 'fanart': meta['fanart'], 'plot': meta['plot']})
        
        for item in episodes:
            try:
                episode = re.compile('>\s*?Epiz.*?([0-9]+)\s*?<').findall(item)[0]
                try:
                    meta2 = metacache.get(get_meta, 720, meta, 'episodes', episode)
                except:
                    pass
                if not 'label' in meta2: meta2['label'] = meta2['title']
                if meta2['label'] == '0':
                        label = '%sx%02d . %s %s' % (meta2['season'], int(episode), 'Epizod', episode)
                else:
                    label = '%sx%02d . %s' % (meta2['season'], int(episode), meta2['label'])
                addDir2(label, item.encode('utf-8'), 10, meta2)
            except:
                pass
        
        viewmode = setviewmode('movie_folder')
        if viewmode != 0:
            xbmc.executebuiltin('Container.SetViewMode(%s)' %viewmode)
        return
    except:
        return


def getEpisodes(url, season, poster):
    result = client.request(url)
    
    try: plot = (client.parseDOM(result, 'p')[0]).replace('\n','').strip()
    except: plot = '0'
    plot = BeautifulStoneSoup(plot, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    plot = (plot.text).encode("UTF-8")

    try: imdb_id = re.compile('imdb.com/title/(tt[0-9]+)').findall(result)[0]
    except: imdb_id = '0'
    
    try:
        youtube_id = client.parseDOM(result, 'div', attrs={'class': 'flex-video'})[0]
        youtube_id = re.compile('youtube.com/v|embed/(.+?(?=\?|"|\'))').findall(youtube_id)[0]
    except: youtube_id = '0'
    
    try:
        duration = client.parseDOM(result, 'ul', attrs={'class': 'small-block-grid-2 movie-details'})[0]
        duration = client.parseDOM(duration, 'li')[0]
        duration = int(re.compile('([0-9]+)\s*?perc').findall(duration)[0]) * 60
        duration = str(duration)
    except: duration = '0'

    episodes = []
    try:
        hosts_url = client.parseDOM(result, 'div', attrs={'class': 'small-12 medium-7 small-centered columns'})[0]
        hosts_url = client.parseDOM(hosts_url, 'a', ret='href')[0]    
        episodes = client.request(hosts_url)
        episodes = client.parseDOM(episodes, 'div', attrs={'class': 'links_holder.*?'})[0]
        episodes = client.parseDOM(episodes, 'div', attrs={'class': 'accordion-episodes.*?'})
    except:
        pass

    parsed = urlparse.urlparse(hosts_url)
    domain = parsed.scheme + "://" + parsed.netloc

    meta = {'imdb': imdb_id, 'plot': plot, 'duration': duration, 'title': title, 'label': title, 'poster': poster, 'fanart': poster, 'thumb': poster, 'season': season, 'url': domain}

    try:
        meta = metacache.get(get_meta, 720, meta, 'season', season)
    except:
        pass
    return (episodes, youtube_id, meta)
    
    
def youtube_trailer():
    metadata = json.loads(meta)
    label = metadata['title']
    thumbnailimage = metadata['thumb']
    direct_url = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + url
    videoitem = xbmcgui.ListItem(label=label, thumbnailImage=iconimage)
    videoitem.setInfo(type='Video', infoLabels= metadata)
    xbmc.Player().play(direct_url, videoitem)   
    return

##########
def getvideo():
    metadata = json.loads(meta)
    label = metadata['label']
    thumbnailimage = metadata['thumb']
    domain = metadata['url']
    videoitem = xbmcgui.ListItem(label=label, thumbnailImage=thumbnailimage)
    videoitem.setInfo(type='Video', infoLabels=metadata)
    try:
        xbmc.Player().play(getMovieUrl(url, domain), videoitem)
    except:
        just_removed()


def getMovieUrl(url, domain):
    try:
        control.busy()
        result = client.request(url)

        top_url = []
        try:
            top_url = client.parseDOM(result, 'div', attrs={'id': 'video-holder'})
            if len(top_url) == 0: raise Exception()
            try: top_url = client.parseDOM(top_url, 'iframe', ret='src')[0]
            except: top_url = client.parseDOM(top_url, 'IFRAME', ret='SRC')[0]
        except:
            pass
        
        if top_url == []:
            try:
                result = client.request(url, output='geturl')
                if not domain in result: top_url = result
            except:
                pass
        if top_url == [] or top_url == None: raise Exception()
        direct_url = urlresolver.resolve(top_url)
        if isinstance(direct_url, basestring):
            control.idle()
            return direct_url
        else:
            control.idle()
            just_removed()
    except: 
        control.idle()
        just_removed()
##########


def getConstants():
        try:
            try: hosts = urlresolver.relevant_resolvers(order_matters=True)
            except: hosts = urlresolver.plugnplay.man.implementors(urlresolver.UrlResolver)
            hostDict = [i.domains for i in hosts if not '*' in i.domains]
            hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
            hostDict = [i.split('.')[0] for i in hostDict]
            hostDict = list(set(hostDict))
        except:
            hostDict = []
        return hostDict


def get_meta(meta, type, tvshow=None):
    if type == 'movie': 
        from resources.lib.movies import movies
        return movies().super_info(meta)
    elif type == 'season': 
        from resources.lib.season import seasons
        return seasons().tvdb_list(meta, tvshow)
    elif type == 'episodes':
        from resources.lib.episodes import seasons
        return seasons().tvdb_list(meta, tvshow)


def addDir(name, url, mode, iconimage, fanart, description, page, category, year, genre, title, orig_title):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&category="+str(category)+"&page="+str(page)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)+"&year="+urllib.quote_plus(year)+"&genre="+urllib.quote_plus(genre)+"&title="+urllib.quote_plus(title)+"&orig_title="+urllib.quote_plus(orig_title)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage})
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description, "Year": year, "Genre": genre } )
    liz.setProperty( "Fanart_Image", fanart )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmcplugin.setContent(addon_handle, 'movies')
    return ok

def addDir2(name, url, mode, meta):
    try: poster = meta['poster']
    except: poster = ''
    sysmeta = urllib.quote_plus(json.dumps(meta))
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&meta="+sysmeta
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=meta['thumb'], thumbnailImage=meta['thumb'])
    liz.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
    liz.setInfo( type="Video", infoLabels= meta )
    if 'fanart' in meta and not meta['fanart'] == '0':
        liz.setProperty('Fanart_Image', meta['fanart'])
    else:
        liz.setProperty('Fanart_Image', control.addonFanart())
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    if 'season' in meta:
        xbmcplugin.setContent(addon_handle, 'episodes')
    else:
        xbmcplugin.setContent(addon_handle, 'movies')
    return ok

def addFile(name, url, mode, meta):
    try: poster = meta['poster']
    except: poster = ''
    sysmeta = urllib.quote_plus(json.dumps(meta))
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&meta="+sysmeta
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=meta['thumb'], thumbnailImage=meta['thumb'])
    liz.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
    liz.setInfo( type="Video", infoLabels= meta )
    liz.setProperty('Video', 'true')
    if 'fanart' in meta and not meta['fanart'] == '0':
        liz.setProperty('Fanart_Image', meta['fanart'])
    else:
        liz.setProperty('Fanart_Image', control.addonFanart())
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    if 'season' in meta:
        xbmcplugin.setContent(addon_handle, 'episodes')
    else:
        xbmcplugin.setContent(addon_handle, 'movies')
    return ok

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

params = get_params()
url = None
name = None
mode = None
iconimage = None
fanart = None
description = None
meta = None
page = 0
category = ''
search_text = ''

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    title = urllib.unquote_plus(params["title"])
except:
    pass
try:
    iconimage = urllib.unquote_plus(params["iconimage"])
except:
    pass
try:        
    mode = int(params["mode"])
except:
    pass
try:        
    page = int(params["page"])
except:
    pass
try:        
    fanart = urllib.unquote_plus(params["fanart"])
except:
    pass
try:        
    description = urllib.unquote_plus(params["description"])
except:
    pass
try:        
    category = urllib.unquote_plus(params["category"])
except:
    pass
try:        
    search_text = urllib.unquote_plus(params["category"])
except:
    pass
try:        
    host = urllib.unquote_plus(params["host"])
except:
    pass
try:        
    year = urllib.unquote_plus(params["year"])
except:
    pass
try:        
    genre = urllib.unquote_plus(params["genre"])
except:
    pass
try:        
    season = urllib.unquote_plus(params["season"])
except:
    pass
try:        
    orig_title = urllib.unquote_plus(params["orig_title"])
except:
    pass
try:
    meta = urllib.unquote_plus(params["meta"])
except:
    pass

if mode == None:
    rootFolder()
elif mode == 1:
    categoryFolder()
elif mode == 2:
    listak()
elif mode == 3:
    forrasok_Film()
elif mode == 4:
    getvideo()
elif mode == 5:
    open_search_panel()
elif mode == 6:
    kereses(search_text, page, description)
elif mode == 7:
    searchFolder()
elif mode == 9:
    Episodes()
elif mode == 10:
    forrasok_Sorozat()
elif mode == 12:
    kategoriak()
elif mode == 13:
    youtube_trailer()
elif mode == 14:
    cache.clear()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
