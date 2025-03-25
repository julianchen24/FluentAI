# FluentAI

An offline, on-premise AI Machine Translation service supporting 50+ languages with dynamic model loading.

## Overview

FluentAI is a fully offline AI Machine Translation service that supports over 50 languages in an any-to-any manner. It leverages the Marian-NMT runtime for translation using pre-trained Opus-MT models, allowing for high-quality translations without any internet connection. Since loading all models at once isn't practical, it uses a Dynamic Model Loading Mechanism (DMLM) with an LRU cache (default capacity: 6 models) that swaps out the least-recently-used model as needed. For translation requests lacking a direct model (e.g., French to Spanish), the service automatically pivots through English. The service is powered by FastAPI and handles asynchronous translation requests with a 2-minute timeout.

## Key Features

- **Dynamic Model Loading & LRU Cache**:
  - Configurable via a JSON config file
  - Loads models dynamically using a semaphore (limit of 5 concurrent loads)
  - Models are stored with the naming convention `{source}-{target}`
  - Automatically manages model memory usage by unloading least recently used models

- **API Endpoints**:
  - `/translate`: Translates text from source language to target language
  - `/clear`: Clears the current model cache
  - `/load`: Loads a specific model manually
  - `/unload`: Unloads a specific model manually
  - `/status`: Shows currently loaded models ordered from most to least recently used

- **Intelligent Pivoting**:
  - Automatically pivots through English for language pairs without direct models
  - Seamless handling of complex translation requests

- **Error Handling**:
  - Standardized API error responses in JSON format
  - Detailed logs for debugging and monitoring

## Installation

### Prerequisites

- Python 3.8+
- Marian-NMT runtime (for Windows users, WSL is recommended)
- Pre-trained Opus-MT models for your language pairs

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/FluentAI.git
cd FluentAI
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Download Marian-NMT runtime and Opus-MT models:

For Windows users with WSL:
```bash
# These commands should be run in your WSL terminal
sudo apt-get update
sudo apt-get install build-essential cmake libboost-all-dev libprotobuf-dev protobuf-compiler libssl-dev
sudo apt-get install intel-mkl-full

git clone https://github.com/marian-nmt/marian-dev.git
cd marian-dev
mkdir build && cd build
cmake .. -DUSE_SENTENCEPIECE=ON -DUSE_MKL=ON -DCOMPILE_CUDA=OFF -DMKL_ROOT=/opt/intel/mkl -DCMAKE_BUILD_TYPE=Release
make -j4
```

5. Download Opus-MT models and place them in the correct directory:

```bash
# Download models from Helsinki-NLP Opus-MT Models repository
mkdir -p app/models

# Example for English-Russian model:
mkdir -p app/models/en-ru
# Download the model files and place them in this directory
```

Your model directories should follow this structure:
```
app/models/
├── ar-en/
│   ├── decoder.yml
│   ├── opus.bpe32k-bpe32k.transformer.model1.npz.best-perplexity.npz
│   └── opus.bpe32k-bpe32k.vocab.yml
├── en-es/
│   ├── decoder.yml
│   ├── opus.bpe32k-bpe32k.transformer.model1.npz.best-perplexity.npz
│   └── opus.bpe32k-bpe32k.vocab.yml
├── en-fr/
│   ├── decoder.yml
│   ├── opus.bpe32k-bpe32k.transformer.model1.npz.best-perplexity.npz
│   └── opus.bpe32k-bpe32k.vocab.yml
└── ... (other language pairs)
```

Each model directory must contain:
- A model file (*.npz) - the actual translation model
- A vocabulary file (*.yml) - containing tokenization vocabulary
- A decoder configuration file (decoder.yml) - containing model parameters

You can download pre-trained models from: [Helsinki-NLP Opus-MT Models](https://github.com/Helsinki-NLP/Opus-MT-train/tree/master/models)

## Configuration

Edit the `config.json` file to customize your deployment:

```json
{
  "app_name": "FluentAI",
  "host": "0.0.0.0", 
  "port": 8000,
  "rate_limit": 100,
  "cache_size": 6,
  "pivot_lang": "en",
  "model_repo_url": "https://github.com/Helsinki-NLP/Opus-MT-train/tree/master/models",
  "auto_update_models": true,
  "log_level": "INFO",
  "log_file": "fluentai.log",
  "model_update_interval": 86400,
  "supported_languages": ["en", "es", "fr", ...]
}
```

Important settings:
- `cache_size`: Number of models to keep in memory (default: 6)
- `pivot_lang`: Language to use for pivoting translations (default: "en")
- `supported_languages`: List of ISO language codes that your service supports

## Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or run directly:

```bash
python -m app.main
```

## API Usage

### Translating Text

```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"source_lang": "en", "target_lang": "fr", "text": "Hello, world!"}'
```

Response:
```json
{
  "translated_text": "Bonjour, monde!"
}
```

### Checking Status

```bash
curl -X GET "http://localhost:8000/status"
```

Response:
```json
{
  "loaded_models": [
    {
      "model_key": "en-fr",
      "source_lang": "en",
      "target_lang": "fr",
      "loaded_at": "2025-03-23T12:34:56.789012"
    },
    ...
  ]
}
```

### Manual Model Management

Loading a model:
```bash
curl -X POST "http://localhost:8000/load?source_lang=en&target_lang=fr"
```

Unloading a model:
```bash
curl -X POST "http://localhost:8000/unload?source_lang=en&target_lang=fr"
```

Clearing the cache:
```bash
curl -X POST "http://localhost:8000/clear"
```

## Supported Languages

FluentAI supports 50+ languages, including:

- English (en)
- Spanish (es)
- French (fr)
- Chinese (zh)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Portuguese (pt)
- Italian (it)
- Hindi (hi)
- Arabic (ar)
- ... and many more!

See the full list in `config.json`.

## Architecture

The application follows a modular architecture with the following key components:

- **Controllers**: Handle API routing and request validation
- **Services**: Core business logic for model loading and translation
- **Marian Runtime**: Interface with the Marian-NMT translation engine
- **Model Loader**: Manages the LRU cache for dynamic model loading
- **Models**: Pre-trained translation models organized by language pairs

## Testing

Run the test suite:

```bash
pytest app/tests/
```

The tests cover:
- API endpoint functionality
- Asynchronous processing
- Dynamic model loading
- Pivot translation
- Error handling

## Troubleshooting

### Common Issues

1. **Model not found error**:
   - Ensure the model directory follows the naming convention `{source}-{target}`
   - Check that the model files are correctly placed
   - Verify the source and target languages are in the supported_languages list

2. **Translation timeout**:
   - Increase the timeout value in `marian_runtime.py` if needed
   - Check if the model is too large for your hardware
   - Consider using a smaller model for that language pair

3. **WSL path issues**:
   - Verify the path conversion in `marian_runtime.py` matches your WSL setup
   - Ensure WSL can access the model files



## Future Enhancements

- Add automatic model downloading
- Support for fine-tuning models on domain-specific data
- Implement batch translation for improved efficiency
- Add metrics collection for performance monitoring
- Enhance caching strategies for frequently used language pairs

## Credits

FluentAI is built using:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Marian-NMT](https://marian-nmt.github.io/) - Neural Machine Translation runtime
- [Helsinki-NLP Opus-MT](https://github.com/Helsinki-NLP/Opus-MT) - Pre-trained translation models

## License

[MIT License](LICENSE)
