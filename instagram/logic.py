import instaloader
import cachetools.func


class InstagramMediaDownloader:
    def __init__(self, login: str, password: str):
        self.account = instaloader.Instaloader()
        self.account.login(login, password)

    @property
    def context(self):
        return self.account.context

    @cachetools.func.ttl_cache(maxsize=None, ttl=60 * 60 * 2)
    def get_post(self, shortcode: str):
        post = instaloader.Post.from_shortcode(self.context, shortcode)
        return post

    @cachetools.func.ttl_cache(maxsize=None, ttl=60 * 60 * 2)
    def get_reels(self, shortcode: str):
        return self.get_post(shortcode)

    @cachetools.func.ttl_cache(maxsize=None, ttl=60 * 60 * 2)
    def get_stories(self, media_id: int):
        stories = instaloader.StoryItem.from_mediaid(self.context, media_id)
        return stories

    @cachetools.func.ttl_cache(maxsize=None, ttl=60 * 60 * 2)
    def get_user(self, username: str):
        user = instaloader.Profile.from_username(self.context, username)
        return user

