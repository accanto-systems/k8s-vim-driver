FROM python:3.7-alpine

ARG DRIVER_PORT
ENV DRIVER_PORT ${DRIVER_PORT:-8294}
ARG NUM_PROCESSES
ENV NUM_PROCESSES ${NUM_PROCESSES:-4}
ARG NUM_THREADS
ENV NUM_THREADS ${NUM_THREADS:-2}
ARG WSGI_CONTAINER
ENV WSGI_CONTAINER ${WSGI_CONTAINER:-uwsgi}

COPY whls/*.whl /whls/

RUN addgroup -S k8svd \
 && adduser -S k8svd -G k8svd \
 && mkdir -p /var/k8svd \
 && chown -R k8svd:k8svd /var/k8svd \
 && apk add --no-cache bash \
 # These packages need to be installed so that we can install the Python dependencies.
 # We make this virtual so that we can remove them later
 && apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev python3-dev make git \
 && for i in /whls/*.whl; do pip install "$i"; done \
 && apk del .build-deps gcc musl-dev libffi-dev openssl-dev python3-dev make git

USER k8svd
WORKDIR /home/k8svd

EXPOSE 8294

CMD ["k8svd"]