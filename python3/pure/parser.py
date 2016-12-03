import collections


class Config(object):

    def __init__(self):
        self.properties = collections.OrderedDict()

    def get(self, prop):
        return self.properties.get(prop)


def parse(raw_input):
    config = Config()

    for line in raw_input.splitlines():
        tokens = line.split()

        prop = tokens[0]
        value = tokens[2]

        config.properties[prop] = value

    return config
