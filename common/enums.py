import enum


class FatAccumulation(enum.Enum):
    NORMAL = "正常"
    EXCESSIVE = "过多"
    INSUFFICIENT = "过少"

    @property
    def description_fat(self):
        return self.value


class DrowsinessDegree(enum.Enum):
    NORMAL = "正常"
    SUSPICIOUS = "可疑嗜睡"
    EXCESSIVE = "过度嗜睡"

    @property
    def description(self):
        return self.value


class SleepinessLevel(enum.Enum):
    N0_CHANCE = 0  # 从不打瞌睡
    SLIGHT_CHANCE = 1  # 打瞌睡的可能性很小
    MODERATE_CHANCE = 2  # 打瞌睡的可能性中等
    HIGH_CHANCE = 3  # 很大可能打瞌睡


class PhotoType(str, enum.Enum):
    front = "front"
    side = "side"


class StatusEnum(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class NeckLength(enum.Enum):
    NORMAL = '正常'
    ABNORMAL = '异常'

    @property
    def description(self):
        return self.value

class LowerJaw(enum.Enum):
    NORMAL = '正常'
    ABNORMAL = '异常'

    @property
    def description(self):
        return self.value

class Nasolabial(enum.Enum):
    NORMAL = '正常'
    ABNORMAL = '异常'

    @property
    def description(self):
        return self.value
