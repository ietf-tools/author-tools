# IETF @
IETF @ (IETF Author Tools)

## Documenation

* [API documenation](http://devbox.amsl.com:8080/api/)
* [OpenAPI specification](api.yml)

## Running API service

```
docker-compose up
```

## Testing

* Test XML RFC generation
```
curl localhost:8888/api/render/xml -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown draft (.md, .mkd) | Text draft (.txt)>"
```

* Test HTML RFC generation
```
curl localhost:8888/api/render/html -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown draft (.md, .mkd) | Text draft (.txt)>"
```

* Test text RFC generation
```
curl localhost:8888/api/render/text -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown draft (.md, .mkd) | Text draft (.txt)>"
```

* Test PDF RFC generation
```
curl localhost:8888/api/render/pdf -X POST -F "file=@<xml2rfc draft (.xml) | Kramdown draft (.md, .mkd) | Text draft (.txt)>" -o draft-output.pdf
```

## Contributing

See [contributing guide](CONTRIBUTING.md).

## License

* [IETF @ - License](LICENSE)
