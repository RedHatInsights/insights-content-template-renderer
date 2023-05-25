FROM registry.access.redhat.com/ubi8-minimal:8.8-860

ENV VENV=/insights-content-template-renderer-venv \
    HOME=/insights-content-template-renderer

RUN microdnf install --nodocs --noplugins -y python3.11

WORKDIR $HOME

COPY . $HOME

ENV PATH="$VENV/bin:$PATH" \
    CONFIG_PATH="$HOME/config.yml"

RUN python -m venv $VENV
RUN pip install --verbose --no-cache-dir -U pip setuptools wheel
RUN pip install --verbose --no-cache-dir -r requirements.txt
RUN pip install .

# Clean up not necessary packages if useful
RUN pip uninstall -y py #https://pypi.org/project/py/

RUN microdnf clean all

USER 1001

EXPOSE 8000

ENV PATH="$VENV/bin:$PATH" \
    CONFIG_PATH="$HOME/config.yml"

CMD ["sh", "-c", "insights-content-template-renderer --config $CONFIG_PATH"]
