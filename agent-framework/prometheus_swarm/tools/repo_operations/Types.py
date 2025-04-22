from enum import Enum
import json

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
    NONE = "none"
    OTHER = "other"
    @classmethod
    def to_string_list(cls):
        return [repo_type.value for repo_type in cls]

class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    R = "r"
    SHELL = "shell"
    NONE = "none"
    OTHER = "other"
    @classmethod
    def to_string_list(cls):
        return [lang.value for lang in cls]

class TestFramework(Enum):
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    JUNIT = "junit"
    TESTNG = "testng"
    GOTESTING = "go_testing"
    RSPEC = "rspec"
    PHPUNIT = "phpunit"
    XCTEST = "xctest"
    KOTEST = "kotest"
    NONE = "none"
    OTHER = "other"
    @classmethod
    def to_string_list(cls):
        return [test_framework.value for test_framework in cls]