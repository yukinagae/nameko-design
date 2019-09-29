import argparse
import threading
from enum import Enum
from jinja2 import Template


class Context:
    contexts = threading.local()

    @classmethod
    def get_contexts(cls):
        if not hasattr(cls.contexts, 'stack'):
            cls.contexts.stack = []
        return cls.contexts.stack

    @classmethod
    def get_context(cls):
        try:
            return cls.get_contexts()[-1]
        except IndexError:
            raise TypeError("No context on context stack")


class Service(Context):

    def __new__(cls, *args, **kwargs):
        instance = super(Service, cls).__new__(cls)
        if cls.get_contexts():
            instance.parent = cls.get_contexts()[-1]
        else:
            instance.parent = None
        return instance

    def __init__(self, name: str):
        self.name = name
        self.named_methods = {}

    def __enter__(self):
        type(self).get_contexts().append(self)
        return self

    def __exit__(self, typ, value, traceback):
        self.generate()
        type(self).get_contexts().pop()

    def title(self, val: str):
        self.title = val
        return self

    def generate(self):
        template = Template("""
from nameko.web.handlers import http


class HttpService:
    name = '{{ name }}
""")
        print(template.render(
            name=self.name,
        ))

        for _, method in self.named_methods.items():
            print(method.generate())

    def __str__(self) -> str:
        return f"name: {self.name}, title: {self.title}"

    def add_method(self, method):
        if method.name in self.named_methods:
            raise ValueError(
                "Variable name {} already exists.".format(method.name))
        self.named_methods[method.name] = method


class Method(Context):

    def __new__(cls, *args, **kwargs):
        instance = super(Method, cls).__new__(cls)
        if cls.get_contexts():
            instance.parent = cls.get_contexts()[-1]
        else:
            instance.parent = None
        return instance

    def __init__(self, name: str):
        self.service = Service.get_context()
        self.name = name
        self.service.add_method(self)

    def __enter__(self):
        type(self).get_contexts().append(self)
        return self

    def __exit__(self, typ, value, traceback):
        type(self).get_contexts().pop()

    def description(self, val: str):
        self.description = val
        return self

    def result(self, result_type: type):
        self.result = result_type
        return self

    def http(self, http):
        self.http = http
        return self

    def generate(self):
        template = Template("""
    @http('{{ http_method }}', '{{ path }}')
    def {{ name }}(self, request) -> {{ result }}:
        pass
        """)
        return template.render(
            name=self.name,
            http_method=str(self.http.http_method),
            path=self.http.path,
            result=self.result.__name__
        )

    def __str__(self) -> str:
        return f"name: {self.name}, description: {self.description}, result: {self.result}, http: {self.http}"


# Service Classes
class Title:

    def __init__(self, name):
        self.service = Service.get_context()
        self.service.title(name)


# Method Classes
class Description:

    def __init__(self, name):
        self.method = Method.get_context()
        self.method.description(name)


class Result:

    def __init__(self, result_type):
        self.method = Method.get_context()
        self.method.result(result_type)


class HTTP:

    def __init__(self, http_method: str, path: str):
        self.http_method = http_method
        self.path = path
        self.method = Method.get_context()
        self.method.http(self)

    def __str__(self) -> str:
        return f"http_method: {self.http_method}, path: {self.path}"


class HTTPMethod(Enum):
    GET = 'GET',
    POST = 'POST',
    DELETE = 'DELETE',
    PUT = 'PUT'

    def __str__(self) -> str:
        return self.value[0]  # ex) Tuple('GET') -> 'GET'


GET = HTTPMethod.GET
POST = HTTPMethod.POST
DELETE = HTTPMethod.DELETE
PUT = HTTPMethod.PUT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)

    args = parser.parse_args()
    with open(args.file, "r") as f:
        exec(f.read())
