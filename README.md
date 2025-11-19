# vrs_sandbox

RealSense ROS bag data extraction tool for RGB-D-IR and IMU data with timestamps.

## Setup

### Install dependencies

```bash
uv sync --all-extras
```

### Git LFS & ROSBag Setup

Your recorded ROSbag file:

```bash
git lfs install
git lfs pull
```

### Download Intel RealSense Sample Data

For testing and development, you can download official Intel RealSense D435i sample datasets:

```bash
# Download sample data (451MB zip file)
wget https://librealsense.intel.com/rs-tests/TestData/d435i_sample_data.zip

# Extract
unzip d435i_sample_data.zip

# Copy to project (recommended: outdoor scene with IMU data)
cp d435i_walk_around.bag data/rosbag/
```

Available sample files:
- `d435i_walk_around.bag` (803MB) - Outdoor scene with D435i (Depth + RGB + IMU) - Primary test file
- `d435i_walking.bag` (690MB) - Walking scene with D435i (Depth + RGB + IMU)

Source: [IntelRealSense/librealsense Sample Data](https://github.com/IntelRealSense/librealsense/blob/master/doc/sample-data.md)

## Usage

```bash
# Extract data from ROSbag with timestamps
uv run python extract_realsense_data.py data/rosbag/d435i_walk_around.bag
```

## Development

### Run tests

```bash
uv run pytest
```

### Run linter

```bash
uv run ruff check scripts/ tests/
```

### Type checking

```bash
uv run mypy scripts/
```
