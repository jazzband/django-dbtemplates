ARG BASE_IMAGE=python
ARG TAG=3.10.4
FROM ${BASE_IMAGE}:${TAG} as server

ENV APP_BASE=/usr/src/app \
    LIB_BASE=/usr/src/lib \
    POETRY_VERSION=1.0.10 \
    NAME=django-dbtemplates \
    PATH="/root/.poetry/bin:$PATH"

WORKDIR ${LIB_BASE}/${NAME}
COPY . ${LIB_BASE}/${NAME}
RUN pip install -e .

CMD ["sleep", "infinity"]