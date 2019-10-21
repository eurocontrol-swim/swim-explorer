FROM swim-base

LABEL maintainer="SWIM EUROCONTROL <http://www.eurocontrol.int>"

ENV PATH="/opt/conda/bin:$PATH"

RUN mkdir -p /app
WORKDIR /app

COPY requirements_pip.txt requirements_pip.txt
RUN pip3 install -r requirements_pip.txt

COPY ./swim_explorer/ ./swim_explorer

COPY . /source/
RUN set -x \
    && pip3 install /source \
    && rm -rf /source

RUN groupadd -r swim && useradd --no-log-init -md /home/swim -r -g swim swim

RUN chown -R swim:swim /app

USER swim

CMD ["python", "/app/swim_explorer/app.py"]
