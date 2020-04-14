import json
from functools import wraps

from lambda_middeware.handlers import MiddlewareHandler
from lambda_middeware.middleware import DecoratorMiddleware


class TraceMiddleware:
    def __init__(self, name):
        self.name = name

    def __call__(self, event, context, nxt):
        event['trace'].append(f'Enter {self.name}')
        res = nxt(event, context)
        event['trace'].append(f'Exit {self.name}')
        return res


def dummy_handler(event, context):
    event['trace'].append('Enter handler')
    return 'Hello World'


def test_middleware_handler():
    middlewares = [
        TraceMiddleware(1),
        TraceMiddleware(2)
    ]
    handler = MiddlewareHandler(dummy_handler, middlewares)
    event = {'trace': []}
    res = handler(event, None)
    assert res == 'Hello World'
    assert event['trace'] == ['Enter 1', 'Enter 2', 'Enter handler', 'Exit 2', 'Exit 1']
    print(event)


def json_http_resp(handler_or_none=None, **json_dumps_kwargs):
    """
Simplified decorator from lambda_decorators

Automatically serialize return value to the body of a successfull HTTP
response.
Returns a 500 error if the response cannot be serialized
    """

    if handler_or_none is not None and len(json_dumps_kwargs) > 0:
        raise TypeError(
            "You cannot include both handler and keyword arguments. How did you even call this?"
        )
    if handler_or_none is None:

        def wrapper_wrapper(handler):
            @wraps(handler)
            def wrapper(event, context):
                resp = handler(event, context)
                if isinstance(resp, dict):
                    status = resp.pop('statusCode', 200)
                else:
                    status = 200
                if isinstance(resp, dict):
                    headers = resp.pop('headers', None)
                else:
                    headers = None
                http_resp = {
                    "statusCode": status,
                    "body": json.dumps(
                        resp, **json_dumps_kwargs
                    ),
                }
                if headers:
                    http_resp["headers"] = headers
                return http_resp
            return wrapper

        return wrapper_wrapper
    else:
        return json_http_resp()(handler_or_none)


def test_decorator_middleware():
    handler = MiddlewareHandler(dummy_handler, middlewares=[DecoratorMiddleware(json_http_resp())])
    event = {'trace': []}
    res = handler(event, None)
    assert res == {'statusCode': 200, 'body': '"Hello World"'}
