import typing as t


class MiddlewareStack:
    def __init__(self, event, context, handler, middlewares):
        self.event = event
        self.context = context
        self.handler = handler
        self.middlewares = middlewares

    def __call__(self, event=None, context=None):
        event = event or self.event
        context = context or self.context
        if self.middlewares:
            [first, *rest] = self.middlewares
            nxt = MiddlewareStack(event, context, self.handler, rest)
            return first(event, context, nxt)
        else:
            return self.handler(event, context)


class MiddlewareHandler:
    def __init__(self, handler, middlewares: t.Optional[list] = None):
        self.handler = handler
        self.middlewares = middlewares or []

    def __call__(self, event, context):
        middlewarestack = MiddlewareStack(event, context, self.handler, self.middlewares)
        return middlewarestack(event, context)
    
    def add_middleware(self, middleware):
        self.middlewares.append(middleware)


class RouterHandler:
    def __init__(self, handler, routes):
        self.default_handler = handler
        self.routes = routes

    def __call__(self, event, context):
        for rule, handler in self.routes:
            if rule(event, context):
                return handler(event, context)
        return self.default_handler(event, context)
