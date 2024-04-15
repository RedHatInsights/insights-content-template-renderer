#!/bin/bash
# Copyright 2022 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -exv


# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
export APP_NAME="ccx-data-pipeline"  # name of app-sre "application" folder this component lives in
export COMPONENT_NAME="insights-content-template-renderer"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
export IMAGE="quay.io/cloudservices/insights-content-template-renderer"
export COMPONENTS="insights-content-template-renderer"  # space-separated list of components to laod
export COMPONENTS_W_RESOURCES="insights-content-template-renderer"  # component to keep
export CACHE_FROM_LATEST_IMAGE="true"

export IQE_PLUGINS="ccx"
export IQE_MARKER_EXPRESSION=""
# Workaround: There are no specific integration tests. Check that the service loads and iqe plugin works.
export IQE_FILTER_EXPRESSION="test_plugin_accessible"
export IQE_REQUIREMENTS_PRIORITY=""
export IQE_TEST_IMPORTANCE=""
export IQE_CJI_TIMEOUT="30m"

build_image() {
    # shellcheck disable=SC1091
    source "${CICD_ROOT}/build.sh"
}

deploy_ephemeral() {
    # shellcheck disable=SC1091
    source "${CICD_ROOT}/deploy_ephemeral_env.sh"
}

run_smoke_tests() {
    # component name needs to be re-export to match ClowdApp name (as bonfire requires for this)
    
    # TODO: Uncomment when there are any tests
    # export COMPONENT_NAME="insights-content-template-renderer"
    # source $CICD_ROOT/cji_smoke_test.sh
    echo 'To be implemented'
}

generate_dummy_junit_report() {

    local artifacts_dir='artifacts'

    if [[ -d "$artifacts_dir" ]]; then
        mkdir artifacts
    fi

    cat <<-EOF > "${artifacts_dir}/junit-stub.xml"
<?xml version="1.0" encoding="utf-8"?>
  <testsuite name"foo">
    <testcase classname="test" name="test_stub" time="0.000"/>
  </testsuite>
EOF
}

# Install bonfire repo/initialize
SCRIPT_URL='https://raw.githubusercontent.com/RedHatInsights/cicd-tools/master/bootstrap.sh'
curl -s "$SCRIPT_URL" > .cicd_bootstrap.sh && source .cicd_bootstrap.sh
echo "creating PR image"
build_image

echo "deploying to ephemeral"
deploy_ephemeral

echo "running PR smoke tests"
run_smoke_tests

# Temporary stub
generate_dummy_junit_report
