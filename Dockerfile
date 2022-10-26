ARG IMAGE_BASE_NAME

# hadolint ignore=DL3006
FROM ${IMAGE_BASE_NAME}

WORKDIR ${PYSETUP_PATH}/repo

COPY . ${PYSETUP_PATH}/repo

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN poetry install -E web && \
  python -m spacy download en_core_web_sm

# Set the PYTHONPATH
ENV PYTHONPATH='./profanity_filter'

ENTRYPOINT ["python -m"]
CMD ["profanity_filter.web"]