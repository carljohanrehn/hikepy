##!/home/alpha/anaconda/bin/python
## -*- coding: utf-8 -*-

__author__ = 'Carl Johan Rehn'
__maintainer__ = "Carl Johan Rehn"
__email__ = "care02@gmail.com"
__credits__ = ["Sydney, The Red Merle"]
__copyright__ = "Copyright (c) 2015, Carl Johan Rehn"
__license__ = "The MIT License (MIT)"
__version__ = "0.1.0"
__status__ = "Development"

import os
from urlparse import urlparse

from functools32 import lru_cache
from pattern.web import URL, plaintext

import requests
from PIL import Image
from StringIO import StringIO

from simplemediawiki import MediaWiki

# WIKIPEDIA_LANGUGAGE = 'dk'
# WIKIPEDIA_LANGUGAGE = 'en'
WIKIPEDIA_LANGUGAGE = 'sv'

get_wikipedia_url = lambda: 'http://' + WIKIPEDIA_LANGUGAGE + '.wikipedia.org/w/api.php'

# wiki = MediaWiki('http://sv.wikipedia.org/w/api.php')
wiki = MediaWiki(get_wikipedia_url())

# TODO Check limits on requests..
# Volatile! Request MAX_LENGTH pages in each call to wikipedia
WIKIPEDIA_REQUEST_MAX_PAGES = 1  # 5

get_titles = lambda list_of_titles: '|'.join(list_of_titles)

get_page_ids = lambda list_of_page_ids: '|'.join(map(str, list_of_page_ids))


@lru_cache(maxsize=128)
def wikipedia_geosearch(latitude, longitude, radius, limit=100):
    """
    Find Wikipedia articles within a radius of geographic location.

    Reference:  http://www.mediawiki.org/wiki/Extension:GeoData

    @param latitude: Latitude, decimal degrees format (e.g. 59.33)
    @param longitude: Longitude, decimal degrees format (e.g. 17.95).
    @param radius: Radius in meters.
    @param limit: Maximum number of results.
    @return: Query result with list of pages.

    >>> latitude, longitude, radius = 59.33, 17.95, 500
    >>> result = wikipedia_geosearch(latitude, longitude, radius)
    >>> result['query']['geosearch'][0]['title']
    u'Abrahamsberg'
    """

    return wiki.call(
        {'action': 'query',
         'list': 'geosearch',
         'gscoord': str(latitude) + '|' + str(longitude),
         'gsradius': str(radius),
         'gslimit': str(limit),
         'gsprop': 'type'}
    )


@lru_cache(maxsize=128)
def get_wikipedia_page(key, value):
    """
    Get Wikipedia pages using titles or page ids.

    @param key: Key is a string with value 'titles' or 'pageids'.
    @param value: As string with titles or page ids separated by '|'.
    @return: List of pages.

    >>> key = 'titles'
    >>> value = 'Aromatics_byggnad'
    >>> page = get_wikipedia_page(key, value)
    >>> page['query']['pages'].keys()
    [u'4868947']
    """

    d_wiki = {'action': 'query',
              'prop': 'categories|coordinates|extracts|info|images',
              'inprop': 'url',
              'continue': ''}

    d_wiki[key] = value

    return wiki.call(d_wiki)


@lru_cache(maxsize=128)
def wikipedia_image_urls(titles):
    """
    Get the url addresses of images.

    url = u'http://upload.wikimedia.org/wikipedia/commons/9/9b/Aromatic_dec_2013b.jpg'

    Reference: http://www.mediawiki.org/wiki/API:Imageinfo

    @param titles: String with image file names (separated with '|').
    @return: List of urls.

    >>> titles = 'Fil:Aromatic dec 2013b.jpg|Fil:Dragontorpet Abrahamsberg, 2013a.jpg'
    >>> wikipedia_image_urls(titles)[0]
    u'http://upload.wikimedia.org/wikipedia/commons/9/9b/Aromatic_dec_2013b.jpg'
    """

    image_info = wiki.call(
        {'action': 'query',
         'titles': titles,
         'prop': 'imageinfo',
         'iiprop': 'url',
         'continue': ''}
    )

    return [d['imageinfo'][0]['url'] for d in image_info['query']['pages'].values()]


