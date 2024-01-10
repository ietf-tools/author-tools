# [IETF Author Tools](https://author-tools.ietf.org)

## Documenation

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
