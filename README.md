# vidtoolz-rnnn

[![PyPI](https://img.shields.io/pypi/v/vidtoolz-rnnn.svg)](https://pypi.org/project/vidtoolz-rnnn/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/vidtoolz-rnnn?include_prereleases&label=changelog)](https://github.com/sukhbinder/vidtoolz-rnnn/releases)
[![Tests](https://github.com/sukhbinder/vidtoolz-rnnn/workflows/Test/badge.svg)](https://github.com/sukhbinder/vidtoolz-rnnn/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/vidtoolz-rnnn/blob/main/LICENSE)

Noise reduction using ffmpeg rnnn model

## Installation

First install [vidtoolz](https://github.com/sukhbinder/vidtoolz).

```bash
pip install vidtoolz
```

Then install this plugin in the same environment as your vidtoolz application.

```bash
vidtoolz install vidtoolz-rnnn
```
## Usage

type ``vid rnnn --help`` to get help

### Basic Usage

```bash
# Basic usage with explicit output
vidtoolz rnnn -i input.mp3 -o output.wav -m bd --mix 0.6

# Automatic output filename generation
vidtoolz rnnn -i input.mp3 -m lq

# With custom mix ratio
vidtoolz rnnn -i input.mp3 -o output.wav -m mp --mix 0.8
```

### Command Line Arguments

- `-i INPUT_AUDIO, --input_audio INPUT_AUDIO`
  Path to input audio file (e.g. mp3, wav) - **Required**

- `-o OUTPUT_WAV, --output_wav OUTPUT_WAV`
  Path to output WAV file - **Optional** (auto-generated if not provided)

- `-m {bd,cb,lq,mp,sh}, --model {bd,cb,lq,mp,sh}`
  RNNoise model to use. Available models: bd, cb, lq, mp, sh - **Required**

- `--mix MIX`
  Wet/dry mix ratio (0.0 = original, 1.0 = fully denoised) - **Optional** (default: 0.6)

### Available Models

The plugin automatically discovers available RNNoise models from the `models` directory:

- **bd** - beguiling-drafter-2018-08-30
- **cb** - conjoined-burgers-2018-08-28  
- **lq** - leavened-quisling-2018-08-31
- **mp** - marathon-prescription-2018-08-29
- **sh** - somnolent-hogwash-2018-09-01

### Examples

```bash
# Denoise a podcast recording with studio model
vidtoolz rnnn -i podcast.mp3 -m sh -o podcast_clean.wav

# Clean up a noisy street interview
vidtoolz rnnn -i interview.mp3 -m mp --mix 0.7

# Process multiple files (bash loop)
for file in *.mp3; do
    vidtoolz rnnn -i "$file" -m cb
 done
```


## RNNoise Model Suitability Summary

| **Suite / Model Name** | **Recording Environment** | **Noise Level** | **Includes Non-Speech Sounds (cough, laugh, music)** | **Best Use Cases** | **When NOT to Use** |
|------------------------|---------------------------|------------------|------------------------------------------------------|--------------------|--------------------|
| **somnolent-hogwash-2018-09-01** | Clean / reasonable | Low | ❌ No | Studio voice, podcasts, audiobooks, narration, clean travel vlogs | Very noisy scenes, crowd, traffic |
| **beguiling-drafter-2018-08-30** | Reasonable (fan, AC, PC noise) | Low–Medium | ⚠️ Yes (light) | Home recordings, YouTube voiceovers, interviews | Heavy noise, music-heavy background |
| **conjoined-burgers-2018-08-28** | Reasonable → moderately noisy | Medium | ✅ Yes | General-purpose denoising, mixed environments | Extremely noisy environments |
| **marathon-prescription-2018-08-29** | Noisy | Medium–High | ✅ Yes (music, cough, laugh) | Vlogs, street recordings, travel audio, public places | Clean studio voice (may over-denoise) |
| **leavened-quisling-2018-08-31** | Very noisy | High | ✅ Yes | Traffic, crowds, cafés, trains, outdoor speech | Clean or semi-clean audio (can sound robotic) |

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd vidtoolz-rnnn
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
