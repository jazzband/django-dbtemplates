import os
from django.conf import settings
from django.core.cache import cache
from django.template import TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_unicode, force_unicode

class BaseCacheBackend(object):
    """
    Base class for custom cache backend of dbtemplates to be used while
    subclassing.

    Set DBTEMPLATES_CACHE_BACKEND setting to the Python path to that subclass.
    """
    def _site(self):
        from django.contrib.sites.models import Site
        return Site.objects.get_current()
    site = property(_site)

    def load(self, name):
        """
        Loads a template from the cache with the given name.
        """
        raise NotImplemented

    def save(self, name, content):
        """
        Saves the given template content with the given name in the cache.
        """
        raise NotImplemented

    def remove(self, name):
        """
        Removes the template with the given name from the cache.
        """
        raise NotImplemented

class DjangoCacheBackend(BaseCacheBackend):
    """
    A cache backend that uses Django's cache mechanism.
    """
    def _cache_key(self, name):
        return 'dbtemplates::%s::%s' % (name, self.site.pk)

    def load(self, name):
        cache_key = self._cache_key(name)
        return cache.get(cache_key)

    def save(self, name, content):
        cache_key = self._cache_key(name)
        cache.set(cache_key, content)

    def remove(self, name):
        cache_key = self._cache_key(name)
        cache.delete(cache_key)

class FileSystemBackend(BaseCacheBackend):
    """
    A cache backend that uses simple files to hold the template cache.
    """
    def __init__(self):
        try:
            self.cache_dir = getattr(settings, 'DBTEMPLATES_CACHE_DIR', None)
            self.cache_dir = os.path.normpath(self.cache_dir)
            if not os.path.isdir(self.cache_dir):
                pass
        except:
            raise ImproperlyConfigured("You're using the dbtemplates file system cache backend without having set the DBTEMPLATES_CACHE_DIR setting to a valid value. Make sure the directory exists and is writeable for the user your Django instance is running with.")
        super(FileSystemBackend, self).__init__()

    def _filepath(self, name):
        return os.path.join(self.cache_dir, self.site.domain, name)

    def load(self, name):
        try:
            filepath = self._filepath(name)
            return open(filepath).read().decode('utf-8')
        except:
            return None

    def save(self, name, content, retry=False):
        try:
            filepath = self._filepath(name)
            dirname = os.path.dirname(filepath)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            cache_file = open(filepath, 'w')
            cache_file.write(force_unicode(content).encode('utf-8'))
            cache_file.close()
        except Exception:
            raise

    def remove(self, name):
        try:
            filepath = self._filepath(name)
            os.remove(filepath)
        except:
            pass
