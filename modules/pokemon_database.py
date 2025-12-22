import pickle
import os
import logging
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PokeDatabase:
    def __init__(self, path):
        self.path = path
        self.pokemon = [] # List of all pokemon
        self.dex_to_index = {} # Map of dex number to index in self.pokemon
        self.name_to_index = {} # Map of name to index in self.pokemon

        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, 'images'), exist_ok=True)

    def add_pokemon(self, pokemon):
        self.pokemon.append(pokemon)
        # Cache the images locally
        self.cache_images(pokemon)

        # Add to the index
        self.dex_to_index[pokemon.dex] = len(self.pokemon) - 1
        self.name_to_index[pokemon.name] = len(self.pokemon) - 1

    def cache_images(self, pokemon):
        def download_image(url, filename):
            with open(filename, 'wb') as f:
                f.write(requests.get(url).content)

        sprites = pokemon.sprites

        for key in sprites.front:
            url = sprites.front[key]
            if url is None:
                continue
            extension = url.split('.')[-1]
            filename = os.path.join(self.path, 'images', f'{pokemon.name}_front_{key}.{extension}')
            download_image(url, filename)
            pokemon.sprites.front[key] = filename

        for key in sprites.back:
            url = sprites.back[key]
            if url is None:
                continue
            extension = url.split('.')[-1]
            filename = os.path.join(self.path, 'images', f'{pokemon.name}_back_{key}.{extension}')
            download_image(url, filename)
            pokemon.sprites.back[key] = filename

    def get(self, dex=None, name=None):
        assert dex is not None or name is not None, 'Either dex or name must be provided'
        assert dex is None or name is None, 'Only one of dex or name must be provided'

        if dex is not None:
            return self.pokemon[self.dex_to_index[dex]]
        if name is not None:
            return self.pokemon[self.name_to_index[name]]

    def save(self):
        with open(os.path.join(self.path, 'database.pkl'), 'wb') as f:
            pickle.dump({'pokemon': self.pokemon, 'dex_to_index': self.dex_to_index, 'name_to_index': self.name_to_index}, f)
        logger.info(f'Saved database to {self.path}')

    def load(self):
        with open(os.path.join(self.path, 'database.pkl'), 'rb') as f:
            data = pickle.load(f)
            self.pokemon = data['pokemon']
            self.dex_to_index = data['dex_to_index']
            self.name_to_index = data['name_to_index']
        logger.info(f'Loaded database from {self.path}')