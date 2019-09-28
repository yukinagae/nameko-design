from jinja2 import Template


class Service:

    def __init__(self, name: str):
        self.name = name
        self.methods = []

    def description(self, val: str):
        self.description = val
        return self

    def method(self, name: str):
        method = Method(name)
        self.methods.append(method)
        return method

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
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._generate()
        return self

    def __str__(self) -> str:
        return f"name: {self.name}, description: {self.description}"


class Method:

    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self

    def description(self, val: str):
        self.description = val
        return self

    def result(self, result_type: type):
        self.result = result_type
        return self

    def http(self, method, path):
        self.http = Http(method, path)
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


class Http:

    def __init__(self, method: str, path: str):
        self.method = method
        self.path = path

    def __str__(self) -> str:
        return f"method: {self.method}, path: {self.path}"


def service(name: str):
    return Service(name)


def method(name: str):
    return Method(name)


if __name__ == '__main__':

    with service("http service") as s:
        s.description("This is a http service")

        with s.method("liveness") as m:
            m.description("liveness probe")
            m.result(str)
            m.http('GET', '/liveness')

        with s.method("readiness") as m:
            m.description("readiness probe")
            m.result(str)
            m.http('GET', '/readiness')
