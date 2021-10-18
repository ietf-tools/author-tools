# IETF @
IETF @ (IETF Author Tools)

## Documenation

* [API documenation](https://author-tools.ietf.org/doc/)
* [OpenAPI specification](api.yml)

## Running API service

```
docker-compose up
```

## Obtaining API key

API key can be generated from
[IETF datatracker](https://datatracker.ietf.org/accounts/apikey/add).

Select `/api/appauth/authortools` as the **Endpoint** and click **Create key**
button.

## Testing

* Test XML RFC generation
```
curl localhost:8888/api/render/xml -X POST -F "apikey=datatracker_authortools_api_key" -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

* Test HTML RFC generation
```
curl localhost:8888/api/render/html -X POST -F "apikey=datatracker_authortools_api_key" -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

* Test text RFC generation
```
curl localhost:8888/api/render/text -X POST -F "apikey=datatracker_authortools_api_key" -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

* Test PDF RFC generation
```
curl localhost:8888/api/render/pdf -X POST -F "apikey=datatracker_authortools_api_key" -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>" -o draft-output.pdf
```

* Test validation
```
curl localhost:8888/api/validate -X POST -F "apikey=datatracker_authortools_api_key" -F "file=@<xml2rfc draft (.xml) | Kramdown/mmark draft (.md, .mkd) | Text draft (.txt)>"
```

## Contributing

See [contributing guide](CONTRIBUTING.md).

## License

* [IETF @ - License](LICENSE)
