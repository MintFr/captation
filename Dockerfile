FROM python:3.5-alpine

LABEL maintainer="Tilwa Qendov"

WORKDIR /app
COPY *.py config.ini *.cdsapirc ./

CMD [ "sh" ]
