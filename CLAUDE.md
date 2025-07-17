# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python main.py
```

### Testing
```bash
python test_app.py
```
This runs basic system tests including module imports, configuration system, and image analyzer initialization.

### Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

This is a PyQt5-based AI-powered design analysis tool with a modular architecture:

### Core Components

- **Entry Point**: `main.py` - Sets up PyQt5 application with high DPI support
- **Configuration System**: `src/core/config.py` - Centralized configuration management using dataclasses
  - `ModelConfig` - AI model configurations (API keys, endpoints, parameters)
  - `ModuleConfig` - Module-specific settings and custom prompts
  - `Config` - Main configuration manager with JSON persistence
- **Base Module**: `src/core/base_module.py` - Abstract base class for all core modules
  - Provides PyQt5 signals for progress tracking and status updates
  - Standardized processing pipeline with error handling

### Model System

- **Model Factory**: `src/models/model_factory.py` - Factory pattern for creating AI model instances
  - Provider registry system for extensibility
  - Model caching and configuration management
- **Base Model**: `src/models/base_model.py` - Abstract interface for AI models
- **Providers**: Currently supports OpenAI and DeepSeek models

### Core Modules

- **Image Analyzer**: `src/core/image_analyzer/analyzer.py` - Main analysis module
  - Processes design images using AI models
  - Supports multiple analysis types (full, layout, colors, components)
  - Handles image preprocessing (resize, format conversion, base64 encoding)
  - Structured result parsing and confidence scoring

### UI Layer

- **Main Window**: `src/ui/main_window.py` - PyQt5 main interface
- UI components are modular and extend PyQt5 widgets

## Key Design Patterns

1. **Factory Pattern**: Used for model creation and provider registration
2. **Observer Pattern**: PyQt5 signals for module communication
3. **Template Method**: BaseModule defines processing pipeline
4. **Strategy Pattern**: Different analysis types and model providers

## Configuration

The application uses a JSON-based configuration system (`config.json`) with defaults defined in `src/core/config.py`. API keys are configured per model provider.

## Extension Points

- **New Model Providers**: Extend `BaseModel` and register with `ModelFactory`
- **New Analysis Modules**: Extend `BaseModule` and follow the established patterns
- **New Analysis Types**: Add to `ImageAnalyzer._get_analysis_prompt()`

## Dependencies

- PyQt5 for GUI framework
- Pillow for image processing
- OpenAI API client
- Requests for HTTP communication