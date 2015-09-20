#!/home/alpha/anaconda/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Carl Johan Rehn'
__maintainer__ = "Carl Johan Rehn"
__email__ = "care02@gmail.com"
__credits__ = ["Sydney, The Red Merle"]
__copyright__ = "Copyright (c) 2015, Carl Johan Rehn"
__license__ = "The MIT License (MIT)"
__version__ = "0.1.0"
__status__ = "Development"

import numpy as np
import pandas as pd
import sqlite3

from functools32 import lru_cache

import LatLon

# TODO Swedish map projections
import sgcpy

# TODO Circular reference
from gpx_trail import create_gpx_file_name

import osmapi
import overpass

osm_api = osmapi.OsmApi()
overpass_api = overpass.API()


@lru_cache(maxsize=128)
def bbox_min_max_to_south_north_west_east(min_longitude, min_latitude, max_longitude, max_latitude):
    """
    Coordinate conversion: min/max to south/north/west/east.

    Convert from
        min_longitude, min_latitude, max_longitude, max_latitude
    to
        south_latitude, north_latitude, west_longitude, east_longitude.

    References:
    http://wiki.openstreetmap.org/wiki/Bounding_Box
    http://wiki.openstreetmap.org/wiki/Overpass_API
    http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
    https://en.wikipedia.org/wiki/Geographic_coordinate_system
    https://en.wikipedia.org/wiki/Latitude
    https://en.wikipedia.org/wiki/Longitude

    @param min_longitude: Min longitude is a decimal number between -180.0 and 180.0.
    @param min_latitude: Min latitude is a decimal number between -90.0 and 90.0.
    @param max_longitude: Max longitude is a decimal number between -180.0 and 180.0.
    @param max_latitude: Max latitude is a decimal number between -90.0 and 90.0.
    @return: Tuple (south_latitude, north_latitude, west_longitude, east_longitude).

    >>> min_longitude, min_latitude, max_longitude, max_latitude = 12.4985, 56.0189, 12.6314, 56.0763
    >>> bbox_min_max_to_south_north_west_east(min_longitude, min_latitude, max_longitude, max_latitude)
    (56.0189, 56.0763, 12.4985, 12.6314)
    """

    return min_latitude, max_latitude, min_longitude, max_longitude


@lru_cache(maxsize=128)
def bbox_south_north_west_east_to_min_max(south_latitude, north_latitude, west_longitude, east_longitude):
    """
    Coordinate conversion: south/north/west/east to min/max.

    Convert from
        south_latitude, north_latitude, west_longitude, east_longitude
    to
        min_longitude, min_latitude, max_longitude, max_latitude.

    References:
    http://wiki.openstreetmap.org/wiki/Bounding_Box
    http://wiki.openstreetmap.org/wiki/Overpass_API
    http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
    https://en.wikipedia.org/wiki/Geographic_coordinate_system
    https://en.wikipedia.org/wiki/Latitude
    https://en.wikipedia.org/wiki/Longitude

    @param min_longitude: Min longitude is a decimal number between -180.0 and 180.0.
    @param min_latitude: Min latitude is a decimal number between -90.0 and 90.0.
    @param max_longitude: Max longitude is a decimal number between -180.0 and 180.0.
    @param max_latitude: Max latitude is a decimal number between -90.0 and 90.0.
    @return: Tuple (min_longitude, min_latitude, max_longitude, max_latitude).

    >>> south_latitude, north_latitude, west_longitude, east_longitude = 56.0189, 56.0763, 12.4985, 12.6314
    >>> bbox_south_north_west_east_to_min_max(south_latitude, north_latitude, west_longitude, east_longitude)
    (12.4985, 56.0189, 12.6314, 56.0763)
    """

    return west_longitude, south_latitude, east_longitude, north_latitude


