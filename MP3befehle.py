from micropython import const

CMD_PLAY_NEXT = const(0x01)
CMD_PLAY_PREV = const(0x02)
CMD_PLAY_W_INDEX = const(0x03)
CMD_SET_VOLUME = const (0x06)
CMD_SEL_DEV = const (0x09)
CMD_PLAY_W_VOL = const(0x22)
CMD_PLAY = const(0x0D)
CMD_PAUSE = const(0x0E)
CMD_SINGLE_CYCLE = const(0x19)
DEV_TF = const(0x02)
SINGLE_CYCLE_ON = const(0x00)
SINGLE_CYCLE_OFF = const(0x01)