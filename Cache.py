__cache = {}


def set(key, val):
  __cache[key] = val


def get(key):
  return __cache.get(key)


def earse(key):
  if (key in __cache):
    del __cache[key]
