# -*- coding: utf-8 -*-
import xbmc, xbmcgui, json, re, xbmcplugin, os, base64, datetime, locale
from resources.lib import client, control, cache, metacache, utils
import resolveurl

if sys.version_info[0] == 3:
    import urllib.parse as urlparse
    from urllib.parse import quote_plus
    from urllib.parse import unquote_plus
    from functools import reduce
else:
    import urlparse
    from urllib import quote_plus
    from urllib import unquote_plus

current_year = datetime.datetime.now().strftime("%Y")

csillag_url = control.setting('mcs_url')
addon_handle = int(sys.argv[1])

base_path = utils.py2_decode(control.transPath(control.addonInfo('profile')))

try:
    locale.setlocale(locale.LC_ALL, "")
except:
    pass

def just_removed():
    control.infoDialog('A keresett videót eltávolították, vagy sikertelen a resolveURL feloldás!')
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
    addDir('Filmek', 'filmek-online', 1, '', '', 'film', 1, '', '', '','','')
    addDir('Sorozatok', 'sorozatok-online', 1, '', '', 'sorozat', 1, '', '', '','','')
    addDir('Keresés', '', 7, '', '', '', 1, '', '', '','','')
    return

def categoryFolder():
    addDir('Legfrissebb', url, 2, '', '', description, 1, '/legfrissebb', '', 'not', '','')
    addDir('Legnézettebb', url, 2, '', '', description, 1, '/legnezettebb', '', 'not', '','')
    addDir('Legjobbra értékelt', url, 2, '', '', description, 1, '/legjobbra-ertekelt', '', 'not', '','')
    addDir('Kategóriák', url, 12, '', '', description, 1, '', '', '', '','')
    return

def searchFolder():
    addDir('Filmek', '', 5, '', '', 'film', 1, '', '', '','','')
    addDir('Sorozatok', '', 5, '', '', 'sorozat', 1, '', '', '','','')

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
        title = client.replaceHTMLCodes(i[0])
        title = utils.py2_encode(title)
        addDir(title, i[1], 2, '', '', description, 1, '', '', '', '', '')
    return
    

def kereses(search_text, page, description):
    type = '1' if description == 'film' else '0'
    search_url = 'search_term=' + search_text + '&search_type=' + type + '&search_where=0&search_rating_start=1&search_rating_end=10&search_year_from=1900&search_year_to=' + current_year
    search_url = base64.b64encode(search_url.encode()).decode()
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
    if not youtube_id == '0':
        addFile('[COLOR orange]' + name + ' - ' + 'ELŐZETES''[/COLOR]', youtube_id, 13, {'title': name, 'thumb': meta['thumb'], 'fanart': meta['fanart'], 'plot': meta['plot']})
    
    for item in hosts:
        try:
            link = client.parseDOM(item, 'a', ret='href')[-1]           
            host = client.parseDOM(item, 'span')[0]
            quality = host.split()[2]         
            host = host.split()[0]
            if '/HU.png' in item: lang = '[COLOR green]SZINKRON[/COLOR]'
            elif '/EN_HU.png' or '/SUB_HU.png' in item: lang = '[COLOR red]FELIRAT[/COLOR]'
            elif '/EN.png' or '/SUB_EN.png' or '/MAS.png' in item: lang = '[COLOR yellow]NINCS FELIRAT[/COLOR]'
            addFile('[COLOR blue]' + utils.py2_encode(client.replaceHTMLCodes(quality.upper())) + '[/COLOR]' + ' | ' + lang + ' | ' + utils.py2_encode(host.upper()), link, 4, meta)
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
    plot = client.replaceHTMLCodes(plot)
    plot = utils.py2_encode(plot)
    
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
    
    links = client.parseDOM(result, 'div', attrs={'class': 'row movie-links-holder'})[0]
    hosts = client.parseDOM(links, 'div', attrs={'class': 'panel'})
    
    meta = {'imdb': imdb_id, 'plot': plot, 'duration': duration, 'title': name, 'label': name, 'poster': poster, 'fanart': poster, 'thumb': poster}
    try:
        meta = metacache.get(get_meta, 720, meta, 'movie')
    except: pass
    return (hosts, youtube_id, meta)

