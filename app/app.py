from flask import Flask
from radarrMover import RadarrMover
import asyncio
import os

def main():
    host_url = os.environ.get('RADARR_URL', '')
    api_key = os.environ.get('RADARR_API_KEY', '')

    mover = RadarrMover(host_url, api_key)

    api = Flask(__name__)

    @api.route('/movie/<int:tmdbId>/', methods=['POST'], strict_slashes=False)
    def update_movie(tmdbId):
        asyncio.run(mover.updateMovie(tmdbId))
        return ''

    api.run(host='0.0.0.0', port='8781')

main()