@lru_cache(maxsize=128)
def bbox_min_max_to_bbox_south_south_north_north(min_longitude, min_latitude, max_longitude, max_latitude):
    """
    Coordinate conversion: min/max to south/south/north/north.

    Convert from
        min_longitude, min_latitude, max_longitude, max_latitude
    to
        south_latitude, south_longitude, north_latitude, north_longitude.

    Format south/south/north/north is used by the Overpass API.

    References:
    http://wiki.openstreetmap.org/wiki/Bounding_Box
    http://wiki.openstreetmap.org/wiki/Overpass_API
    http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
    https://en.wikipedia.org/wiki/Geographic_coordinate_system
    https://en.wikipedia.org/wiki/Latitude
    https://en.wikipedia.org/wiki/Longitude

    @param min_longitude: Min longitude is a decimal number between -180.0 and 180.0.
    @param min_latitude: Min latitude is a decimal number between -90.0 and 90.0.
    @param max_longitude: Max longitude is a decimal number between -180.0 and 180.0.
    @param max_latitude: Max latitude is a decimal number between -90.0 and 90.0.
    @return: Tuple (south_latitude, south_longitude, north_latitude, north_longitude).

    >>> min_longitude, min_latitude, max_longitude, max_latitude = 12.4985, 56.0189, 12.6314, 56.0763
    >>> bbox_min_max_to_bbox_south_south_north_north(min_longitude, min_latitude, max_longitude, max_latitude)
    (56.0189, 12.4985, 56.0763, 12.6314)
    """

    return min_latitude, min_longitude, max_latitude, max_longitude


@lru_cache(maxsize=128)
def bbox_south_south_north_north_to_min_max(south_latitude, south_longitude, north_latitude, north_longitude):
    """
    Coordinate conversion: south/south/north/north to min/max.

    Convert from
        south_latitude, south_longitude, north_latitude, north_longitude
    to
        min_longitude, min_latitude, max_longitude, max_latitude.

    Format south/south/north/north is used by the Overpass API.

    References:
    http://wiki.openstreetmap.org/wiki/Bounding_Box
    http://wiki.openstreetmap.org/wiki/Overpass_API
    http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
    https://en.wikipedia.org/wiki/Geographic_coordinate_system
    https://en.wikipedia.org/wiki/Latitude
    https://en.wikipedia.org/wiki/Longitude

    @param min_longitude: Min longitude is a decimal number between -180.0 and 180.0.
    @param min_latitude: Min latitude is a decimal number between -90.0 and 90.0.
    @param max_longitude: Max longitude is a decimal number between -180.0 and 180.0.
    @param max_latitude: Max latitude is a decimal number between -90.0 and 90.0.
    @return: Tuple (min_longitude, min_latitude, max_longitude, max_latitude).

    >>> south_latitude, south_longitude, north_latitude, north_longitude = 56.0189, 12.4985, 56.0763, 12.6314
    >>> bbox_south_south_north_north_to_min_max(south_latitude, south_longitude, north_latitude, north_longitude)
    (12.4985, 56.0189, 12.6314, 56.0763)
    """

    return south_longitude, south_latitude, north_longitude, north_latitude


@lru_cache(maxsize=128)
def convert_lat_lon(lat, lon):
    """
    Convert from degrees decimal minutes format to decimal degrees format.

    References:
    https://pypi.python.org/pypi/LatLon/1.0.2
    http://en.wikipedia.org/wiki/Geographic_coordinate_conversion

    @param lat: Latitude (e.g. 'N 59 16.58').
    @param lon: Longitude (e.g. 'E 18 11.22').
    @return: Latitude and longitude on decimal format (e.g. 59.202 and 18.26825).

    >>> convert_lat_lon('N 59 12.120', 'E 18 16.095')
    (59.202, 18.26825)
    >>> convert_lat_lon('N 59 11.772', 'E 17 4.744')
    (59.1962, 17.079066666666666)
    """

    obj = LatLon.string2latlon(lat, lon, 'H% d% %M')
    return obj.lat.decimal_degree, obj.lon.decimal_degree