def forrasok_Sorozat():
    metadata = json.loads(meta)

    hosts = client.parseDOM(url, 'div', attrs={'class': 'panel\s*?'})

    for item in hosts:
        link = client.parseDOM(item, 'a', ret='href')[-1]
        host = client.parseDOM(item, 'span')[0]
        quality = host.split()[2]
        host = host.split()[0]
        if '/HU.png' in item: lang = '[COLOR green]SZINKRON[/COLOR]'
        elif '/EN_HU.png' or '/SUB_HU.png' in item: lang = '[COLOR red]FELIRAT[/COLOR]'
        elif '/EN.png' or '/SUB_EN.png' or '/MAS.png' in item: lang = '[COLOR yellow]NINCS FELIRAT[/COLOR]'
        addFile('[COLOR blue]' + utils.py2_encode(quality.upper()) + '[/COLOR]' + ' | ' + lang + ' | ' + utils.py2_encode(host.upper()), link, 4, metadata)
                
    viewmode = setviewmode('movie_folder')
    if viewmode != 0:
        xbmc.executebuiltin('Container.SetViewMode(%s)' %viewmode)
    return

def getSearches():
    searchFile = os.path.join(base_path, "%ssearch.history" % description)
    addDir('[COLOR blue]Új keresés[/COLOR]', '', 15, '', '', description, 1, '', '', '','','')
    try:
        file = open(searchFile, "r")
        olditems = file.read().splitlines()
        file.close()
        items = list(set(olditems))
        items.sort(key=locale.strxfrm)
        if len(items) != len(olditems):
            file = open(searchFile, "w")
            file.write("\n".join(items))
            file.close()
        for item in items:
            addDir(item, '', 16, '', '', description, 1, '', '', '','','')
        if len(items) > 0:
            addDir('[COLOR red]Keresési előzmények törlése[/COLOR]', '', 17, '', '', description, 1, '', '', '','','')
    except:
        pass

def open_search_panel():
    search_text = ''
    keyb = xbmc.Keyboard('' , 'Keresés')
    keyb.doModal()
 
    if (keyb.isConfirmed()):
        search_text = keyb.getText()
        if search_text != '':
            searchFile = os.path.join(base_path, "%ssearch.history" % description)
            if not os.path.exists(base_path):
                os.mkdir(base_path)
            file = open(searchFile, "a")
            file.write("%s\n" % search_text)
            file.close()
            kereses(search_text, 1, description)
        return
    
def deleteSearchHistory():
    searchFile = os.path.join(base_path, "%ssearch.history" % description)
    if os.path.exists(searchFile):
        os.remove(searchFile)
    getSearches()
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
                title = client.replaceHTMLCodes(title)
                title = utils.py2_encode(title)
                addDir(title, link, 3, img, control.addonFanart(), '', 1, '', '', '', '','')
            elif type == 'sorozat':
                title = client.parseDOM(item, 'div', attrs={'class': 'title'})[0]
                title = (client.parseDOM(title, 'h2')[0]).replace('\n','').strip()
                title = client.replaceHTMLCodes(title)
                title = utils.py2_encode(title)
                title = re.compile('(.*)\:\s(.*)').findall(title)[0]
                addDir(title[0]  + ' : ' + '[COLOR yellow]' + title[1] + '[/COLOR]', link, 9, img, control.addonFanart(), '', 1, '', '', '', title[0],'')       
        except:
            pass
    return

def Episodes():
    #try:
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
                addDir2(label, utils.py2_encode(item), 10, meta2)
            except:
                pass
        
        viewmode = setviewmode('movie_folder')
        if viewmode != 0:
            xbmc.executebuiltin('Container.SetViewMode(%s)' %viewmode)
        return
    #except:
    #    return


