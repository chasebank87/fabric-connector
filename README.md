
## Overview

FabricYTProxy is a Python-based application that integrates with Fabric and YT binaries to provide a proxy service. It includes a FastAPI server for handling API requests and a system tray application for managing the API server status. The application supports both macOS and Windows platforms.

## Table of Contents

- [Installation](#installation)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [License](#license)

## Installation

A MacOS and Windows executable is provided for easy installation. Click the latest release.

**When running on windows, fabric is ran using WSL, we need a WSL1 or WSL2 distribution running and set as default, fabric installed, fabric configures, and the user must be the same as your windows user.**

### Prerequisites

Ensure you have Python 3.7+ installed on your system. You will also need to have the Fabric and YT binaries installed and accessible in your system's PATH.

Portable executables are available for MacOS and Windows (Releases)[https://github.com/chasebank87/fabric-connector/releases]

### Steps

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/fabricytproxy.git
    cd fabricytproxy
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Ensure the paths to the Fabric and YT binaries are correctly set in the code:
    ```python
    FABRIC_PATH = "/path/to/fabric"
    YT_PATH = "/path/to/yt"
    ```

## Dependencies

The project relies on several Python packages, which are listed in `requirements.txt`:

- `rumps==0.4.0`
- `fastapi==0.95.1`
- `uvicorn==0.22.0`
- `pydantic==1.10.7`
- `requests==2.30.0`
- `pystray==0.19.4`
- `pillow==9.5.0`
- `pyinstaller==5.10.1`
- `py2app==0.28.6`

## Configuration

When using windows

## Usage

### Running the Application

To start the application, run:

```sh
python main.py
```

This will start the system tray application and the FastAPI server.

### System Tray Application

The system tray application provides options to:

- Check API status
- Start/Stop the API server
- Open API documentation
- Exit the application

### API Endpoints

The FastAPI server exposes several endpoints:

#### POST `/fabric`

Runs the Fabric binary with the provided command and returns the output.

**Request Body:**
```json
{
  "pattern": "pattern_name",
  "data": "input_data"
}
```

**Response:**
```json
{
  "output": "result_output"
}
```

#### POST `/yt`

Runs the YT binary with the provided command and returns the output.

**Request Body:**
```json
{
  "pattern": "pattern_name",
  "url": "video_url"
}
```

**Response:**
```json
{
  "output": "result_output"
}
```

#### GET `/patterns`

Returns a list of available patterns from the Fabric binary.

**Response:**
```json
{
  "data": {
    "patterns": [
      {"name": "pattern1"},
      {"name": "pattern2"}
    ]
  }
}
```

## Development

### Building for macOS

To build a macOS application bundle, use `pyinstaller`:

```sh
pyinstaller main.spec
```

### Building for Windows

To build a Windows executable, use `pyinstaller`:

```sh
pyinstaller main.spec
```

### Running Tests

To run tests, use:

```sh
pytest tests/
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For more information, please refer to the [documentation](http://127.0.0.1:8000/docs).