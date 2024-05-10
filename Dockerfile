FROM ghcr.io/truenas/middleware:master

RUN /usr/bin/install-dev-tools

RUN apt-get install -y \
      debhelper-compat \
      dh-python \
      python3-dev \
      python3-setuptools \
      devscripts \
      python3-jsonschema \
      python3-semantic-version \
      python3-yaml

ENV PYTHONUNBUFFERED 1
ENV WORK_DIR /app
RUN mkdir -p ${WORK_DIR}
WORKDIR ${WORK_DIR}

ADD . ${WORK_DIR}/
RUN pip install --break-system-packages -r requirements.txt
RUN pip install --break-system-packages -U .

RUN echo "python3 /app/catalog_templating/scripts/render_compose.py "$@"" > /usr/bin/catalog_templating && \
      chmod +x /usr/bin/catalog_templating
RUN echo "python3 /app/apps_validation/scripts/catalog_validate.py "$@"" > /usr/bin/catalog_validate && \
      chmod +x /usr/bin/catalog_validate
RUN echo "python3 /app/apps_validation/scripts/catalog_update.py "$@"" > /usr/bin/catalog_update && \
      chmod +x /usr/bin/catalog_update
RUN echo "python3 /app/apps_validation/scripts/dev_apps_validate.py "$@"" > /usr/bin/dev_apps_validate && \
      chmod +x /usr/bin/dev_apps_validate