@lru_cache(maxsize=128)
def lat_lon_to_osm(lat, lon, geo_format='degrees decimal minutes',
                   layer_code='M', zoom_level=14):
    """
    Get a map centered on (lat, lon) with a given zoom level.

    References:
    http://en.wikipedia.org/wiki/Geographic_coordinate_conversion
    http://wiki.openstreetmap.org/wiki/Browsing

    @param lat: Latitude (e.g. 'N 59 16.58' or 59.2763333333).
    @param lon: Longitude (e.g. 'E 18 11.22' or 18.187).
    @param geo_format: 'degrees decimal minutes' or 'decimal degrees'.
    @param layer_code: Mapnik ('M'), Cyclemap ('C'), MapQuest ('Q'), Humanitarian ('H').
    @param zoom_level: Set zoom level (default is 14).
    @return: OSM map query (string).

    >>> lat_lon_to_osm('N 59 16.58', 'E 18 11.22')
    http://www.openstreetmap.org/?mlat=59.2763333333&mlon=18.187#map=14/59.2763333333/18.187&layers=M

    >>> lat_lon_to_osm(59.2763333333, 18.187, 'decimal degrees')
    http://www.openstreetmap.org/?mlat=59.2763333333&mlon=18.187#map=14/59.2763333333/18.187&layers=M
    """

    decimal_degrees = None

    if geo_format in 'degrees decimal minutes':
        decimal_degrees = dict(zip(('lat', 'lon'), map(str, convert_lat_lon(lat, lon))))
    elif geo_format in 'decimal degrees':
        decimal_degrees = dict(zip(('lat', 'lon'), (str(lat), str(lon))))

    if decimal_degrees is None:
        return None

    return 'http://www.openstreetmap.org/?mlat=' + decimal_degrees['lat'] + '&mlon=' + decimal_degrees['lon'] + \
           '#map=' + str(zoom_level) + '/' + decimal_degrees['lat'] + '/' + decimal_degrees['lon'] + \
           '&layers=' + layer_code


@lru_cache(maxsize=128)
def bbox_to_osm(minlon, minlat, maxlon, maxlat, mlat=None, mlon=None, layer_code='M'):
    """
    Get a map that displays everything within a given bounding box (decimal degrees format).

    You can also combine a bounding box with a marker by setting the coordinates of the marker.

    References:
    http://wiki.openstreetmap.org/wiki/Browsing

    @param minlon: Min longitude of bounding box.
    @param minlat: Min latitude of bounding box.
    @param maxlon: Max longitude of bounding box.
    @param maxlat: Max latitude of bounding box.
    @param mlat: Latitude of marker.
    @param mlon: Longitude of marker.
    @param layer_code: Mapnik ('M'), Cyclemap ('C'), MapQuest ('Q'), Humanitarian ('H').
    @return: OSM map query (string).

    >>> minlon, minlat, maxlon, maxlat = 22.3418234, 57.5129102, 22.5739625, 57.6287332
    >>> minlon, minlat, maxlon, maxlat = 12.4985, 56.0189, 12.6314, 56.0763
    >>> bbox_to_osm(minlon, minlat, maxlon, maxlat)
    http://www.openstreetmap.org/?minlon=12.4985&minlat=56.0189&maxlon=12.6314&maxlat=56.0763&layers=M

    >>> mlat, mlon = 57.5529102, 22.5148625
    >>> mlat, mlon = 56.037, 12.61303
    >>> bbox_to_osm(minlon, minlat, maxlon, maxlat, mlat, mlon)
    http://www.openstreetmap.org/?minlon=12.4985&minlat=56.0189&maxlon=12.6314&maxlat=56.0763&mlat=56.037&mlon=12.61303&layers=M
    """

    # TODO Check OSM definition of bounding box, ie order of minlon, minlat, etc - see overpass api and route_query.py

    query = 'http://www.openstreetmap.org/?minlon=' + str(minlon) + '&minlat=' + str(minlat) + \
            '&maxlon=' + str(maxlon) + '&maxlat=' + str(maxlat)

    # TODO What if either mlat or mlon is not None?
    if mlat is not None and mlon is not None:
        query += '&mlat=' + str(mlat) + '&mlon=' + str(mlon)

    query += '&layers=' + layer_code

    return query


