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
APP_NAME="ccx-data-pipeline"  # name of app-sre "application" folder this component lives in
COMPONENT_NAME="insights-content-template-renderer"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
IMAGE="quay.io/cloudservices/insights-content-template-renderer"
COMPONENTS="ccx-data-pipeline ccx-insights-results dvo-writer ccx-redis ccx-smart-proxy ccx-notification-writer ccx-notification-service ccx-notification-db-cleaner notifications-backend notifications-aggregator notifications-engine insights-content-service ccx-mock-ams ccx-upgrades-sso-mock insights-content-template-renderer"  # space-separated list of components to load
COMPONENTS_W_RESOURCES="insights-content-template-renderer"  # component to keep
CACHE_FROM_LATEST_IMAGE="true"
DEPLOY_FRONTENDS="false"
# Set the correct images for pull requests.
# pr_check in pull requests still uses the old cloudservices images
EXTRA_DEPLOY_ARGS="--set-parameter insights-content-template-renderer/IMAGE=quay.io/cloudservices/insights-content-template-renderer"
EXTRA_DEPLOY_ARGS="${EXTRA_DEPLOY_ARGS} --no-remove-resources notifications-engine"

export IQE_PLUGINS="ccx"
export IQE_MARKER_EXPRESSION="servicelog"
export IQE_FILTER_EXPRESSION=""
export IQE_REQUIREMENTS_PRIORITY=""
export IQE_TEST_IMPORTANCE=""
export IQE_CJI_TIMEOUT="30m"
export IQE_SELENIUM="false"
export IQE_ENV="ephemeral"
export IQE_ENV_VARS="DYNACONF_USER_PROVIDER__rbac_enabled=false"


export IQE_CJI_TIMEOUT="30m"


function build_image() {
    source $CICD_ROOT/build.sh
}

function deploy_ephemeral() {
    source $CICD_ROOT/deploy_ephemeral_env.sh
}

function run_smoke_tests() {
    # component name needs to be re-export to match ClowdApp name (as bonfire requires for this)
    export COMPONENT_NAME="insights-content-template-renderer"    
    source $CICD_ROOT/cji_smoke_test.sh
    source $CICD_ROOT/post_test_results.sh  # publish results in Ibutsu#
}


# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh
echo "creating PR image"
build_image

echo "deploying to ephemeral"
deploy_ephemeral

echo "running PR smoke tests"
run_smoke_tests

# Temporary stub
mkdir -p artifacts
echo '<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" errors="0" failures="0" skipped="0" tests="1" time="0.014" timestamp="2021-05-13T07:54:11.934144" hostname="thinkpad-t480s"><testcase classname="test" name="test_stub" time="0.000" /></testsuite></testsuites>' > artifacts/junit-stub.xml
