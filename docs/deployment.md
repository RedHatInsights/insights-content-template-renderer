# Deployment

## Testing the local version of the service in ephemeral

[![asciicast](https://asciinema.org/a/uMQESE4ay2ok7oQWr04slhuWw.svg)](https://asciinema.org/a/uMQESE4ay2ok7oQWr04slhuWw)

1. Install `bonfire`
```
pip install crc-bonfire
```

2. Log into https://console-openshift-console.apps.crc-eph.r9lp.p1.openshiftapps.com/k8s/cluster/projects

```
oc login --token=${TOKEN} --server=https://api.c-rh-c-eph.8p0c.p1.openshiftapps.com:6443
```

3. Reserve a namespace
```
NAMESPACE=$(bonfire namespace reserve)
```

4. Deploy the renderer
```
bonfire deploy -c deploy/test.yaml -n $NAMESPACE ccx-data-pipeline
```

5. Make a request to the renderer
```
oc --namespace $NAMESPACE run curl -i --rm \
    --image=docker.io/curlimages/curl:latest  \
    --command -- sh -c "
        echo '[INFO] Downloading jq' && \
        wget -O /tmp/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 2>/dev/null && \
        chmod +x /tmp/jq && \
        echo '[INFO] Downloading a request data example' && \
        curl -s https://raw.githubusercontent.com/RedHatInsights/insights-content-template-renderer/main/insights_content_template_renderer/tests/request_data_example.json > /tmp/req.json && \
        echo '[INFO] Testing the service' && \
        curl -s -X POST -H 'Content-Type: application/json' -d @/tmp/req.json insights-content-template-renderer-svc:8000/v1/rendered_reports | /tmp/jq && \
        echo '' && \
        echo '[INFO] Testing finished'
    "
```

You should see the generated report.

6. Delete the namespace
```
bonfire namespace release $NAMESPACE 
```
