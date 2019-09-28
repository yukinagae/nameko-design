# nameko-design

WIP: Generate [Nameko](https://www.nameko.io/) http files from design schema inspired by [goa](https://goa.design/)

## Dependencies

- Python3.6
- [Poetry](https://github.com/sdispater/poetry)

## Installation

```bash
cd nameko-design
poetry install
```

## Usage

```bash
cd nameko-design
poetry run python cli/design.py
```

## Design

This API design schema

```python

with service("http service"):
    description("This is a http service")

    with method("liveness"):
        description("liveness probe")
        result(str)
        http('GET', '/liveness')

    with method("readiness"):
        description("readiness probe")
        result(str)
        http('GET', '/readiness')
```

will generate the below nameko file

```python
from nameko.web.handlers import http


class HttpService:
    name = "http service"

    @http('GET', '/liveness')
    def liveness(self, request)
        pass

    @http('GET', '/readiness')
    def readiness(self, request)
        pass
```
