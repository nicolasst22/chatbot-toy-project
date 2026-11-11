FROM python:3.13-slim

WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r ./requirements.txt
COPY ./mcp_server.py    ./mcp_server.py

EXPOSE 8001
CMD python ./mcp_server.py

