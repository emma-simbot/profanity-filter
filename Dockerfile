ARG BUILDER_IMAGE_NAME
ARG BASE_IMAGE_NAME

# ---------------------------------- Builder --------------------------------- #
# hadolint ignore=DL3006
FROM ${BUILDER_IMAGE_NAME} as builder

WORKDIR ${PYSETUP_PATH}/repo

COPY . ${PYSETUP_PATH}/repo

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN poetry install --only main,web && \
  python -m spacy download en_core_web_sm

# ---------------------------------- Runner ---------------------------------- #
# hadolint ignore=DL3006
FROM ${BASE_IMAGE_NAME} as runner

COPY --from=builder ${PYSETUP_PATH} ${PYSETUP_PATH}

WORKDIR ${PYSETUP_PATH}/repo

# Set the PYTHONPATH
ENV PYTHONPATH='./profanity_filter'

ENTRYPOINT ["python -m"]
CMD ["profanity_filter.web"]