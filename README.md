#Gitflow tool

## Possible flows

### Release

To **start** release - `gitflow release start`
> Tag autoincrement is enabled by default. If you want to set it manually - you can do it via setting the `GITFLOW_TARGET_TAG` env variable

To **finish** release - `gitflow release finish`


### Hotfix

To **start** hotfix - `gitflow hotfix start`
> Tag autoincrement is enabled by default. If you want to set it manually - you can do it via setting the `GITFLOW_TARGET_TAG` env variable

To **finish** hotfix - `gitflow hotfix finish`


### Support

To **start** support - `gitflow support start`
> You should set `GITFLOW_SOURCE_TAG` env variable

To **finish** support - `gitflow support finish`

To **tag** support - `gitflow support tag`

## Envs
|             Name              | Description                                             |                           Default                           |
|:-----------------------------:|:--------------------------------------------------------|:-----------------------------------------------------------:|
|      CI_SERVER_PROTOCOL       | Predefined Gitlab Ci variable                           |                              -                              |
|        CI_SERVER_HOST         | Predefined Gitlab Ci variable                           |                              -                              |
|        CI_PROJECT_PATH        | Predefined Gitlab Ci variable                           |                              -                              |
|        GITFLOW_BOT_ID         | Gitlab CI/CD variable, should be set manually           |                              -                              |
|       GITFLOW_BOT_TOKEN       | Gitlab CI/CD variable, should be set manually           |                              -                              |
|      GITFLOW_MASTER_NAME      | 'master' branch name for your project                   |                          `master`                           |
|       GITFLOW_DEV_NAME        | 'dev' branch name for your project                      |                            `dev`                            |
|       GITFLOW_TIMEWAIT        | Timewait interval between Gitlab API requests in [secs] |                             `5`                             |
|        GITFLOW_TIMEOUT        | Timeout for Gitlab API requests in [secs]               |                            `30`                             |
|     GITFLOW_GET_ALL_TAGS      | Fetch all project tags                                  |                           `true`                            |
|    GITFLOW_ARTIFACTS_PATH     | Relative path for artifacts file                        |                     `./artifacts.json`                      |
|       GITFLOW_LOG_LEVEL       | Log level                                               |                           `INFO`                            |
|    GITFLOW_RELEASE_PREFIX     | Release prefix                                          |                         `release/`                          |
| GITFLOW_RELEASE_SCHEDULE_NAME | Release pipeline schedule name                          |                          `RELEASE`                          |
|     GITFLOW_HOTFIX_PREFIX     | Hotfix prefix                                           |                          `hotfix/`                          |
| GITFLOW_HOTFIX_SCHEDULE_NAME  | Hotfix pipeline schedule name                           |                          `HOTFIX`                           |
|    GITFLOW_SUPPORT_PREFIX     | Support prefix                                          |                         `support/`                          |
| GITFLOW_SUPPORT_SCHEDULE_NAME | Support pipeline schedule name                          |                          `SUPPORT`                          |
|      GITFLOW_SOURCE_TAG       | Source tag should be presented for `support` branch     |                            `""`                             |
|      GITFLOW_TARGET_TAG       | Target tag for manual versioning                        |                            `""`                             |
|      GITFLOW_TAG_REGEXP       | Regexp for tag parsing (prefix, version, postfix)       | `(?P<prefix>.*)(?P\<version>\d+\.\d+\.\d+)(?P\<postfix>.*)` |
|   GITFLOW_TAG_SEMVER_REGEXP   | Regexp for tag version parsing                          |      `(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)`       |
| GITFLOW_TAG_MESSAGE_TEMPLATE  | Tag message template with `.format`-style rendering     |                           `{tag}`                           |
|       GITFLOW_MR_LABELS       | Labels for created due gitflow mrs                      |                          `gitflow`                          |
|   GITFLOW_MR_TITLE_TEMPLATE   | Mr title template with `.format`-style rendering        |                `Merge {source} to {target}`                 |
|    GITFLOW_MR_MSG_TEMPLATE    | Mr message template with `.format`-style rendering      |            `Merge branch {source} into {target}`            |
|     GITFLOW_MR_RM_SOURCE      | Delete source branch after merged mr or not             |                           `false`                           |
|      GITFLOW_MR_SKIP_CI       | Skip CI pipeline for created mrs or not                 |                           `true`                            |
|       GITFLOW_MR_SQUASH       | Squash commits for created mrs or not                   |                           `false`                           |
|    GITFLOW_MR_ASSIGNEE_ID     | Ids of the users to assign the created mrs              |                      `GITFLOW_BOT_ID`                       |
|    GITFLOW_MR_REVIEWER_IDS    | Ids of the users to review the created mrs              |                             ``                              |