def getEpisodes(url, season, poster):
    result = client.request(url)
    
    try: plot = (client.parseDOM(result, 'p')[0]).replace('\n','').strip()
    except: plot = '0'
    plot = client.replaceHTMLCodes(plot)
    plot = utils.py2_encode(plot)

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

    episodes = client.parseDOM(result, 'dd', attrs={'class': 'accordion-navigation'})

    meta = {'imdb': imdb_id, 'plot': plot, 'duration': duration, 'title': title, 'label': title, 'poster': poster, 'fanart': poster, 'thumb': poster, 'season': season}
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
    videoitem = xbmcgui.ListItem(label=label)
    videoitem.setArt({'thumb': thumbnailimage})
    videoitem.setInfo(type='Video', infoLabels=metadata)
    try:
        xbmc.Player().play(getMovieUrl(url), videoitem)
    except:
        just_removed()


def getMovieUrl(url):
    try:
        control.busy()
        result = client.request(url, redirect=False, output='headers')
        hmf = resolveurl.HostedMediaFile(result['location'])
        if hmf:
            direct_url = hmf.resolve()
            if isinstance(direct_url, str) or isinstance(direct_url, basestring):
                control.idle()
                return direct_url
            else:
                control.idle()
                just_removed()
        else:
            xbmc.log('Mozicsillag: ResolveURL could not resolve url: %s' % result['location'], xbmc.LOGINFO)
            xbmcgui.Dialog().notification("URL feloldás hiba", "URL feloldása sikertelen a %s host-on" % urlparse.urlparse(result['location']).hostname)
            control.idle()
    except: 
        control.idle()
        just_removed()
##########


def getConstants():
        try:
            try: hosts = resolveurl.relevant_resolvers(order_matters=True)
            except: hosts = resolveurl.plugnplay.man.implementors(resolveurl.UrlResolver)
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
    u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&category="+str(category)+"&page="+str(page)+"&name="+quote_plus(name)+"&iconimage="+quote_plus(iconimage)+"&fanart="+quote_plus(fanart)+"&description="+quote_plus(description)+"&year="+quote_plus(year)+"&genre="+quote_plus(genre)+"&title="+quote_plus(title)+"&orig_title="+quote_plus(orig_title)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage})
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description, "Year": year, "Genre": genre } )
    liz.setProperty( "Fanart_Image", fanart )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmcplugin.setContent(addon_handle, 'movies')
    return ok

def addDir2(name, url, mode, meta):
    try: poster = meta['poster']
    except: poster = ''
    sysmeta = quote_plus(json.dumps(meta))
    u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&name="+quote_plus(name)+"&meta="+sysmeta
    ok=True
    liz=xbmcgui.ListItem(name) #, iconImage=meta['thumb'], thumbnailImage=meta['thumb'])
    liz.setArt({'icon': meta['thumb'], 'thumb': meta['thumb'], 'poster': poster})
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
    sysmeta = quote_plus(json.dumps(meta))
    u=sys.argv[0]+"?url="+quote_plus(url)+"&mode="+str(mode)+"&name="+quote_plus(name)+"&meta="+sysmeta
    ok=True
    liz=xbmcgui.ListItem(name) #, iconImage=meta['thumb'], thumbnailImage=meta['thumb'])
    liz.setArt({'icon': meta['thumb'], 'thumb': meta['thumb'], 'poster': poster})
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
    url = unquote_plus(params["url"])
except:
    pass
try:
    name = unquote_plus(params["name"])
except:
    pass
try:
    title = unquote_plus(params["title"])
except:
    pass
try:
    iconimage = unquote_plus(params["iconimage"])
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
    fanart = unquote_plus(params["fanart"])
except:
    pass
try:        
    description = unquote_plus(params["description"])
except:
    pass
try:        
    category = unquote_plus(params["category"])
except:
    pass
try:        
    search_text = unquote_plus(params["category"])
except:
    pass
try:        
    host = unquote_plus(params["host"])
except:
    pass
try:        
    year = unquote_plus(params["year"])
except:
    pass
try:        
    genre = unquote_plus(params["genre"])
except:
    pass
try:        
    season = unquote_plus(params["season"])
except:
    pass
try:        
    orig_title = unquote_plus(params["orig_title"])
except:
    pass
try:
    meta = unquote_plus(params["meta"])
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
    getSearches()
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
elif mode == 15:
    open_search_panel()
elif mode == 16:
    kereses(name, 1, description)
elif mode == 17:
    deleteSearchHistory()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