@lru_cache(maxsize=128)
def query_id_to_osm(query_id, what='node', layer_code='M'):
    """
    Ask openstreetmap.org to show a particular node, way, or relation.

    References:
    http://wiki.openstreetmap.org/wiki/Browsing
    http://wiki.openstreetmap.org/wiki/Layer_URL_parameter

    @param query_id: Id of node, way, or relation.
    @param what: 'node', 'way', or 'relation'.
    @param layer_code: Mapnik ('M'), Cyclemap ('C'), MapQuest ('Q'), Humanitarian ('H').
    @return: Query string.
    """

    return 'http://www.openstreetmap.org/?' + what + '=' + str(query_id) + \
           '&layers=' + layer_code


def node_to_osm(node_id, layer_code='M', marker=False, zoom_level=14):
    """
    Ask openstreetmap.org to show a particular node.

    @param node_id: Id of node.
    @param layer_code: Mapnik ('M'), Cyclemap ('C'), MapQuest ('Q'), Humanitarian ('H').
    @return: Query string.

    >>> node_to_osm(652065750)
    http://www.openstreetmap.org/?node=652065750

    >>> node_to_osm(652065750, layer_code='H', marker=True)
    http://www.openstreetmap.org/?mlat=59.2766213&mlon=18.1870509#map=14/59.2766213/18.1870509&layers=H
    """

    if marker:
        node = get_node_by_id(node_id)
        return lat_lon_to_osm(
            node['lat'], node['lon'], 'decimal degrees', layer_code, zoom_level
        )
    else:
        return query_id_to_osm(node_id, 'node', layer_code)


def way_to_osm(way_id, layer_code='M'):
    """
    Ask openstreetmap.org to show a particular way.

    @param way_id: Id of way.
    @param layer_code: Mapnik ('M'), Cyclemap ('C'), MapQuest ('Q'), Humanitarian ('H').
    @return: Query string.

    >>> way_to_osm(305561115)
    http://www.openstreetmap.org/?way=305561115
    """

    return query_id_to_osm(way_id, 'way', layer_code)


def relation_to_osm(relation_id, layer_code='M'):
    """
    Ask openstreetmap.org to show a particular node, way or relation.

    @param relation_id: Id of relation.
    @param layer_code: Mapnik ('M'), Cyclemap ('C'), MapQuest ('Q'), Humanitarian ('H').
    @return: Query string.

    >>> relation_to_osm(660162)
    http://www.openstreetmap.org/?relation=660162
    """

    return query_id_to_osm(relation_id, 'relation', layer_code)


@lru_cache(maxsize=128)
def get_relation_by_id(relation_id):
    """
    Read relation from OSM API using relation id.

    @param relation_id: Id of relation.
    @return: Relation dictionary.
    """

    return osm_api.RelationGet(relation_id)


@lru_cache(maxsize=128)
def get_relation_by_name(relation_name):
    """
    Read relation from Overpass API using relation name.

    @param relation_name: Name of relation.
    @return: Relation dictionary.
    """

    return overpass_api.Get('relation["name"~"' + relation_name + '"]')


@lru_cache(maxsize=2048)
def get_way_by_id(way_id):
    """
    Read way from OSM API using way id.

    @param way_id: Id of way.
    @return: Way dictionary.
    """

    return osm_api.WayGet(way_id)


@lru_cache(maxsize=4096)
def get_node_by_id(node_id):
    """
    Read node from OSM API using node id.

    @param node_id: Id of node.
    @return: Node dictionary.
    """

    return osm_api.NodeGet(node_id)


