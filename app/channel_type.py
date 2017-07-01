from enum import Enum


class ChannelType(Enum):
    FLOATING = 0
    COLOR = 1

    def translate(self, *args):
        return self.value
