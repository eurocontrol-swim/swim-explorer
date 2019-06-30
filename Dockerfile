FROM swim-base

LABEL maintainer="SWIM EUROCONTROL <http://www.eurocontrol.int>"

ENV PATH="/opt/conda/envs/app/bin:$PATH"

RUN mkdir -p /app
WORKDIR /app

COPY requirements.yml requirements.yml
RUN conda env create --name app -f requirements.yml

COPY ./swim_explorer/ ./swim_explorer/

COPY . /source/
RUN set -x \
    && pip install /source \
    && rm -rf /source

CMD ["python", "/app/swim_explorer/app.py"]
