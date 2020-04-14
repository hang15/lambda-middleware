class DecoratorMiddleware:
    def __init__(self, decorator):
        self.decorator = decorator

    def __call__(self, event, context, nxt):
        return self.decorator(nxt)(event, context)
