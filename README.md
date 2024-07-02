# Fabric YT Proxy

A Mac menu bar application that proxies commands to Fabric and YT.

## Description

This application runs in the background as a menu bar icon on macOS. It provides an API that proxies commands to Fabric and YT, which are tools for AI-assisted task automation.

## Features

- Mac menu bar application with a brain icon
- FastAPI-based API for proxying commands
- Integration with Fabric and YT tools

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/fabric_yt_proxy.git
   cd fabric_yt_proxy
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install the application:
   ```
   pip install -e .
   ```

## Usage

1. Run the application:
   ```
   fabric_yt_proxy
   ```

2. The brain icon will appear in your Mac's menu bar.

3. Click on the icon to access the menu options:
   - Start API: Starts the FastAPI server
   - Stop API: Stops the FastAPI server

4. Once the API is started, you can send POST requests to:
   - `http://127.0.0.1:8000/fabric` for Fabric commands
   - `http://127.0.0.1:8000/yt` for YT commands

   Example using curl:
   ```
   curl -X POST "http://127.0.0.1:8000/fabric" -H "Content-Type: application/json" -d '{"command": "your_fabric_command_here"}'
   ```

## Requirements

- macOS
- Python 3.7 or higher
- Fabric and YT tools installed (https://github.com/danielmiessler/fabric)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.