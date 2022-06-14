from pyarr import RadarrAPI
import asyncio
import re

class RadarrMover:
    def __init__(self, host_url, api_key):
        self.host_url = host_url
        self.api_key = api_key
        self.radarr = RadarrAPI(host_url, api_key)

    async def updateMovie(self, tmdbId):
        movies = self.radarr.get_movie(tmdbId)

        if (movies == None or len(movies) == 0):
            return

        movie = movies[0]

        isKidCert = self.determineKidCert(movie)

        if (not isKidCert):
            return

        updatedPath = self.updateMoviePath(movie)

        updatedTags = self.updateMovieTags(movie)

        if (updatedTags or updatedPath):
            self.radarr.upd_movie(movie, True)

    def updateMoviePath(self, movie):
        rootPaths = self.getRootPaths()
        kidPath = self.getKidPath(rootPaths)

        moviePath = movie['path']

        isKidPath = re.search(kidPath, moviePath, re.IGNORECASE)

        if (not isKidPath):
            currentPath = next(filter(lambda path: re.search(path['path'], moviePath, re.IGNORECASE), rootPaths))
            movieName = re.sub(currentPath['path'], '', moviePath)

            newPath = f"{kidPath}{movieName}"
            movie['path'] = newPath

        return (not isKidPath)

    def determineKidCert(self, movie):
        certification = movie['certification']
        kidCerts = ['G', 'PG']

        return (certification in kidCerts)

    def updateMovieTags(self, movie):
        tags = self.getTags()
        kidTag = self.getTag(tags, 'kidmovie')
        movieTag = self.getTag(tags, 'movies')

        movieTags = movie['tags']

        addedKidTag = False
        removedTag = False

        if (movieTag['id'] in movieTags):
            removedTag = True
            movieTags.remove(movieTag['id'])

        if (not (kidTag['id'] in movieTags)):
            addedKidTag = True
            movieTags.append(kidTag['id'])

        if (removedTag or addedKidTag):
            movie['tags'] = movieTags

        return removedTag or addedKidTag

    def getTags(self):
        return self.radarr.get_tag()

    def getTag(self, tags, tagName):
        return next(filter(lambda tag: tag['label'] == tagName, tags), None)

    def getRootPaths(self):
        return self.radarr.get_root_folder()

    def getKidPath(self, paths):
        kid = next(filter(lambda path: re.search('kidmovies', path['path'], re.IGNORECASE), paths), None)
        return kid['path']