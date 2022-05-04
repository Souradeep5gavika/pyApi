#!/bin/bash
PCP_UWSGI_PORT=${PCP_UWSGI_PORT:-6661}

cd /pcp-app

/pcp-env/bin/uwsgi \
  --http-socket 0.0.0.0:"${PCP_UWSGI_PORT}" \
  --wsgi-file pcp \
  --buffer-size 65535 \
  --enable-threads \
  --single-interpreter \
  --threads 2 \
  -L \
  --stats /run/pcp-app/uwsgi_stats.socket \
  --lazy-apps \
  --master-fifo /run/pcp-app/uwsgimasterfifo \
  --processes 2 \
  --harakiri 960 \
  --max-worker-lifetime=21600 \
  --ignore-sigpipe \
  --ignore-write-errors \
  --disable-write-exception \
  --mount /=run:app \
  --manage-script-name