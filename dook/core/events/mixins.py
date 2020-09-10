class ModelEventMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = self.events_class(self)