@lru_cache(maxsize=128)
def get_wikipedia_category_members(title, limit=100):
    """
    Get category members (pages) corresponding to title.

    @param title: Title of category.
    @param limit: Maximum number of query results.
    @return: Dictionary with category members (pages).

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> title = 'Kategori:Byggnader_i_Västerort'
    >>> category_members = get_wikipedia_category_members(title)
    >>> category_members['query']['categorymembers'][0]['title']
    u'Anticimex kontorsbyggnad'
    """

    return wiki.call(
        {'action': 'query',
         'list': 'categorymembers',
         'cmtitle': title,
         'cmlimit': limit,
         'continue': ''}
    )


def get_wikipedia_pages_by_list(titles_or_page_ids):
    """
    Get Wikipedia pages using list of titles or page ids.

    @param titles_or_page_ids: List of titles or page ids.
    @return: List of pages.


    >>> titles_or_page_ids = 'Aromatics_byggnad'
    >>> pages = get_wikipedia_pages_by_list(titles_or_page_ids)
    >>> pages[0]['pageid']
    4868947

    >>> titles_or_page_ids = ['Aromatics_byggnad']
    >>> pages = get_wikipedia_pages_by_list(titles_or_page_ids)
    >>> pages[0]['pageid']
    4868947

    >>> titles_or_page_ids = ['Dragontorpet Abrahamsberg', 'Farfadern']
    >>> pages = get_wikipedia_pages_by_list(titles_or_page_ids)
    >>> pages[0]['pageid']
    3879445

    >>> titles_or_page_ids = [1160607, 3879445]
    >>> pages = get_wikipedia_pages_by_list(titles_or_page_ids)
    >>> pages[0]['pageid']
    3879445
    """

    # Function for splitting a list into smaller lists, see
    # http://stackoverflow.com/questions/752308/split-list-into-smaller-lists
    split_list = lambda l, n=WIKIPEDIA_REQUEST_MAX_PAGES: [l[:]] if len(l) <= n else [l[i:i+n] for i in range(0, len(l), n)]

    if isinstance(titles_or_page_ids, str):
        titles_or_page_ids = [titles_or_page_ids]

    titles_or_page_ids = split_list(titles_or_page_ids, WIKIPEDIA_REQUEST_MAX_PAGES)

    pages = []
    for values in titles_or_page_ids:

        if all([isinstance(v, str) for v in values]):
            results = get_wikipedia_page('titles', '|'.join(values))
        else:
            results = get_wikipedia_page('pageids', '|'.join(map(str, values)))

        pages.extend(results['query']['pages'].values())

    return pages

    # TODO: What about 'continue'...


def get_wikipedia_pages_by_category(title, limit=100):
    """
    Get Wikipedia pages using category title.

    @param title: Category title.
    @param limit: Maximum number of pages.
    @return: List of pages.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> pages = get_wikipedia_pages_by_category(title, 10)
    >>> pages[0]['pageid']
    1878869

    >>> title = 'Kategori:Byggnader_i_Västerort'
    >>> pages = get_wikipedia_pages_by_category(title, 10)
    >>> pages[0]['pageid']
    271817
    """

    category_members = get_wikipedia_category_members(title, limit)
    page_ids = [member['pageid'] for member in category_members['query']['categorymembers']]

    return get_wikipedia_pages_by_list(page_ids)


def wikipedia_categories(list_of_pages):
    """
    Find categories of Wikipedia pages.

    @param list_of_pages: List of pages.
    @return: List of categories for each page and the unique list of categories.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> list_of_pages = get_wikipedia_pages_by_category(title, 2)
    >>> wikipedia_categories(list_of_pages)[1][2]
    'Kategori:Ljusskyltar i Stockholm'
    """

    categories = [d['title'] for page in list_of_pages for d in page['categories']]

    return categories, list(set(categories))


def wikipedia_coordinates(list_of_pages):
    """
    Find coordinates of Wikipedia pages

    @param list_of_pages: List of pages.
    @return: List of coordinates.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> list_of_pages = get_wikipedia_pages_by_category(title, 2)
    >>> wikipedia_coordinates(list_of_pages)[0]
    (59.317, 17.9991)
    """

    return [(d['lat'], d['lon']) for page in list_of_pages for d in page['coordinates']]