@lru_cache(maxsize=4096)
def get_node_by_name(node_name):
    """
    Read node from Overpass API using node name.

    @param node_name: Name of node.
    @return: Node dictionary.
    """

    return overpass_api.Get('node["name"="' + node_name + '"]')


def get_relation(ways):
    """
    Get all begin and end nodes of relation members (ways) and all nodes belonging to the relation.

    @param ways: List of ways (relation members).
    @return: Data frame with way ids, and the way's begin and end ids.
             List with all nodes belonging to the relation.

    >>> relation_id = 660162
    >>> ways = get_relation_by_id(relation_id)['member']
    >>> df, l_nodes = get_relation(ways[:2])
    >>> df['way']
             way       begin         end
    0  234171837   360693242  1692053035
    1  156967440  1692053035   360693367
    """

    def get_way_nodes(way):
        try:
            nd = get_way_by_id(way['ref'])['nd']
            return nd
        except:
            return None

    def get_relation_nodes(ways):
        l_nodes, l_way, l_begin, l_end = [], [], [], []
        for way in ways:
            nd = get_way_nodes(way)
            if nd:
                l_way.append(way['ref'])
                l_begin.append(nd[0])
                l_end.append(nd[-1])
                l_nodes.append(nd)
        return l_way, l_begin, l_end, l_nodes

    l_way, l_begin, l_end, l_nodes = get_relation_nodes(ways)

    df = pd.DataFrame(
        np.array([l_way, l_begin, l_end]).transpose(), columns=['way', 'begin', 'end']
    )

    return df, l_nodes


def get_relation_members(relation, skip=True, role='alternative'):
    """
    Get all begin and end nodes of relation members (ways), and all nodes belonging to the relation.

    @param relation: Relation dictionary (as obtained from OSM API).
    @param skip: Skip relation members (ways) according to 'role'.
    @param role: Tag for relation members (ways).
    @return: Data frame with way ids, and the way's begin and end ids.
             List with all nodes belonging to the relation.

    >>> d_relations = {'Spångastråket':(4570739, 1458482713, '...', '...')}
    >>> relation_id, start_node, _, _ = d_relations['Spångastråket']
    >>> relation = get_relation_by_id(relation_id)
    >>> df, l_nodes = get_relation_members(relation)
    >>> df.way[0], df.begin[0], df.end[0]
    (243491145, 1458482713, 1458482757)
    """

    def skip_ways(ways, **kwargs):

        for (key, value) in kwargs.items():
            ways = [way for way in ways if not way[key] == value]

        return ways

    #df, l_nodes = get_relation(
    #    skip_ways(relation['member'], **{'role': 'alternative'})
    #)

    if skip:
        members = skip_ways(relation['member'], **{'role': role})
    else:
        members = relation['member']

    df, l_nodes = get_relation(members)

    return df, l_nodes


def create_track_points(relation, start_node):
    """
    Create track points (OSM node ids) of OSM relation starting from start node.

    @param relation: OSM relation as dictionary.
    @param start_node: Start node of track.
    @return: List of track points.

    >>> relation_id, start_node = 660162, 360693242
    >>> relation = get_relation_by_id(relation_id)
    >>> track_points = create_track_points(relation, start_node)
    """

    def check_node(df, current_way, current_node, node='begin'):
        if current_node not in df.begin:
            if current_way is None:
                way = df[df[node] == current_node].way
            else:
                way = df[~(df.way == int(current_way)) & (df[node] == current_node)].way
            if way.empty:
                raise
            return way
        else:
            raise

    def get_segment(df, current_way):
        return int(df[df.way == int(current_way)].index[0])

    def get_nodes(nodes, current_segment, reverse=False):
        list_of_nodes = nodes[current_segment][:]
        if reverse:
            list_of_nodes.reverse()
        return list_of_nodes

    def extend_track_points(track_points, list_of_nodes, reverse=False):
        if reverse:
            track_points.extend(list_of_nodes[:-1])
        else:
            track_points.extend(list_of_nodes[1:])
        return track_points

    def get_node_list(list_of_nodes):
        return list_of_nodes[-1]

    df, l_nodes = get_relation_members(relation)

    nodes = l_nodes[:]

    current_way = None
    current_node = start_node
    track_points = [start_node]
    while True:
        try:
            try:
                reverse = False
                current_way = check_node(df, current_way, current_node, node='begin')
            except:
                reverse = True
                current_way = check_node(df, current_way, current_node, node='end')
        except:
            break

        list_of_nodes = get_nodes(nodes, get_segment(df, current_way), reverse)
        current_node = get_node_list(list_of_nodes)
        #print current_node
        track_points = extend_track_points(track_points, list_of_nodes, reverse)

    return track_points


