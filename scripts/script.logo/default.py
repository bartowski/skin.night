__script__       = "Logo Downloader"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = ""
__credits__      = "Team XBMC PASSION, http://passion-xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "04-06-2010"
__version__      = "1.2.1"
__svn_revision__  = "$Revision: 697 $"
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__ = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"


import urllib
import os
import re
from traceback import print_exc
import xbmc
import xbmcgui



SOURCEPATH = os.getcwd()
RESOURCES_PATH = os.path.join( SOURCEPATH , "resources" )
db_path = os.path.join(xbmc.translatePath( "special://profile/Database/" ), "MyVideos34.db")
BASE_URL = "http://www.themurrayworld.com/xbmc/logos/"
LOGO_TEST_PATH = os.path.join( RESOURCES_PATH , "test" )
DIALOG_PROGRESS = xbmcgui.DialogProgress()

# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( RESOURCES_PATH, "platform_libraries", env ) )
sys.path.append( os.path.join( RESOURCES_PATH, "lib" ) )

from pysqlite2 import dbapi2 as sqlite3
from convert import translate_string
from convert import set_entity_or_charref

def footprints():
    print "### %s starting ..." % __script__
    print "### author: %s" % __author__
    print "### URL: %s" % __url__
    print "### credits: %s" % __credits__
    print "### date: %s" % __date__
    print "### version: %s" % __version__
    
def get_html_source( url , save=False):
    """ fetch the html source """
    class AppURLopener(urllib.FancyURLopener):
        version = __useragent__
    urllib._urlopener = AppURLopener()

    try:
        if os.path.isfile( url ): sock = open( url, "r" )
        else:
            urllib.urlcleanup()
            sock = urllib.urlopen( url )

        htmlsource = sock.read()
        if save: file( os.path.join( CACHE_PATH , save ) , "w" ).write( htmlsource )
        sock.close()
        return htmlsource
    except:
        print_exc()
        print "### ERROR impossible d'ouvrir la page %s" % url
        xbmcgui.Dialog().ok("ERROR" , "site unreacheable")
        return False

def get_nfo_id( path ):
    nfo= os.path.join(path , "tvshow.nfo")
    print "### nfo file: %s" % nfo
    nfo_read = file(repr(nfo).strip("u'\""), "r" ).read()
    tvdb_id = re.findall( "<tvdbid>(\d{1,10})</tvdbid>", nfo_read )
    print "thetvdb id: %s" % tvdb_id[0]
    return tvdb_id[0]

def listing():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try: c.execute('select c00,c12,strPath from tvshowview')
    except: c.execute('select tvshow.c00 , tvshow.c12 , path.strPath from tvshow , path , tvshowlinkpath where path.idPath = tvshowlinkpath.idPath AND tvshow.idShow = tvshowlinkpath.idShow')
    try:
        TVlist = []
        for import_base in c:
            #print import_base
            TVshow = {}
            TVshow["name"] = repr(import_base[0]).strip("'u")
            TVshow["id"] = repr(import_base[1]).strip("'u")
            TVshow["path"] = import_base[2]
            TVlist.append(TVshow)
        c.close()
        return TVlist
    except:
        print "no tvdbid found in db"
        return False
        print_exc()

def get_tvid_path( tvpath ):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try: 
        for raw in c.execute('select tvshow.c12 , path.strpath from tvshow,tvshowlinkpath,path where tvshow.idShow=tvshowlinkpath.idshow and tvshowlinkpath.idpath=path.idpath and path.strpath=\"%s\"' % (tvpath)):
            c.close()
            return raw[0] , raw[1]
    except: 
        print_exc()
        return ( False , False )
    
    
def get_first_logo( tvid ):
    match = re.search("""<li><a href="(.*%s.*\.png)">.*?</a></li>""" % tvid , base_info)
    if match:
        logo_url = BASE_URL + match.group(1)
        #getting first logo:
        multi_logo = re.search("(-\d)\.png" , logo_url )
        if multi_logo:
            print "### Detect multi logo, getting the first"
            logo_url = logo_url.replace ( multi_logo.group(1) , "")
        print "### logo: %s" % logo_url
        return logo_url
    else: 
        print "### No match"
        return False

def get_logo_list( tvid ):
    match = re.findall("""<li><a href="(.*%s.*\.png)">.*?</a></li>""" % tvid , base_info)
    if match: return match
    else: 
        print "### No logo found !"
        return False
    
def download_logo( url_logo , path , tvcount , name ):
    destination = os.path.join( path , "logo.png").replace("\\\\" , "\\").encode("utf-8")
    print "### download :" + url_logo , "### path: " + repr(destination).strip("'u")
     
    try:
        def _report_hook( count, blocksize, totalsize ):
            percent = int( float( count * blocksize * 100 ) / totalsize )
            strProgressBar = str( percent )
            #print percent  #DEBUG
            DIALOG_PROGRESS.update( tvcount , "Searching: %s " %  translate_string( name ) , "Downloading: %s" % percent )
        if os.path.exists(path):
            fp , h = urllib.urlretrieve( url_logo , destination , _report_hook )
            #print h
            return True
    except :
        print_exc()   
        return False
        
        
