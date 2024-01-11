<div align="center">
  
<img src="https://raw.githubusercontent.com/ietf-tools/common/main/assets/logos/authortools.svg" alt="IETF Author Tools" height="125" />

[![Release](https://img.shields.io/github/release/ietf-tools/ietf-at.svg?style=flat&maxAge=300)](https://github.com/ietf-tools/ietf-at/releases)
[![License](https://img.shields.io/github/license/ietf-tools/ietf-at?20240110)](https://github.com/ietf-tools/ietf-at/blob/main/LICENSE)

##### IETF Author Tools

</div>

- [**Production Website**](https://datatracker.ietf.org)
- [Changelog](https://github.com/ietf-tools/ietf-at/releases)
- [Contributing](https://github.com/ietf-tools/ietf-at/blob/main/LICENSE)
- [Documentation](#documentation)
- [Running Author Tools service](#running-author-tools-service)
- [Testing Web UI](#testing-web-ui)
- [Testing API](#testing-api)

---

## Documentation

* [API documenation](https://author-tools.ietf.org/doc/)
* [OpenAPI specification](api.yml)

## Running Author Tools service

```
docker-compose up --build -d
```

## Testing Web UI

* Visit http://localhost:8888

## Testing API

* Test XML RFC generation
```
curl localhost:8888/api/render/xml -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

* Test HTML RFC generation
```
curl localhost:8888/api/render/html -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

* Test text RFC generation
```
curl localhost:8888/api/render/text -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

* Test PDF RFC generation
```
curl localhost:8888/api/render/pdf -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>" -o draft-output.pdf
```

* Test validation
```
curl localhost:8888/api/validate -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

## Contributing

See [contributing guide](CONTRIBUTING.md).

## License

* [IETF Author Tools License](LICENSE)
