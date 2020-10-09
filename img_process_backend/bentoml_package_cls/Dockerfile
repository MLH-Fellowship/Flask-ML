FROM bentoml/model-server:0.9.1-py37

# Configure PIP install arguments, e.g. --index-url, --trusted-url, --extra-index-url
ARG EXTRA_PIP_INSTALL_ARGS=
ENV EXTRA_PIP_INSTALL_ARGS $EXTRA_PIP_INSTALL_ARGS

# copy over files needed for init script
COPY environment.yml requirements.txt setup.sh* bentoml-init.sh python_version* /bento/
WORKDIR /bento

# Execute permission for bentoml-init.sh
RUN chmod +x /bento/bentoml-init.sh

# Install conda, pip dependencies and run user defined setup script
RUN if [ -f /bento/bentoml-init.sh ]; then bash -c /bento/bentoml-init.sh; fi

# copy over model files
COPY . /bento

# Install bundled bentoml if it exists (used for development)
RUN if [ -d /bento/bundled_pip_dependencies ]; then pip install -U bundled_pip_dependencies/* ;fi

# the env var $PORT is required by heroku container runtime
ENV PORT 5000
EXPOSE $PORT

COPY docker-entrypoint.sh /usr/local/bin/

# Execute permission for docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD ["bentoml", "serve-gunicorn", "/bento"]
