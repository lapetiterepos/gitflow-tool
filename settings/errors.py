from settings.logger import get_logger
import traceback
import typing
import sys

log = get_logger(__name__)


def error_handler(func: typing.Callable) -> typing.Callable:
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except CmdException as e:
            log.debug(traceback.format_exc())
            log.error(f"Command exception: {e}")
            sys.exit(1)
        except KeyError as e:
            log.debug(traceback.format_exc())
            log.error(f"Missing environment variable exception: {e}")
            sys.exit(1)
        except GitflowError as e:
            log.debug(traceback.format_exc())
            log.error(f"Gitflow exception: {e}")
            sys.exit(1)
        except GitlabProjectError as e:
            log.debug(traceback.format_exc())
            log.error(f"Gitlab project exception: {e}")
            sys.exit(1)
        except GitlabBranchError as e:
            log.debug(traceback.format_exc())
            log.error(f"Gitlab branch exception: {e}")
            sys.exit(1)
        except GitlabMrError as e:
            log.debug(traceback.format_exc())
            log.error(f"Gitlab merge request exception: {e}")
            sys.exit(1)
        except GitlabPipelineError as e:
            log.debug(traceback.format_exc())
            log.error(f"Gitlab pipeline exception: {e}")
            sys.exit(1)
        except GitlabTagError as e:
            log.debug(traceback.format_exc())
            log.error(f"Gitlab tag exception: {e}")
            sys.exit(1)

        except Exception as e:
            log.debug(traceback.format_exc())
            log.error(f"Undefined exception: {e}")
            sys.exit(1)

    return wrapper


class CmdException(Exception):
    """Exception raised for errors in the cli commands"""

    pass


class CliError(Exception):
    """Exception raised for errors in the cli commands"""

    pass


class HelpersArtifactsError(Exception):
    """Exception raised for errors in the artifacts helper"""

    pass


class HelpersCommonError(Exception):
    """Exception raised for errors in the common helper"""

    pass


class SettingsConfigError(Exception):
    """Exception raised for errors in the config"""

    pass


class SettingsLoggerError(Exception):
    """Exception raised for errors in the log"""

    pass


class GitflowError(Exception):
    """Exception raised for the gitflow errors"""

    pass


class GitlabProjectError(Exception):
    """Exception raised for the gitflow errors"""

    pass


class GitlabBranchError(Exception):
    """Exception raised for the gitflow errors"""

    pass


class GitlabMilestoneError(Exception):
    """Exception raised for the gitflow errors"""

    pass


class GitlabMrError(Exception):
    """Exception raised for the merge request errors"""

    pass


class GitlabPipelineError(Exception):
    """Exception raised for the pipeline errors"""

    pass


class GitlabTagError(Exception):
    """Exception raised for errors in the tags"""

    pass
