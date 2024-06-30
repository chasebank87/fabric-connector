# Fabric Connector README

## Overview

This project consists of a FastAPI application and a macOS menu bar application built using Rumps. The FastAPI application provides endpoints for interacting with Fabric and YouTube transcription services, while the Rumps application provides a user interface to monitor and interact with the FastAPI service.

## Table of Contents

- [Fabric Connector README](#fabric-connector-readme)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Project Structure](#project-structure)
  - [API Endpoints](#api-endpoints)
    - [Fabric Routes](#fabric-routes)
      - [`GET /get-patterns`](#get-get-patterns)
      - [`POST /run-fabric`](#post-run-fabric)
    - [YouTube Routes](#youtube-routes)
      - [`GET /transcribe`](#get-transcribe)
  - [Rumps Application](#rumps-application)
    - [Key Components](#key-components)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-repo/myapp.git
    cd myapp
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Ensure you have the `fabric` and `yt` binaries installed and accessible in your PATH.

## Usage

To run the application, execute the following command:
```sh
python main.py
```

This will start the FastAPI server on port `49152` and the Rumps application in the macOS menu bar.

## Project Structure

```
myapp/
├── main.py
├── routes/
│   ├── fabric_routes.py
│   └── yt_routes.py
├── assets/
│   └── icons/
│       └── fabric-brain.icns
├── requirements.txt
└── README.md
```

- **main.py**: Entry point for the application.
- **routes/**: Contains route definitions for the FastAPI application.
  - **fabric_routes.py**: Routes related to Fabric operations.
  - **yt_routes.py**: Routes related to YouTube transcription.
- **assets/**: Contains static assets like icons.
- **requirements.txt**: Lists the Python dependencies.

## API Endpoints

### Fabric Routes

#### `GET /get-patterns`

Runs the Fabric binary with the `--list` option and returns the output.

**Response:**
```json
{
  "patterns": ["pattern1", "pattern2", ...]
}
```

#### `POST /run-fabric`

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

### YouTube Routes

#### `GET /transcribe`

Runs the yt binary with the `--transcribe` option and returns the output.

**Query Parameters:**
- `url`: The URL of the YouTube video to transcribe.

**Response:**
```json
{
  "transcription": ["line1", "line2", ...]
}
```

## Rumps Application

The Rumps application provides a macOS menu bar interface with the following features:

- **API Status**: Displays whether the FastAPI server is running or not.
- **Open API Docs**: Opens the FastAPI documentation in the default web browser.
- **Quit**: Stops the FastAPI server and quits the application.

### Key Components

- **MyApp Class**: Inherits from `rumps.App` and initializes the menu items.
- **check_port Method**: Periodically checks if the FastAPI server is running.
- **open_api_docs Method**: Opens the API documentation in a web browser.
- **quit_app Method**: Stops the FastAPI server and quits the application.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.