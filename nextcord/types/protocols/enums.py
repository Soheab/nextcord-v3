from enum import IntEnum


class ChannelType(IntEnum):
    text = 0
    DM = 1
    voice = 2
    group_dm = 3
    category = 4
    news = 5
    store = 6
    news_thread = 10
    public_thread = 11
    private_thread = 12
    stage_voice = 13
