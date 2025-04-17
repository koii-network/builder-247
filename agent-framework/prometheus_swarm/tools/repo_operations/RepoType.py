from enum import Enum

class RepoType(Enum):
    LIBRARY = "library"
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    MOBILE_APP = "mobile_app"
    TUTORIAL = "tutorial"
    TEMPLATE = "template"
    CLI_TOOL = "cli_tool"
    FRAMEWORK = "framework"
    DATA_SCIENCE = "data_science"
    OTHER = "other"