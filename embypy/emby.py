from simplejson.scanner import JSONDecodeError

from embypy import objects
from embypy.utils import Connector
from embypy.utils.asyncio import async_func


class Emby(objects.EmbyObject):
    '''Emby connection class, an object of this type should be created
    to communicate with emby

    Parameters
    ----------
    url : str
      url to the server (e.g. http://127.0.0.1:8096/)

    api_key : str, optional
      key obtained from server dashboard
    device_id : str, optional
      device id to pass to emby

    username : str, optional
      username to login, this+password can be used instead of an apikey
    password : str, optional
      password for user to login as

    Attributes
    ----------
    connector : embypy.utils.connector.Connector
      Object used to make api requests, do not use
    '''
    def __init__(self, url, **kargs):
        connector = Connector(url, **kargs)
        super().__init__({'ItemId': '', 'Name': ''}, connector)

    @async_func
    async def info(self, obj_id=None):
        '''Get info about object id

        |coro|

        Parameters
        ----------
        obj_id : str, list
          if not provided, server info is retured(as a dict).
          Otherwise, an object with that id is returned
          (or objects if `obj_id` is a list).
        '''
        if obj_id:
            try:
                return await self.process(obj_id)
            except JSONDecodeError:
                raise LookupError(
                    'Error object with that id does not exist',
                    obj_id
                )
        else:
            return await self.connector.info()

    @async_func
    async def search(
        self, query,
        sort_map={'BoxSet':0, 'Series':1, 'Movie':2, 'Audio':3, 'Person':4},
        strict_sort=False
    ):
        '''Sends a search request to emby, returns results

        |coro|

        Parameters
        ----------
        query : str
          the search string to send to emby
        sort_map : dict
          is a dict of strings to ints. Strings should be item types, and
          the ints are the priority of those types(for sorting).
          lower valued(0) will appear first.
        strict_sort : bool
          if True, then only item types in the keys of sortmap will be
          included in the results

        Returns
        -------
        list
          list of emby objects
        '''
        search_params = {
            'remote'     : False,
            'searchTerm' : query
        }
        if strict_sort:
            search_params['IncludeItemTypes'] = ','.join(sort_map.keys())

        json = await self.connector.getJson('/Search/Hints/', **search_params)
        items = await self.process(json["SearchHints"])

        m_size = len(sort_map)
        items = sorted(items, key=lambda x: sort_map.get(x.type, m_size))

        return items

    @async_func
    async def latest(self, userId=None, itemTypes='', groupItems=False):
        '''returns list of latest items

        |coro|

        Parameters
        ----------
        userId : str
          if provided, then the list returned is
          the one that that use will see.
        itemTypes: str
          if provided, then the list will only include items
          if that type - gets passed to the emby api
          see https://github.com/MediaBrowser/Emby/wiki/Item-Types

        Returns
        -------
        list
          the itmes that will appear as latest (for user if id was given)
        '''
        json = await self.connector.getJson(
            '/Users/{UserId}/Items/Latest',
            remote=False,
            userId=userId,
            IncludeItemTypes=itemTypes,
            GroupItems=groupItems,
        )
        return await self.process(json)

    @async_func
    async def nextUp(self, userId=None):
        '''returns list of items marked as `next up`

        |coro|

        Parameters
        ----------
        userId : str
          if provided, then the list returned is
          the one that that use will see.

        Returns
        -------
        list
          the itmes that will appear as next up
          (for user if id was given)
        '''
        json = await self.connector.getJson(
            '/Shows/NextUp',
            pass_uid=True,
            remote=False,
            userId=userId
        )
        return await self.process(json)

    @async_func
    async def update(self):
        '''
        reload all cached information

        |coro|

        Notes
        -----
        This is a slow process, and will remove the cache before updating.
        Thus it is recomended to use the `*_force` properties, which will
        only update the cache after data is retrived.
        '''
        keys = self.extras.keys()
        self.extras = {}
        for key in keys:
            try:
                func = getattr(self, key, None)
                if callable(func):
                    func()
            except:
                pass

    @async_func
    async def create_playlist(self, name, *songs):
        '''create a new playlist

        |coro|

        Parameters
        ----------
        name : str
          name of new playlist
        songs : array_like
          list of song ids to add to playlist
        '''
        data = {'Name': name}
        ids = [i.id for i in (await self.process(songs))]

        if ids:
            data['Ids'] = ','.join(ids)

        # TODO - return playlist(s?)
        await self.connector.post(
            '/Playlists',
            data=data,
            pass_uid=True,
            remote=False
        )

    @property
    @async_func
    async def albums(self):
        '''returns list of all albums.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Album`
        '''
        return self.extras.get('albums') or await self.albums_force

    @property
    @async_func
    async def albums_force(self):
        items = await self.connector.getJson(
            '/Users/{UserId}/Items',
            remote            = False,
            format            = 'json',
            Recursive         = 'true',
            IncludeItemTypes  = 'MusicAlbum',
            Fields            = 'Path,ParentId,Overview,Genres,Tags,Artists',
            SortBy            = 'SortName',
            SortOrder         = 'Ascending'
        )
        items = await self.process(items)
        self.extras['albums'] = items
        return items

    @property
    @async_func
    async def songs(self):
        '''returns list of all songs.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Audio`
        '''
        return self.extras.get('songs') or await self.songs_force

    @property
    @async_func
    async def songs_force(self):
        items = await self.connector.getJson(
            '/Users/{UserId}/Items',
            remote            = False,
            format            = 'json',
            Recursive         = 'true',
            IncludeItemTypes  = 'Audio',
            Fields            = 'Path,ParentId,Overview,Genres,Tags,Artists',
            SortBy            = 'SortName',
            SortOrder         = 'Ascending'
        )
        items = await self.process(items)
        self.extras['songs'] = items
        return items

    @property
    @async_func
    async def playlists(self):
        '''returns list of all playlists.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Playlist`
        '''
        return self.extras.get('playlists') or await self.playlists_force

    @property
    @async_func
    async def playlists_force(self):
        items = await self.connector.getJson(
            '/Users/{UserId}/Items',
            remote            = False,
            format            = 'json',
            Recursive         = 'true',
            IncludeItemTypes  = 'Playlist',
            Fields            = 'Path,ParentId,Overview',
            SortBy            = 'SortName',
            SortOrder         = 'Ascending'
        )
        items = await self.process(items)
        self.extras['playlists'] = items
        return items

    @property
    @async_func
    async def artists(self):
        '''returns list of all song artists.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Artist`
        '''
        return self.extras.get('artists', []) or await self.artists_force

    @property
    @async_func
    async def artists_force(self):
        items = await self.connector.getJson(
            '/Users/{UserId}/Items',
            remote            = False,
            format            = 'json',
            Recursive         = 'true',
            IncludeItemTypes  = 'MusicArtist',
            Fields            = 'Path,ParentId,Overview,Genres,Tags',
            SortBy            = 'SortName',
            SortOrder         = 'Ascending'
        )
        items = await self.process(items)
        self.extras['artists'] = items
        return items

    @property
    @async_func
    async def movies(self):
        '''returns list of all movies.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Movie`
        '''
        return self.extras.get('movies', []) or await self.movies_force

    @property
    @async_func
    async def movies_force(self):
        items = await self.connector.getJson(
            '/Users/{UserId}/Items',
            remote            = False,
            format            = 'json',
            Recursive         = 'true',
            IncludeItemTypes  = 'Movie',
            Fields            = 'Path,ParentId,Overview,Genres,Tags,ProviderIds',
            SortBy            = 'SortName',
            SortOrder         = 'Ascending'
        )
        items = await self.process(items)
        self.extras['movies'] = items
        return items

    @property
    @async_func
    async def series(self):
        '''returns a list of all series in emby.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Series`
        '''
        return self.extras.get('series', []) or await self.series_force

    @property
    @async_func
    async def series_force(self):
        items = await self.connector.getJson(
            '/Users/{UserId}/Items',
            remote            = False,
            format            = 'json',
            Recursive         = 'true',
            IncludeItemTypes  = 'Series',
            Fields            = 'Path,ParentId,Overview,Genres,Tags',
            SortBy            = 'SortName',
            SortOrder         = 'Ascending'
        )
        items = await self.process(items)
        self.extras['series'] = items
        return items

    @property
    @async_func
    async def episodes(self):
        '''returns a list of all episodes in emby.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Episode`
        '''
        return self.extras.get('episodes', []) or await self.episodes_force

    @property
    @async_func
    async def episodes_force(self):
        items = await self.connector.getJson(
            '/Users/{UserId}/Items',
            remote            = False,
            format            = 'json',
            Recursive         = 'true',
            IncludeItemTypes  = 'Episode',
            Fields            = 'Path,ParentId,Overview,Genres,Tags',
            SortBy            = 'SortName',
            SortOrder         = 'Ascending'
        )
        items = await self.process(items)
        self.extras['episodes'] = items
        return items

    @property
    @async_func
    async def devices(self):
        '''returns a list of all devices connected to emby.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Devices`
        '''
        return self.extras.get('devices', []) or await self.devices_force

    @property
    @async_func
    async def devices_force(self):
        items = await self.connector.getJson('/Devices', remote=False)
        items = await self.process(items)
        self.extras['devices'] = items
        return items

    @property
    @async_func
    async def users(self):
        '''returns a list of all users.

        |force|

        |coro|

        Returns
        -------
        list
          of type :class:`embypy.objects.Users`
        '''
        return self.extras.get('users', []) or await self.users_force

    @property
    @async_func
    async def users_force(self):
        items = await self.connector.getJson('/Users', remote=False)
        items = await self.process(items)
        self.extras['users'] = items
        return items