def get_way_points(relation):
    """
    Get way points of OSM relation.

    @param relation: OSM relation as dictionary.
    @return: List of way points (OSM node ids).

    >>> relation_id = 660162
    >>> relation = get_relation_by_id(relation_id)
    >>> way_points = get_way_points(relation)
    """

    return [r['ref'] for r in relation['member'] if r['type'] == 'node']


def relation_to_dataframes(relation, skip=True, role='alternative'):
    """
    Create data frames with relation, ways, and nodes.

    @param relation: Id of relation.
    @param skip: Skip ways with role.
    @param role: Role value of ways to skip.
    @return: Data frames with relation, ways, and nodes.

    >>> relation_id = 660162
    >>> relation = get_relation_by_id(relation_id)
    >>> df_relation, df_ways, df_nodes = relation_to_dataframes(relation)
    >>> df_relation
    """

    def drop_columns(data_frame, names):
        return data_frame.drop(names, inplace=True, axis=1)

    #drop_columns(df_nodes, 'relation')
    #drop_columns(df_nodes, 'relation')

    def add_columns(data_frame, names):
        for name, value in names.items():
            data_frame[name] = value
        return data_frame

    def change_column_order(data_frame):
        columns = data_frame.columns.tolist()
        return data_frame[columns[-1:] + columns[:-1]]

    df_ways, l_nodes = get_relation_members(relation, skip=skip, role=role)

    df_ways = change_column_order(
        add_columns(df_ways, {'relation': relation['id']})
    )

    df_nodes = pd.DataFrame(
        {'relation': relation['id'],
         'way': map(str, df_ways.way),
         'nodes': map(str, l_nodes)}, columns=['relation', 'way', 'nodes']
    )

    d_relation = {'relation': relation['id'],
                  'name': relation['tag']['name'],
                  'source': relation['tag']['source'] if 'source' in relation['tag'] else None}

    df_relation = pd.DataFrame.from_dict({0: d_relation}, orient='index')
    df_relation = df_relation[['relation', 'name', 'source']]

    return df_relation, df_ways, df_nodes


def save_relation_to_db(engine, relation):
    """
    Save relation, ways, and nodes to database.

    @param engine: Database engine.
    @param relation: Id of relation.

    >>> engine = sqlite3.connect("relations.sqlite")
    >>> relation_id = 660162
    >>> relation = get_relation_by_id(relation_id)
    >>> save_relation_to_db(engine, relation)
    """

    df_relation, df_ways, df_nodes = relation_to_dataframes(relation)

    df_relation.to_sql('relations', engine, if_exists='append', index=False)
    df_ways.to_sql('ways', engine, if_exists='append', index=False)
    df_nodes.to_sql('nodes', engine, if_exists='append', index=False)

    # TODO: Figure out how to add records to existing tables... if_exists='append'
    #l_nd = pd.read_sql_query('select * from nodes', engine, index_col='relation')


