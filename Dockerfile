FROM registry.access.redhat.com/ubi9/python-39:1-117

WORKDIR /insights-content-template-renderer

COPY . /insights-content-template-renderer

USER 0

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install .

USER 1001

EXPOSE 8000

CMD ["insights-content-template-renderer", "--config", "config.yml"]
