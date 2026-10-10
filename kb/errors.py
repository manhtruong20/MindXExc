class KBStorageError(ValueError):
    pass

class KBApiError(Exception):
    """Connecting to the Knowledge Base server failed."""