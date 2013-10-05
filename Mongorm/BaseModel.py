
class BaseModel(object):

    def _presave(self, entityManager):
        """
        Hook for pre-save event
        """
        pass

    def _postsave(self, entityManager):
        """
        Hook for post-save event
        """
        pass