def wikipedia_extracts(list_of_pages):
    """
    Find extracts of Wikipedia pages.

    @param list_of_pages: List of pages.
    @return: List of extracts.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> list_of_pages = get_wikipedia_pages_by_category(title, 2)
    >>> print wikipedia_extracts(list_of_pages)[1]
    """

    extracts = []
    for page in list_of_pages:
        extracts.append(plaintext(page['extract']) if 'extract' in page else None)

    return extracts


# def wikipedia_info(list_of_pages):
#
#     return [d['title'] for page in list_of_pages for d in page['info']]


def wikipedia_images(list_of_pages):
    """
    Find image titles of Wikipedia pages.

    @param list_of_pages: List of pages.
    @return: List of image titles.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> list_of_pages = get_wikipedia_pages_by_category(title, 2)
    >>> wikipedia_images(list_of_pages)[0][1]
    u'Fil:Aromatic dec 2013b.jpg'
    """

    titles = []
    for page in list_of_pages:
        try:
            titles.append([d['title'] for d in page['images']])
        except:
            titles.append(None)

    return titles
#    return [d['title'] for page in list_of_pages for d in page['images']]  # download


def wikipedia_urls(list_of_pages):
    """
    Find urls of Wikipedia pages.

    @param list_of_pages: List of pages.
    @return: List of urls.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> list_of_pages = get_wikipedia_pages_by_category(title, 2)
    >>> wikipedia_urls(list_of_pages)
    [u'http://sv.wikipedia.org/wiki/Aromatics_byggnad',
    u'http://sv.wikipedia.org/wiki/Anticimex_kontorsbyggnad']
    """

    return [page['fullurl'] for page in list_of_pages]


def wikipedia_titles(list_of_pages):
    """
    Find titles of Wikipedia pages.

    @param list_of_pages: List of pages.
    @return: List of titles.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> list_of_pages = get_wikipedia_pages_by_category(title, 2)
    >>> wikipedia_titles(list_of_pages)
    [u'Aromatics byggnad', u'Anticimex kontorsbyggnad']
    """

    return [page['title'] for page in list_of_pages]


def wikipedia_page_ids(list_of_pages):
    """
    Find ids of Wikipedia pages.

    @param list_of_pages: List of pages.
    @return: List of ids.

    >>> title = 'Kategori:Byggnader_i_Söderort'
    >>> list_of_pages = get_wikipedia_pages_by_category(title, 2)
    >>> wikipedia_page_ids(list_of_pages)
    [4868947, 4527387]
    """

    return [page['pageid'] for page in list_of_pages]


def download_wikipedia_images(urls_or_titles, folder=''):
    """
    Download Wikipedia images.

    Reference: http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests

    @param urls_or_titles: List of urls or titles.
    @param folder: Download folder.

    >>> urls_or_titles = ['Fil:Aromatic dec 2013b.jpg', 'Fil:Dragontorpet Abrahamsberg, 2013a.jpg']
    >>> urls_or_titles = wikipedia_image_urls('|'.join(urls_or_titles))
    >>> download_wikipedia_images(urls_or_titles, 'images')
    """

    is_url = lambda urls_or_titles: all([True if urlparse(s).scheme == 'http' else False for s in urls_or_titles])

    if is_url(urls_or_titles):
        urls = urls_or_titles
        titles = [os.path.split(s)[-1] for s in urls]
    else:
        urls = wikipedia_image_urls('|'.join(urls_or_titles))
        titles = urls_or_titles

    for url, title in zip(urls, titles):
        print url, title
        r = requests.get(url)
        image_io = Image.open(StringIO(r.content))
        image_io.save(os.path.join(folder, title), format='JPEG')


def wikipedia_search(srsearch, srwhat, srlimit=10):
    """
    Search for all page titles (or content).

    Refernce : http://www.mediawiki.org/wiki/API:Search

    @param srsearch: Search value.
    @param srwhat: 'title', 'text', or 'nearmatch'.
    @param srlimit: Number of pages to return.
    @return: List of page titles.

    >>> srsearch, srwhat = 'Skåneleden', 'text'
    >>> list_of_titles = wikipedia_search(srsearch, srwhat)
    >>> print list_of_titles[0]
    Skåneleden
    """

    search_result = wiki.call(
        {'action': 'query',
         'list': 'search',
         'srsearch': srsearch,
         'srwhat': srwhat,
         'srlimit': str(srlimit),
         'continue': ''}
    )

    list_of_titles = [page['title'].encode('utf-8') for page in search_result['query']['search']]

    #list_of_pages = get_wikipedia_pages_by_list(list_of_titles)

    return list_of_titles


