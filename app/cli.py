from settings import errors
from app.gitflow import Gitflow
from settings.logger import get_logger

log = get_logger(__name__)


class Cli:
    """
    Gitflow tool\n
    Possible flows: 'release', 'hotfix', 'support'.
    Possible commands: 'start', 'finish'.
    """

    @staticmethod
    @errors.error_handler
    def release(command: str) -> None:
        _gitflow = Gitflow()
        match command:
            case "start":
                _gitflow.start_release()
            case "finish":
                _gitflow.finish_release()
            case _:
                raise errors.CmdException(f"Unknown command: {command}")

    @staticmethod
    @errors.error_handler
    def hotfix(command: str):
        _gitflow = Gitflow()
        match command:
            case "start":
                _gitflow.start_hotfix()
            case "finish":
                _gitflow.finish_hotfix()
            case _:
                raise errors.CmdException(f"Unknown command: {command}")

    @staticmethod
    @errors.error_handler
    def support(command: str):
        _gitflow = Gitflow()
        match command:
            case "start":
                _gitflow.start_support()
            case "finish":
                _gitflow.finish_support()
            case _:
                raise errors.CmdException(f"Unknown command: {command}")
