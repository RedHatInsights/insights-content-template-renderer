FROM registry.access.redhat.com/ubi9-minimal:latest

ENV VENV=/insights-content-template-renderer-venv \
    HOME=/insights-content-template-renderer

WORKDIR $HOME

COPY . $HOME

ENV PATH="$VENV/bin:$PATH"

RUN microdnf install --nodocs --noplugins -y python3.11 git-core npm && \
    python3.11 -m venv $VENV && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir .

# Clean up not necessary packages if useful
RUN pip uninstall -y py pip

RUN microdnf remove -y git-core && \
    microdnf clean all && \
    rpm -e --nodeps sqlite-libs krb5-libs libxml2 readline

USER 1001

EXPOSE 8000

CMD ["uvicorn", "insights_content_template_renderer.endpoints:app", "--host=0.0.0.0", "--port=8000", "--log-config", "logging.yml"]
