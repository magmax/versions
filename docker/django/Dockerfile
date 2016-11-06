FROM python:3.4

RUN apt-get -y update \
    && apt-get install -y \
       postgresql-client supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/app \
    && useradd -M celery

WORKDIR /opt/app
COPY run.sh /run.sh
COPY config/supervisor.conf /etc/supervisor/conf.d/django.conf

EXPOSE 80
VOLUME /opt/app

CMD ["/run.sh"]
