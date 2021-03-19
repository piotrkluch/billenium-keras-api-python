from collections.abc import Container


class UniversalContainer(Container):

    def __contains__(self, _):
        return True


_universal_container = UniversalContainer()


def universal_container():
    return _universal_container
