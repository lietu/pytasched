# ----- BUILD ENVIRONMENT ----- #

FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    USER="pytasched" \
    GROUP="pytasched" \
    UID=1000 \
    GID=1000 \
    WORKON_HOME="/.venv"

# Initial setup for build environment
WORKDIR /src
ADD docker-build-setup.sh ./
RUN sh docker-build-setup.sh

# Add minimal things for installing dependencies
USER ${USER}

# GOTCHA: These will be owned by root --chown= does not take env variables
ADD pyproject.toml poetry.lock docker-build-deps.sh ./
RUN sh docker-build-deps.sh


# ----- RUNTIME ENVIRONMENT ----- #

FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    USER="pytasched" \
    GROUP="pytasched" \
    UID=1000 \
    GID=1000 \
    WORKON_HOME="/.venv"

# Copy results from build environment
COPY --from=0 /home/${USER}/.poetry /home/${USER}/.poetry/
COPY --from=0 ${WORKON_HOME} ${WORKON_HOME}

# Set up this container
WORKDIR /src
ADD settings_docker.py pyproject.toml poetry.lock docker-runtime-setup.sh ./
RUN sh docker-runtime-setup.sh

# Add the whole source
ADD . ./

# Configure runtime
USER ${USER}
EXPOSE 8000
ENTRYPOINT ["sh", "docker-runtime-entrypoint.sh"]
