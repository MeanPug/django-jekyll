class CollectionSizeExceeded(Exception):
    """ raised when the number of docs found for a given collection exceeds the JEKYLL_MAX_COLLECTION_SIZE setting """
    pass


class DocGenerationFailure(Exception):
    """ raised when a Jekyll document fails to generate """
    pass