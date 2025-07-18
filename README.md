# UI Easy - AI-Powered Design Tool

A professional design software powered by large language models for analyzing design images, processing requirements, and generating high-fidelity prototypes.

## Features

- **Image Analysis**: Analyze design images using powerful AI models to generate comprehensive design documentation
- **Requirement Analysis**: Process user requirements and create structured documentation (Coming Soon)
- **Prototype Generation**: Generate high-fidelity prototypes from design docs and requirements (Coming Soon)
- **Modular Architecture**: Each function can be used independently
- **Multiple Model Support**: Supports OpenAI GPT-4 and DeepSeek models
- **Extensible Design**: Built for maintainability and future enhancements

## Installation

1. Clone or download the project
2. Install Python 3.8+ 
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

UI Easy now features a comprehensive configuration interface. You can configure the application in two ways:

### Method 1: Using the Settings Tab (Recommended)

1. Run the application: `python main.py`
2. Click on the "Settings" tab
3. Configure your AI models:
   - Add/edit model configurations
   - Enter your API keys
   - Set model parameters
4. Configure modules and app settings
5. Test your configuration
6. Save settings

### Method 2: Manual Configuration

1. Copy `config_template.json` to `config.json`
2. Edit the file to add your API keys:

```json
{
  "models": {
    "gpt4": {
      "name": "GPT-4",
      "provider": "openai",
      "api_key": "your-openai-api-key",
      "model_id": "gpt-4-turbo-preview"
    },
    "deepseek": {
      "name": "DeepSeek",
      "provider": "deepseek", 
      "api_key": "your-deepseek-api-key",
      "base_url": "https://api.deepseek.com/v1",
      "model_id": "deepseek-chat"
    }
  }
}
```

For detailed configuration instructions, see [CONFIG_GUIDE.md](CONFIG_GUIDE.md).

## Usage

Run the application:
```bash
python main.py
```

### Image Analysis

1. Go to the "Image Analyzer" tab
2. Click "Select Design Image" to choose an image file
3. Select the analysis type (Full Analysis, Layout Only, Colors Only, or Components Only)
4. Click "Analyze Design" to start the analysis
5. View results in the right panel
6. Export results as JSON or text file

## Architecture

The application follows a modular architecture:

- `src/core/`: Core functionality modules
  - `image_analyzer/`: Image analysis module
  - `requirement_analyzer/`: Requirements processing (Coming Soon)
  - `prototype_generator/`: Prototype generation (Coming Soon)
- `src/models/`: AI model integration layer
- `src/ui/`: Qt5 user interface components
- `src/utils/`: Utility functions

## Development

The system is designed for extensibility:

- Add new model providers by extending `BaseModel`
- Add new analysis modules by extending `BaseModule`
- Register new providers in `ModelFactory`
- UI components are modular and can be extended

## Future Enhancements

- Version control for designs
- UI style consistency across projects
- Additional model providers
- Advanced prototype generation
- Collaborative features

## Requirements

- Python 3.8+
- PyQt5
- PIL (Pillow)
- OpenAI API key (for GPT-4 analysis)
- DeepSeek API key (optional, for efficient analysis)