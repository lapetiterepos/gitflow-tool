from __future__ import annotations
from app.helpers.common import DotDict
from dotenv import load_dotenv
import os


class Config:
    env_names = DotDict(
        {
            "gitlab": DotDict(
                {
                    "proto": "CI_SERVER_PROTOCOL",
                    "host": "CI_SERVER_HOST",
                    "project": "CI_PROJECT_PATH",
                    "bot_id": "GITFLOW_BOT_ID",
                    "bot_token": "GITFLOW_BOT_TOKEN",
                    "master_name": "GITFLOW_MASTER_NAME",
                    "dev_name": "GITFLOW_DEV_NAME",
                    "timewait": "GITFLOW_TIMEWAIT",
                    "timeout": "GITFLOW_TIMEOUT",
                    "get_all_tags": "GITFLOW_GET_ALL_TAGS",
                }
            ),
            "artifacts": DotDict(
                {
                    "path": "GITFLOW_ARTIFACTS_PATH",
                }
            ),
            "logger": DotDict(
                {
                    "level": "GITFLOW_LOG_LEVEL",
                }
            ),
            "release": DotDict(
                {
                    "prefix": "GITFLOW_RELEASE_PREFIX",
                    "ref": "GITFLOW_DEV_NAME",
                    "schedule": "GITFLOW_RELEASE_SCHEDULE_NAME",
                }
            ),
            "hotfix": DotDict(
                {
                    "prefix": "GITFLOW_HOTFIX_PREFIX",
                    "ref": "GITFLOW_MASTER_NAME",
                    "schedule": "GITFLOW_HOTFIX_SCHEDULE_NAME",
                }
            ),
            "support": DotDict(
                {
                    "prefix": "GITFLOW_SUPPORT_PREFIX",
                    "schedule": "GITFLOW_SUPPORT_SCHEDULE_NAME",
                }
            ),
            "tag": DotDict(
                {
                    "source": "GITFLOW_SOURCE_TAG",
                    "target": "GITFLOW_TARGET_TAG",
                    "regexp": "GITFLOW_TAG_REGEXP",
                    "semver_regexp": "GITFLOW_TAG_SEMVER_REGEXP",
                    "message_template": "GITFLOW_TAG_MESSAGE_TEMPLATE",
                }
            ),
            "mr": DotDict(
                {
                    "labels": "GITFLOW_MR_LABELS",
                    "title_template": "GITFLOW_MR_TITLE_TEMPLATE",
                    "msg_template": "GITFLOW_MR_MSG_TEMPLATE",
                    "rm_source": "GITFLOW_MR_RM_SOURCE",
                    "skip_ci": "GITFLOW_MR_SKIP_CI",
                    "squash": "GITFLOW_MR_SQUASH",
                    "assignee": "GITFLOW_MR_ASSIGNEE_ID",
                    "reviewers": "GITFLOW_MR_REVIEWER_IDS",
                }
            ),
        }
    )

    optional = [
        env_names.tag.source,
        env_names.tag.target,
    ]

    def __init__(self):
        load_dotenv()
        self.gitlab = self.load_envs("gitlab")
        get_all = False
        if self.gitlab.get_all_tags == "true":
            get_all = True
        self.gitlab.get_all_tags = get_all
        self.gitlab.timewait = int(self.gitlab.timewait)
        self.gitlab.timeout = int(self.gitlab.timeout)
        self.artifacts = self.load_envs("artifacts")
        self.logger = self.load_envs("logger")
        self.release = self.load_envs("release")
        self.hotfix = self.load_envs("hotfix")
        self.support = self.load_envs("support")
        self.tag = self.load_envs("tag")
        self.mr = self.load_envs("mr")
        self.mr.reviewers = self.mr.reviewers.split(",")
        self.mr.labels = self.mr.labels.split(",")

    @classmethod
    def load_envs(cls, envs_name: str) -> DotDict:
        result = DotDict()
        for key, value in cls.env_names[envs_name].items():
            result[key] = cls.load_env(env_name=value)
        return result

    @classmethod
    def load_env(cls, env_name: str) -> str:
        if env_name in cls.optional:
            return os.getenv(env_name, None)
        return os.environ[env_name]


init = Config()
logger = init.logger
gitlab = init.gitlab
artifacts = init.artifacts
release = init.release
hotfix = init.hotfix
support = init.support
tag = init.tag
mr = init.mr
