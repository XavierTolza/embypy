#!/usr/bin/env python3

from embypy.objects.object import *

# Generic class
class Video(EmbyObject):
  '''Class representing generic emby video objects

  Parameters
  ----------
    object_dict : dict
      same as for `EmbyObject`
    connector : embypy.utils.connector.Connector
      same as for `EmbyObject`
  '''
  def __init__(self, object_dict, connector):
    super().__init__(object_dict, connector)

  @property
  def aspect_ratio(self):
    '''aspect ratio of the video'''
    return self.object_dict.get('AspectRatio', 0.0)

  @property
  def chapters(self):
    '''chapters included in the video file'''
    return self.object_dict.get('Chapters')

  @property
  def stream_url(self):
    '''stream url (as an mp4)'''
    path = '/Videos/{}/stream.mp4'.format(self.id)
    return self.connector.get_url(path, attach_api_key=False)

# Videos
class Movie(Video):
  '''Class representing movie objects

  Parameters
  ----------
    object_dict : dict
      same as for `EmbyObject`
    connector : embypy.utils.connector.Connector
      same as for `EmbyObject`
  '''
  def __init__(self, object_dict, connector):
    super().__init__(object_dict, connector)

  @property
  def premiere_date(self):
    '''date that the movie permiered'''
    return self.object_dict.get('PremiereDate')


class Episode(Video):
  '''Class representing episode objects

  Parameters
  ----------
    object_dict : dict
      same as for `EmbyObject`
    connector : embypy.utils.connector.Connector
      same as for `EmbyObject`
  '''
  def __init__(self, object_dict, connector):
    super().__init__(object_dict, connector)

  @property
  def premiere_date(self):
    '''date that the episode permiered'''
    return self.object_dict.get('PremiereDate')

  @property
  def index_number(self):
    '''the episode number (in the season)'''
    return self.object_dict.get('IndexNumber', 1)

  @index_number.setter
  def index_number(self, value):
    self.object_dict['IndexNumber'] = value

  @property
  def episode_number(self):
    return self.index_number

  @episode_number.setter
  def episode_number(self, value):
    self.index_number = value

  @property
  def season_id(self):
    '''season number'''
    return self.object_dict.get('SeasonId', 1)

  @season_id.setter
  def season_id(self, value):
    self.object_dict['SeasonId'] = value

  @property
  def season(self):
    '''season object'''
    return self.process(self.season_id)

  @property
  def series_id(self):
    '''The emby id of the series this episode belongs to'''
    return self.object_dict.get('SeriesId')

  @property
  def series(self):
    '''Series object for this episode'''
    return self.process(self.series_id)

  @property
  def show(self):
    return self.series

  @property
  def series_name(self):
    '''name of the season'''
    return self.object_dict.get('SeriesName')

  @property
  def genres(self):
    '''genres for the show'''
    return self.object_dict.get('SeriesGenres', [])

class Trailer(Video):
  '''Class representing trailer objects

  Parameters
  ----------
    object_dict : dict
      same as for `EmbyObject`
    connector : embypy.utils.connector.Connector
      same as for `EmbyObject`
  '''
  def __init__(self, object_dict, connector):
    super().__init__(object_dict, connector)

class AdultVideo(Video):
  '''Class representing adult vidoe objects

  Parameters
  ----------
    object_dict : dict
      same as for `EmbyObject`
    connector : embypy.utils.connector.Connector
      same as for `EmbyObject`
  '''
  def __init__(self, object_dict, connector):
    super().__init__(object_dict, connector)

class MusicVideo(Video):
  '''Class representing music video objects

  Parameters
  ----------
    object_dict : dict
      same as for `EmbyObject`
    connector : embypy.utils.connector.Connector
      same as for `EmbyObject`
  '''
  def __init__(self, object_dict, connector):
    super().__init__(object_dict, connector)
