# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Run all tests: `python -m pytest tests/`
- Run single test: `python -m pytest tests/test_file.py::test_function`
- Install dependencies: `pip install -e .` or `uv install -e .`

## Code Style Guidelines
- **Imports**: Group standard library, third-party, and local imports in separate blocks
- **Formatting**: Use snake_case for variables/functions, PascalCase for classes
- **Type hints**: Include type annotations for function parameters and return values
- **Error handling**: Use specific exception types with descriptive error messages
- **Documentation**: Add docstrings to all functions and classes
- **Tools structure**: New tools should be added to appropriate module in `milo_agent/tools/`
- **Testing**: All new functionality should have corresponding tests in `tests/`

## Development Workflow
- The project uses PyAutogen and OpenAI for AI agent capabilities
- Core agent logic is in `milo_agent/agent.py`
- Tool implementations are organized by domain in `milo_agent/tools/`