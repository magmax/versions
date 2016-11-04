FROM python:3.4

RUN apt-get -y update \
    && apt-get install -y \
       postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/app

WORKDIR /opt/app
COPY run.sh /run.sh


EXPOSE 80
VOLUME /opt/app

CMD ["/run.sh"]
