import base64
import hashlib
import importlib
import warnings
from collections import OrderedDict
from functools import lru_cache

from core.utils.crypto import (
    constant_time_compare, get_random_string, pbkdf2
)


UNUSABLE_PASSWORD_PREFIX = '!'  # This will never be a valid encoded hash
UNUSABLE_PASSWORD_SUFFIX_LENGTH = 40  # number of random chars to add after UNUSABLE_PASSWORD_PREFIX


# TODO typing

@lru_cache()
def get_hashers():
    return [PBKDF2PasswordHasher()]


@lru_cache()
def get_hashers_by_algorithm():
    return {hasher.algorithm: hasher for hasher in get_hashers()}


def get_hasher(algorithm='default'):
    """
    Return an instance of a loaded password hasher.

    If algorithm is 'default', return the default hasher. Lazily import hashers
    specified in the project's settings file if needed.
    """
    if hasattr(algorithm, 'algorithm'):
        return algorithm

    elif algorithm == 'default':
        return get_hashers()[0]

    else:
        hashers = get_hashers_by_algorithm()
        try:
            return hashers[algorithm]
        except KeyError:
            raise ValueError("Unknown password hashing algorithm '%s'. "
                             "Did you specify it in the PASSWORD_HASHERS "
                             "setting?" % algorithm)


def mask_hash(hash, show=6, char="*"):
    """
    Return the given hash, with only the first ``show`` number shown. The
    rest are masked with ``char`` for security reasons.
    """
    masked = hash[:show]
    masked += char * len(hash[show:])
    return masked


def identify_hasher(encoded):
    """
    Return an instance of a loaded password hasher.

    Identify hasher algorithm by examining encoded hash, and call
    get_hasher() to return hasher. Raise ValueError if
    algorithm cannot be identified, or if hasher is not loaded.
    """
    # Ancient versions of Django created plain MD5 passwords and accepted
    # MD5 passwords with an empty salt.
    if ((len(encoded) == 32 and '$' not in encoded) or
            (len(encoded) == 37 and encoded.startswith('md5$$'))):
        algorithm = 'unsalted_md5'
    # Ancient versions of Django accepted SHA1 passwords with an empty salt.
    elif len(encoded) == 46 and encoded.startswith('sha1$$'):
        algorithm = 'unsalted_sha1'
    else:
        algorithm = encoded.split('$', 1)[0]
    return get_hasher(algorithm)


class BasePasswordHasher:
    """
    Abstract base class for password hashers

    When creating your own hasher, you need to override algorithm,
    verify(), encode() and safe_summary().

    PasswordHasher objects are immutable.
    """
    algorithm = None
    library = None

    def _load_library(self):
        if self.library is not None:
            if isinstance(self.library, (tuple, list)):
                name, mod_path = self.library
            else:
                mod_path = self.library
            try:
                module = importlib.import_module(mod_path)
            except ImportError as e:
                raise ValueError("Couldn't load %r algorithm library: %s" %
                                 (self.__class__.__name__, e))
            return module
        raise ValueError("Hasher %r doesn't specify a library attribute" %
                         self.__class__.__name__)

    def salt(self):
        """Generate a cryptographically secure nonce salt in ASCII."""
        return get_random_string()

    def verify(self, password, encoded):
        """Check if the given password is correct."""
        raise NotImplementedError('subclasses of BasePasswordHasher must provide a verify() method')

    def encode(self, password, salt):
        """
        Create an encoded database value.

        The result is normally formatted as "algorithm$salt$hash" and
        must be fewer than 128 characters.
        """
        raise NotImplementedError('subclasses of BasePasswordHasher must provide an encode() method')

    def safe_summary(self, encoded):
        """
        Return a summary of safe values.

        The result is a dictionary and will be used where the password field
        must be displayed to construct a safe representation of the password.
        """
        raise NotImplementedError('subclasses of BasePasswordHasher must provide a safe_summary() method')

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        """
        Bridge the runtime gap between the work factor supplied in `encoded`
        and the work factor suggested by this hasher.

        Taking PBKDF2 as an example, if `encoded` contains 20000 iterations and
        `self.iterations` is 30000, this method should run password through
        another 10000 iterations of PBKDF2. Similar approaches should exist
        for any hasher that has a work factor. If not, this method should be
        defined as a no-op to silence the warning.
        """
        warnings.warn('subclasses of BasePasswordHasher should provide a harden_runtime() method')


class PBKDF2PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the PBKDF2 algorithm (recommended)

    Configured to use PBKDF2 + HMAC + SHA256.
    The result is a 64 byte binary string.  Iterations may be changed
    safely but you must rename the algorithm if you change SHA256.
    """
    algorithm = "pbkdf2_sha256"
    iterations = 150000
    digest = hashlib.sha256

    def encode(self, password, salt, iterations=None):
        assert password is not None
        assert salt and '$' not in salt
        iterations = iterations or self.iterations
        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def verify(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return OrderedDict([
            ('algorithm', algorithm),
            ('iterations', iterations),
            ('salt', mask_hash(salt)),
            ('hash', mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        extra_iterations = self.iterations - int(iterations)
        if extra_iterations > 0:
            self.encode(password, salt, extra_iterations)


def make_password(password, salt=None):
    """
    Turn a plain-text password into a hash for database storage

    Same as encode() but generate a new random salt. If password is None then
    return a concatenation of UNUSABLE_PASSWORD_PREFIX and a random string,
    which disallows logins. Additional random string reduces chances of gaining
    access to staff or superuser accounts. See ticket #20079 for more info.
    """
    if password is None:
        return UNUSABLE_PASSWORD_PREFIX + get_random_string(UNUSABLE_PASSWORD_SUFFIX_LENGTH)
    hasher = get_hasher()

    if not salt:
        salt = hasher.salt()

    return hasher.encode(password, salt)


def is_password_usable(encoded):
    """
    Return True if this password wasn't generated by
    User.set_unusable_password(), i.e. make_password(None).
    """
    return encoded is None or not encoded.startswith(UNUSABLE_PASSWORD_PREFIX)


def check_password(password, encoded):
    """
    Return a boolean of whether the raw password matches the three
    part encoded digest.

    If setter is specified, it'll be called when you need to
    regenerate the password.
    """
    if password is None or not is_password_usable(encoded):
        return False

    preferred = get_hasher()
    hasher = identify_hasher(encoded)

    hasher_changed = hasher.algorithm != preferred.algorithm
    if hasher_changed:
        raise ValueError('Only one hash algorithm type can be used for password hashing.')

    is_correct = hasher.verify(password, encoded)

    return is_correct
