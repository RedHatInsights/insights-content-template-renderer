# Copyright 2023 Red Hat Inc.
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

"""Utility functions to redirect logs to cloudwatch."""

# Copied from
# https://github.com/RedHatInsights/insights-ccx-messaging/blob/main/ccx_messaging/utils/logging.py

import logging
import os

from boto3.session import Session
from watchtower import CloudWatchLogHandler


class InitializedCloudWatchLogger(logging.Handler):
    """Set the CloudWatch handler if the proper configuration is provided."""

    def __new__(self):
        """Try to create a CloudWatchLogHandler, otherwise create a no-op.

        Returns:
            logging.NullHandler: if the hanlder couldn't be configured.
                or
            watchtower.CloudWatchLogHandler: if it could be configured.
        """
        enabled = os.getenv("LOGGING_TO_CW_ENABLED", "False").lower()
        if enabled not in ("true", "1", "t", "yes"):
            # TODO: How to not initialize?
            print("Cloudwatch is not enabled")
            return logging.NullHandler()

        aws_config_vars = (
            "CW_AWS_ACCESS_KEY_ID",
            "CW_AWS_SECRET_ACCESS_KEY",
            "CW_AWS_REGION_NAME",
            "CW_LOG_GROUP",
            "CW_STREAM_NAME",
        )
        missing_envs = list(
            filter(
                lambda key: os.environ.get(key, "").strip() == "",
                list(aws_config_vars),
            )
        )

        if len(missing_envs) > 0:
            print(f"Missing envs: {missing_envs}, so not starting cloudwatch")
            return logging.NullHandler()

        session = Session(
            aws_access_key_id=os.environ["CW_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["CW_AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["CW_AWS_REGION_NAME"],
        )
        client = session.client("logs")

        print("Cloudwatch is configured")

        return CloudWatchLogHandler(
            boto3_client=client,
            log_group_name=os.environ["CW_LOG_GROUP"],
            log_stream_name=os.environ["CW_STREAM_NAME"],
            create_log_group=False,
        )
