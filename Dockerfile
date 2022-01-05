FROM python:slim-bullseye

COPY requirements.txt /app/
RUN apt-get update                          && \
    apt-get install --yes graphviz          && \
    pip install -r /app/requirements.txt

COPY entrypoint.sh /app/
COPY refgraph/ /app/refgraph/

ENTRYPOINT ["/app/entrypoint.sh"]
