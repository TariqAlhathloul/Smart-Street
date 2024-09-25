# Smart-Street
This project focuses on detecting road lines using the YOLOv8n model, specifically identifying solid yellow lines indicating "No Overtaking" zones and broken yellow lines where overtaking is allowed. The dataset consists of images collected via a dash cam, which are annotated using Roboflow.

[![DataSet](https://raw.githubusercontent.com/roboflow-ai/notebooks/main/assets/badges/roboflow.svg)](https://universe.roboflow.com/capstoneteam/road-lines-segmentation-2/dataset/1)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Smart-Street.git
    cd Smart-Street
    ```

2. Create a virtual environment:
    ```bash
    python3 -m venv project-env
    source project-env/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the violation detection on the example video, use the this command:
```bash
cd deployment
python detect.py
```

To run live violation detection, use the this command:
```bash
cd deployment
python run.py
```

<a href="https://www.youtube.com/watch?v=_5nmKUGjOls" target="_blank">
  <img src="https://img.youtube.com/vi/_5nmKUGjOls/maxresdefault.jpg" alt="Watch the video" width="600" height="400">
</a>