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

import sqlite3
import pandas as pd
import srtm

from osm_query import get_node_by_id


def get_elevation(track_points):
    """
    Get elevation of track points.

    Typically, requesting elevation of track points can take time.

    @param track_points: List of OSM node ids.
    @return: Dictionary of elevations for node ids.

    >>> elevation_nodes = [360693242, 360693253, 360693255, 360693257, 550026012]
    >>> elevation = get_elevation(elevation_nodes)
    """

    elevation = {}
    for nd in track_points:
        node = get_node_by_id(nd)
        elevation_data = srtm.get_data()
        elevation[nd] = elevation_data.get_elevation(node['lat'], node['lon'], approximate=True)
        print 'Elevation (meters):', elevation[nd]

    return elevation


def save_elevation_to_db(engine, relation_id, elevation):
    """
    Save elevations to database.

    @param engine: Database engine.
    @param relation_id: Id of relation.
    @param elevations: Dictionary of elevations for OSM node ids.

    >>> engine = sqlite3.connect("relations.sqlite")
    >>> relation_id = 660162
    >>> elevation_nodes = [360693242, 360693253, 360693255, 360693257, 550026012]
    >>> elevation = get_elevation(elevation_nodes)
    >>> save_elevation_to_db(engine, relation_id, elevation)
    """

    df_elevation = pd.DataFrame(
        {'relation': relation_id,
         'node': elevation.keys(),
         'elevation': elevation.values()}, columns=['relation', 'node', 'elevation']
    )

    df_elevation.to_sql('elevations', engine, if_exists='append', index=False)


def load_elevation_from_db(engine, relation_id=None):
    """
    Load elevations from database.

    @param engine: Database engine.
    @param relation_id: Id of relation
    @return: Dictionary of elevations for OSM node ids.

    >>> engine = sqlite3.connect("relations.sqlite")
    >>> relation_id = 660162
    >>> elevation = load_elevation_from_db(engine, relation_id)
    """

    where_relation_id = '' if relation_id is None else ' where relation="' + str(relation_id) + '"'

    df_elevation = pd.read_sql_query(
        'select * from elevations' + where_relation_id, engine, index_col='relation'
    )

    d_elevation = pd.DataFrame(df_elevation.as_matrix(), columns=df_elevation.columns).to_dict()

    elevation = {int(key): value for key, value in zip(d_elevation['node'].values(), d_elevation['elevation'].values())}

    return elevation


