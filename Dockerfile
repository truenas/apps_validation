FROM ghcr.io/truenas/middleware:master

RUN /usr/bin/install-dev-tools

ENV PYTHONUNBUFFERED=1
ENV WORK_DIR=/app
RUN mkdir -p ${WORK_DIR}
WORKDIR ${WORK_DIR}

ADD . ${WORK_DIR}/
RUN pip install --break-system-packages .
