from collections import namedtuple
from typing import Optional, List

ChannelType = namedtuple('ChannelType', ('id', 'name', 'title', 'unit'))

types = (
    ChannelType(
        id=0,
        name='temperature',
        title='Temperatura',
        unit='℃'
    ),
    ChannelType(
        id=1,
        name='pressure',
        title='Ciśnienie',
        unit='hPa'
    )
)


def get_types() -> List[ChannelType]:
    """
    Get all ChannelType objects.
    """
    return types


def get_type_by_id(type_id: int) -> Optional[ChannelType]:
    """
    Get ChannelType object with specified type ID.
    """
    for channel_type in types:
        if channel_type.id == type_id:
            return channel_type

    return None
