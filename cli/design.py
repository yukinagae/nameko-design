import threading
from jinja2 import Template


class Context:
    """Functionality for objects that put themselves in a context using
    the `with` statement.
    """
    contexts = threading.local()

    def __enter__(self):
        type(self).get_contexts().append(self)
        return self

    def __exit__(self, typ, value, traceback):
        type(self).get_contexts().pop()


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

    def title(self, val: str):
        self.title = val
        return self

    def _generate(self):
        template = Template("""
from nameko.web.handlers import http


class HttpService:
    name = "{{ name }}"
""")
        print(template.render(
            name=self.name,
        ))

        for method in self.methods:
            print(method.generate())
    
    def __str__(self) -> str:
        return f"name: {self.name}, title: {self.title}"

    @classmethod
    def get_contexts(cls):
        # no race-condition here, cls.contexts is a thread-local object
        # be sure not to override contexts in a subclass however!
        if not hasattr(cls.contexts, 'stack'):
            cls.contexts.stack = []
        return cls.contexts.stack

    @classmethod
    def get_context(cls):
        """Return the deepest context on the stack."""
        try:
            return cls.get_contexts()[-1]
        except IndexError:
            raise TypeError("No context on context stack")

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
    def {{ name }}(self, request)
        pass
        """)
        return template.render(
            name=self.name,
            http_method=self.http.method,
            path=self.http.path
        )

    def __str__(self) -> str:
        return f"name: {self.name}, description: {self.description}, result: {self.result}, http: {self.http}"

    @classmethod
    def get_contexts(cls):
        # no race-condition here, cls.contexts is a thread-local object
        # be sure not to override contexts in a subclass however!
        if not hasattr(cls.contexts, 'stack'):
            cls.contexts.stack = []
        return cls.contexts.stack

    @classmethod
    def get_context(cls):
        """Return the deepest context on the stack."""
        try:
            return cls.get_contexts()[-1]
        except IndexError:
            raise TypeError("No context on context stack")


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


class Http:

    def __init__(self, http_method: str, path: str):
        self.http_method = http_method
        self.path = path
        self.method = Method.get_context()
        self.method.http(self)

    def __str__(self) -> str:
        return f"http_method: {self.http_method}, path: {self.path}"


if __name__ == '__main__':

    with Service("name"):
        Title("This is a http service")
        with Method("liveness"):
            Description("liveness probe")
            Result(str)
            Http('GET', '/liveness')
            m = Method.get_contexts()[-1]
            print(m)

        s = Service.get_contexts()[-1]
        print(s)
