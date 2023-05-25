FROM registry.access.redhat.com/ubi8-minimal:8.8-860

ENV VENV=/insights-content-template-renderer-venv \
    HOME=/insights-content-template-renderer
#    REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt

RUN microdnf install python3.9
WORKDIR $HOME

COPY . $HOME

ENV PATH="$VENV/bin:$PATH" \
    CONFIG_PATH="$HOME/config.yml"

RUN microdnf install --nodocs -y python39-pip unzip
RUN python -m venv $VENV
#RUN curl -ksL https://password.corp.redhat.com/RH-IT-Root-CA.crt \
#    -o /etc/pki/ca-trust/source/anchors/RH-IT-Root-CA.crt && \
#    update-ca-trust
RUN pip install --verbose --no-cache-dir -U pip setuptools wheel
RUN pip install --verbose --no-cache-dir -r requirements.txt
RUN pip install .

RUN microdnf remove -y unzip python39-pip
RUN microdnf clean all
RUN chmod -R g=u $HOME $VENV /etc/passwd && \
    chgrp -R 0 $HOME $VENV

USER 1001

EXPOSE 8000

ENV PATH="$VENV/bin:$PATH" \
    CONFIG_PATH="$HOME/config.yml"

CMD ["sh", "-c", "insights-content-template-renderer --config $CONFIG_PATH"]
