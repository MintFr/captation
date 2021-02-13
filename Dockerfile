FROM python:3.5-stretch

LABEL maintainer="Tilwa Qendov"

WORKDIR /app

# Install python-grib
RUN apt-get update \
  && apt-get install -y python3-grib \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY *.py model.sh config.ini *.cdsapirc ./

# Install dependencies in ./venv
RUN python3 -m venv venv \
  && . venv/bin/activate \
  && ./install_requirements.py

CMD [ "sh" ]