def load_relation_from_db(engine, relation_id=None):
    """
    Load relation, ways, and nodes from database.

    @param engine: Database engine.
    @param relation_id: Id of relation.
    @return: Relation, ways, and nodes data frames.

    >>> engine = sqlite3.connect("/media/alpha/ransta/alpha/my/stockholm/py/relations.sqlite")
    >>> relation_id = 660162
    >>> df_ways, l_nodes = load_relation_from_db(engine, relation_id)
    """

    where_relation_id = '' if relation_id is None else ' where relation="' + str(relation_id) + '"'

    # Not needed
    #df_relation = pd.read_sql_query(
    #    'select * from relations' + where_relation_id, engine, index_col='relation'
    #)

    df_ways = pd.read_sql_query(
        'select * from ways' + where_relation_id, engine, index_col='relation'
    )

    df_ways = pd.DataFrame(df_ways.as_matrix(), columns=df_ways.columns)

    df_nodes = pd.read_sql_query(
        'select * from nodes' + where_relation_id, engine, index_col='relation'
    )

    df_nodes = pd.DataFrame(df_nodes.as_matrix(), columns=df_nodes.columns)
    df_nodes = df_nodes[df_ways.way == map(int, df_nodes.way)]

    l_nodes = [eval(nodes) for nodes in map(str, df_nodes.nodes)]

    return df_ways, l_nodes


def write_relation_to_excel(dir_name, relation):
    """
    Create Excel workbook with relations, ways, and nodes tables.

    @param dir_name: Name of directory.
    @param relation: Id of relation.
    """

    file_name = create_gpx_file_name(dir_name, relation['id'], relation['tag']['name'], ext='xlsx')
    writer = pd.ExcelWriter(file_name)

    df_relation, df_ways, df_nodes = relation_to_dataframes(relation)

    df_relation.to_excel(writer, 'Relation')
    df_ways.to_excel(writer, 'Ways')
    df_nodes.to_excel(writer, 'Nodes')

    writer.save()


def read_relation_from_excel():
    pass


def save_track_points_to_db(engine, relation_id, track_points):
    """
    Save track points to database.

    @param engine: Database engine.
    @param relation_id: Id of relation.
    @param track_points: List of track points (OSM node ids).

    >>> engine = sqlite3.connect("/media/alpha/ransta/alpha/my/stockholm/py/relations.sqlite")
    >>> relation_id = 660162
    >>> track_points = [360693242, 360693253, 360693255, 360693257, 550026012]
    >>> save_track_points_to_db(engine, relation_id, track_points)
    """

    df_track_points = {'relation': relation_id, 'nodes': str(track_points)}

    df_track_points = pd.DataFrame.from_dict({0: df_track_points}, orient='index')
    df_track_points = df_track_points[['relation', 'nodes']]
    df_track_points.to_sql('track_points', engine, if_exists='append', index=False)


def load_track_points_from_db(engine, relation_id=None):
    """
    Load track points from database.

    @param engine: Database engine.
    @param relation_id: Id of relation.
    @return: List of track points (OSM node ids).

    >>> engine = sqlite3.connect("/media/alpha/ransta/alpha/my/stockholm/py/relations.sqlite")
    >>> relation_id = 660162
    >>> track_points = load_track_points_from_db(engine, relation_id)
    """

    where_relation_id = '' if relation_id is None else ' where relation="' + str(relation_id) + '"'

    df_nodes = pd.read_sql_query(
        'select * from track_points' + where_relation_id, engine, index_col='relation'
    )

    df_nodes = pd.DataFrame(df_nodes.as_matrix(), columns=df_nodes.columns)

    if df_nodes.empty:
        track_points = []
    else:
        track_points = [eval(nodes) for nodes in map(str, df_nodes.nodes)][0]

    return track_points


# http://osmapi.divshot.io/
# TODO: http://wiki.openstreetmap.org/wiki/API_v0.6
# TODO: Upload nodes, ways, relations, and GPS traces
# http://wiki.openstreetmap.org/wiki/API_v0.6#GPS_traces
#