if ( __name__ == "__main__" ): 
     
    solo_mode = False
    footprints()
    try: 
        if sys.argv[ 1 ] : 
            DIALOG_PROGRESS.create( "Logo Downloader in action ..." , "Searching Logo ..." )
            solo_mode = True
    except: print "### No Args found"
    
    base_info = get_html_source( BASE_URL )
    
    if solo_mode:        
        print "### Starting solo Mode"
        logo_path = sys.argv[ 1 ]
        print "### path:%s###" % logo_path
        print "### Getting id"
        tvid , logo_path = get_tvid_path( sys.argv[ 1 ] )
        print "### id Found: %s" % tvid
        if tvid[0:2] == "tt" : 
            print "### IMDB id found (%s), checking for nfo" % logo_path
            try: tvid = get_nfo_id( logo_path )
            except:                
                print "### Error checking for nfo: %stvshow.nfo" % logo_path.replace("\\\\" , "\\").encode("utf-8")
                print_exc()
        print "### get logo list for id:%s ###" % tvid
        logo_list = get_logo_list( tvid )
        if logo_list: 
            print "### %s" % logo_list
            DIALOG_PROGRESS.close
            select = xbmcgui.Dialog().select("choose logo to download" , logo_list)
            if select == -1: pass
            else:
                DIALOG_PROGRESS.create( "Logo Downloader in action ..." , "Downloading ..." )
                
                url_logo = BASE_URL + logo_list[select]
                
                if logo_path: 
                    full_logo_path = os.path.join( logo_path , "logo.png").replace("\\\\" , "\\").encode("utf-8")
                    print "### download logo: %s" % url_logo
                    try:
                        def _report_hook( count, blocksize, totalsize ):
                            percent = int( float( count * blocksize * 100 ) / totalsize )
                            strProgressBar = str( percent )
                            #print percent  #DEBUG
                            DIALOG_PROGRESS.update( percent , "downloading: %s " %  logo_list[select] , "path: %s" % full_logo_path )
                        if os.path.exists(logo_path):
                            fp , h = urllib.urlretrieve( url_logo , full_logo_path , _report_hook )
                            #print h
                            DIALOG_PROGRESS.close
                            xbmcgui.Dialog().ok("Success" , "Logo downloaded successfully !" )
                    except :
                        print_exc()
                        DIALOG_PROGRESS.close   
                        xbmcgui.Dialog().ok("Error" , "Error downloading logo !" )
                else: print "### Path not found"
        
    else:
        print "### Starting Bulk Mode"
        DIALOG_PROGRESS.create( "Logo Downloader in action ..." , "Getting info ..." )   
        TVshow_list = listing()
   
        if TVshow_list and base_info:
            total_tvshow = len(TVshow_list)
            tvcount = 0
            total_logo = 0
            downloaded = 0
            for TVshow in TVshow_list:
                tvcount = tvcount + 1
                ratio =  int (float( tvcount  * 100 ) / total_tvshow )
                print "### Checking %s TVshow: %s  id: %s" % ( ratio , translate_string( TVshow["name"] ) , TVshow["id"] )
                if TVshow["id"][0:2] == "tt" : 
                    print "### IMDB id found in database(%s), checking for nfo" % TVshow["id"]
                    try: tvid = get_nfo_id( TVshow["path"] )
                    except:                
                        print "### Error checking for nfo: %stvshow.nfo" % TVshow["path"]
                        tvid = TVshow["id"]
                        print_exc()
                else : tvid = TVshow["id"]        
                DIALOG_PROGRESS.update( ratio , "Searching: %s " %  translate_string( TVshow["name"] ) , tvid )
                if ( DIALOG_PROGRESS.iscanceled() ): break
                if tvid == "" : 
                    print "### no id, skipping ..."
                    logo_url = False
                if os.path.isfile(os.path.join( TVshow["path"] , "logo.png").replace("\\\\" , "\\").encode("utf-8")):
                    print "### Logo.png already exist, skiping ..."
                    total_logo = total_logo + 1
                    logo_url = False
                else: logo_url = get_first_logo( tvid )
                if logo_url: 
                    succes = download_logo( logo_url , TVshow["path"] , ratio , TVshow["name"] )
                    if succes: 
                        downloaded = downloaded + 1
                        total_logo = total_logo + 1
                        print "### Logo downloaded Successfully !!!"
                    else: print "### Logo download Failed !!!"
            DIALOG_PROGRESS.close
            reussite = int( float( total_logo  * 100 ) / total_tvshow ) 
            xbmcgui.Dialog().ok("Logo Downloader Finished ..." , " %s Logo Downloaded ! TVshow: %s" % ( downloaded , total_tvshow ) , "%s percent completed (%s logo found)" %  ( reussite , total_logo ) )
            print "### %s Logo Downloaded ! TVshow: %s" % (downloaded , total_tvshow)
        else: xbmcgui.Dialog().ok("Error" , "No tvshow find or error getting web page" )
    
    