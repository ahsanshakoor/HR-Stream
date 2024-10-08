class ObjectNotFound(Exception):

    def __init__(self, template):

        # call the base class constructor
        Exception.__init__(self, 'Object not found')

        # set the template
        self.template = template