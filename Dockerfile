FROM python:3.8.12-bullseye
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR off

# Install gcp
RUN apt-get update
RUN apt-get -y install curl jq
RUN pip install --upgrade pip==20.2.4
RUN mkdir -p /gcp
ENV GOOGLE_CLOUD_SDK_VERSION 365.0.1
RUN cd /gcp && \
  curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${GOOGLE_CLOUD_SDK_VERSION}-linux-x86_64.tar.gz \
    -o google-cloud-sdk.tar.gz && \
  tar xf google-cloud-sdk.tar.gz && \
  rm google-cloud-sdk.tar.gz
RUN /gcp/google-cloud-sdk/install.sh -q
ENV PATH="/gcp/google-cloud-sdk/bin/:${PATH}"
RUN gcloud components install kubectl

ENV PYTHONPATH /app
WORKDIR /app

# Install library requirements
ENV PIP_INSTALL_PIPENV_VERSION=2021.5.29
RUN pip install pipenv==${PIP_INSTALL_PIPENV_VERSION}
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
#COPY Pipfile .
#COPY Pipfile.lock .
ARG PIPENV_DEV=0
ENV PIPENV_DEV ${PIPENV_DEV}
#RUN pipenv install --system --deploy
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV AIRFLOW_HOME=/app/composer
ENV COMPOSER_LOCAL_STORAGE=/app/composer
ENV AIRFLOW_ENVIRONMENT=test
ENV AIRFLOW__CORE__LOAD_EXAMPLES=false

ENV PYTHONPATH="${PYTHONPATH}:${AIRFLOW_HOME}"

RUN pip freeze
RUN pipenv lock
RUN cat Pipfile
RUN cat Pipfile.lock

COPY . .
