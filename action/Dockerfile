FROM python:slim-bullseye
COPY ../refgraph ../requirements.txt entrypoint.sh /app
RUN pip install -r /app/requirements.txt
ENTRYPOINT ["/app/entrypoint.sh"]
