""" Utilities """
from distlib.util import split_filename
from distlib.locators import Locator, SimpleScrapingLocator
from six.moves.urllib.parse import urlparse  # pylint: disable=F0401,E0611
import posixpath

ALL_EXTENSIONS = Locator.source_extensions + Locator.binary_extensions


def parse_filename(filename, name=None):
    """ Parse a name and version out of a filename """
    version = None
    for ext in ALL_EXTENSIONS:
        if filename.endswith(ext):
            trimmed = filename[:-len(ext)]
            parsed_name, version = split_filename(trimmed, name)[:2]
            break
    if version is None:
        raise ValueError("Cannot parse package file '%s'" % filename)
    if name is None:
        name = parsed_name
    return normalize_name(name), version


def normalize_name(name):
    """ Normalize a python package name """
    return name.lower().replace('-', '_')


class FilenameScrapingLocator(SimpleScrapingLocator):

    """
    This locator should only be used for get_project. It hacks the
    SimpleScrapingLocator to return all found distributions, rather than a
    unique dist per version number.

    """

    def _update_version_data(self, result, info):
        version = info['version']
        filename = info['filename']
        super(FilenameScrapingLocator, self)._update_version_data(result, info)
        result[filename] = result[version]
        del result[version]


class BetterScrapingLocator(SimpleScrapingLocator):

    """ Layer on top of SimpleScrapingLocator that allows preferring wheels """

    def __init__(self, *args, **kwargs):
        self.prefer_wheel = kwargs.pop('wheel', True)
        super(BetterScrapingLocator, self).__init__(*args, **kwargs)

    def score_url(self, url):
        t = urlparse(url)
        filename = posixpath.basename(t.path)
        return (
            t.scheme == 'https',
            not (self.prefer_wheel ^ filename.endswith('.whl')),
            'pypi.python.org' in t.netloc,
            filename,
        )