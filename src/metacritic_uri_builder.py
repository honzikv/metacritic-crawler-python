# Module for uri building

_METACRITIC_URL = 'https://www.metacritic.com'
_MOVIE_RELEASE_URL = f'{_METACRITIC_URL}/browse/movies/score/metascore/year'
_GAME_RELEASE_URL = f'{_METACRITIC_URL}/browse/games/score/metascore/year'


# Functions for url creations

def create_movies_url(year: int, page: int = 0):
    return f'{_MOVIE_RELEASE_URL}/filtered?year_selected={year}&sort=desc&view=detailed&page={page}'


def create_games_url(year: int, page: int = 0):
    return f'{_GAME_RELEASE_URL}/filtered?year_selected={year}&sort=desc&view=detailed&page={page}'


def create_absolute_item_url(relative_url: str): return f'{_METACRITIC_URL}/{relative_url}'


def create_critic_reviews_url(base_url: str): return f'{base_url}/critic-reviews'


def create_user_reviews_url(base_url: str): return f'{base_url}/user-reviews'
