FROM ghcr.io/truenas/middleware:master

RUN /usr/bin/install-dev-tools

ENV PYTHONUNBUFFERED=1
ENV WORK_DIR=/app
RUN mkdir -p ${WORK_DIR}
WORKDIR ${WORK_DIR}

# Copy only dependency files first for better layer caching
COPY pyproject.toml ${WORK_DIR}/
RUN pip install --break-system-packages --no-cache-dir --ignore-installed .

# Copy the rest of the application code
COPY . ${WORK_DIR}/

# Reinstall in case any package metadata changed
RUN pip install --break-system-packages --no-cache-dir --no-deps --ignore-installed .
