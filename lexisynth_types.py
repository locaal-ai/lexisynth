class AudioSource:
    class SourceType:
        FILE = 0
        DEVICE = 1

    def __init__(self, sourceType, sourceName):
        self.sourceType = sourceType
        self.sourceName = sourceName