def wikipedia_upload_images():
    # https://www.mediawiki.org/wiki/API:Upload
    pass


# TODO: Add fields...
def wikipedia_create_page(title, text, **kwargs):
    """

    # Reference: http://www.mediawiki.org/wiki/API:Edit

    @param title:
    @param text:

    >>> title = 'Gislavedsleden'
    >>> text = 'Gislavedsleden är 10 mil lång. Den har sin början i Kinnared och går norrut mot Isaberg.'
    >>> wikipedia_create_page(title, text)

    >>> get_wikipedia_pages_by_list(['Gislavedsleden'])

    >>> get_wikipedia_pages_by_list([4964044])

    """

    result = wiki.call(
        {'action': 'query',
         'meta': 'tokens'}
    )

    token = result['query']['tokens']['csrftoken']

    wiki.call(
        {'action': 'edit',
         'title': title,
         'text': text,
         'token': token}
    )

    # {u'edit': {u'contentmodel': u'wikitext',
    #   u'new': u'',
    #   u'newrevid': 29942311,
    #   u'newtimestamp': u'2015-05-04T19:45:28Z',
    #   u'oldrevid': 0,
    #   u'pageid': 4964044,
    #   u'result': u'Success',
    #   u'title': u'Gislavedsleden'}}


# TODO: Add fields...
def wikipedia_edit_page(title_or_page_id, **kwargs):

    result = wiki.call(
        {'action': 'query',
         'meta': 'tokens'}
    )

    token = result['query']['tokens']['csrftoken']

    title = 'Sörmlandsleden'
    section = 'new'
    sectiontitle = 'Ledens etapper'
    text = 'Sörmländskt kulturlandskap, historiska minnesmärken, odlingsmark och skogar, \
            berg och sjöar; runt 100 etapper av varierande längd erbjuder allt från \
            strapatsrik vandring till enkla och behagliga promenader.'

    wiki.call(
        {'action': 'edit',
         'title': title,
         'section': section,
         'sectiontitle': sectiontitle,
         'text': text,
         'token': token}
    )







########




#--- Use pattern to extract texts etc (see dir(article) for methods).
#
# from pattern.web import Wikipedia
#
# search_string = 'Skåne'
# article = Wikipedia(language="sv").search(search_string, throttle=10)
# article.title
# article.sections
# dir(article)
# get_wikipedia_pages_by_list([article.title.encode('utf-8')])
#
#---


# API Sandbox
#http://en.wikipedia.org/wiki/Special:ApiSandbox#action=edit&title=Talk:Main_Page&section=new&summary=Hello%20World&text=Hello%20everyone!&watch&basetimestamp=2008-03-20T17:26:39Z&token=cecded1f35005d22904a35cc7b736e18%2B%5C

#--- Using pattern.web for scraping Wikipedia
#--- http://www.clips.ua.ac.be/pages/pattern-web#plaintext

# from pattern.web import Wikipedia
#
# article = Wikipedia(language="sv").search(get_wikipedia_titles(list_of_pages)[0], throttle=10)
#
# article.categories
# article.sections
# article.media
#
# article.plaintext()
# article.html()
# #article.download()
#
# print article.sections[0].content
#
# for section in article.sections:
#     print repr(' ' * section.level + section.title)
#
#
# article.download(media, **kwargs)
# image = article.download(u'Dragontorpet_Abrahamsberg,_2013a1.jpg')


# from pattern.web import Wikipedia
#
# article = Wikipedia(language="sv").search(title, throttle=10)
#
# article.categories
# article.sections
# article.media
#
# article.plaintext()
# article.html()
# #article.download()
#
# print article.sections[0].content


# TODO Upload Wikipedia waypoints as OSM nodes

# TODO Scrape Web + pfd for information using "pattern"



