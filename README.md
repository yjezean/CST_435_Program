# AI Story Creator & Multi-Media Enhancement Pipeline

A Python program that demonstrates **sequential pipeline processing** combined with **parallel service execution**. The program creates a complete multimedia story package from a simple text prompt, showcasing distributed service architecture patterns.

## Program Overview

This program implements a **hybrid pipeline-parallel architecture**:

```
Main Program
    ↓
[Pipeline Stage 1] Story Generator Service (A)
    ↓
[Pipeline Stage 2] Story Analyzer Service (B)
    ↓
[Pipeline Stage 3] Parallel Processing Hub (C)
    ├─→ [Parallel] Image Concept Service (C1)
    ├─→ [Parallel] Audio Script Service (C2)
    ├─→ [Parallel] Translation Service (C3)
    └─→ [Parallel] Formatting Service (C4)
    ↓
[Pipeline Stage 4] Final Aggregator Service (D)
    ↓
Return Complete Package
```

### Features

- **Sequential Pipeline**: Services A → B → D demonstrate dependency chain
- **Parallel Processing**: Service C spawns 4 parallel services simultaneously
- **Timestamp Tracking**: Complete timestamp tracking through the entire pipeline
- **Multiple Output Formats**: Story, analysis, image concepts, audio scripts, translations, formatted outputs
- **Performance Measurement**: Ready for comparison between local, RPC, and gRPC execution

## Architecture

### Services

1. **Service A: Story Generator**
   - Generates creative stories from user prompts
   - Uses template-based generation with theme detection
   - Output: Story text with metadata

2. **Service B: Story Analyzer**
   - Analyzes story sentiment (positive/neutral/negative)
   - Extracts keywords and main characters
   - Calculates statistics (word count, sentence count, etc.)
   - Output: Analysis metadata

3. **Service C: Parallel Processing Hub**
   - Coordinates 4 parallel services:
     - **C1: Image Concept Generator** - Creates visual scene descriptions
     - **C2: Audio Script Service** - Generates narration scripts with pauses
     - **C3: Translation Service** - Translates story to multiple languages
     - **C4: Formatting Service** - Formats story as Markdown and HTML
   - Output: Combined results from all parallel services

4. **Service D: Final Aggregator**
   - Combines all results into final package
   - Validates completeness
   - Generates summary statistics
   - Output: Complete multimedia package

## Input/Output

### Input
- User provides a text prompt/topic (e.g., "A space adventure about robots")
- Can be provided via command line or interactive prompt

### Output
- Complete JSON package containing:
  - Generated story text
  - Story analysis (sentiment, keywords, statistics)
  - Image concept (scene, colors, mood)
  - Audio script with narration markers
  - Translations (Spanish, French)
  - Formatted outputs (Markdown, HTML)
  - Complete timestamp chain for all services
- Terminal display showing execution timeline
- JSON file: `pipeline_output.json`

## Installation

### Requirements
- Python 3.8 or higher
- No external dependencies required for local execution mode

### Setup

1. Clone or download the project:
```bash
cd Programs
```

2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies (if needed for future RPC/gRPC):
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the program with a prompt:

```bash
python main.py "A space adventure about robots"
```

Or run interactively:

```bash
python main.py
# Enter prompt when asked
```

### Example Output

```
=== Pipeline Execution Timeline ===
[Service A: Story Generator]
  Received: 2024-01-15 10:00:00.050
  Started: 2024-01-15 10:00:00.051
  Completed: 2024-01-15 10:00:00.350
  Duration: 299.00ms

[Service B: Story Analyzer]
  Received: 2024-01-15 10:00:00.351
  Started: 2024-01-15 10:00:00.352
  Completed: 2024-01-15 10:00:00.450
  Duration: 98.00ms

[Service C: Parallel Processing Hub]
  [Parallel Services]
    [Service C1: Image Concept] Started: 10:00:00.453, Completed: 10:00:00.580 (127.00ms)
    [Service C2: Audio Script] Started: 10:00:00.453, Completed: 10:00:00.620 (167.00ms)
    [Service C3: Translation] Started: 10:00:00.453, Completed: 10:00:00.750 (297.00ms)
    [Service C4: Formatting] Started: 10:00:00.453, Completed: 10:00:00.520 (67.00ms)
  
  Parallel Batch Completed: 10:00:00.750 (max duration: 297.00ms)

[Service D: Final Aggregator]
  Received: 2024-01-15 10:00:00.751
  Started: 2024-01-15 10:00:00.752
  Completed: 2024-01-15 10:00:00.800
  Duration: 48.00ms

Total Pipeline Duration: 800.00ms
```

## Project Structure

```
Programs/
├── main.py                       # Main program entry point
├── services/
│   ├── service_a_story_generator.py    # Story generation service
│   ├── service_b_story_analyzer.py      # Story analysis service
│   ├── service_c_parallel_hub.py        # Parallel processing coordinator
│   ├── service_c1_image_concept.py      # Image concept generation
│   ├── service_c2_audio_script.py       # Audio script creation
│   ├── service_c3_translation.py        # Translation service
│   ├── service_c4_formatting.py          # Formatting service
│   └── service_d_aggregator.py          # Final aggregation service
├── core/
│   ├── pipeline.py               # Core pipeline logic (local mode)
│   ├── message.py                # Message format with timestamps
│   └── timestamp_tracker.py      # Timestamp management and display
├── utils/
│   ├── story_generator.py        # Story generation logic
│   ├── text_analyzer.py          # Text analysis utilities
│   └── output_formatter.py      # Final output formatting
├── docs/
│   ├── communication_setup.md  # RPC vs gRPC setup guide (reference)
│   └── docker_deployment.md    # Docker container setup guide (reference)
├── requirements.txt
└── README.md
```

## Current Implementation

The current implementation runs in **LOCAL MODE** - all services execute as direct function calls within the same process. This serves as the **baseline** for performance comparison.

### Future Enhancements

1. **RPC Mode**: Implement RPyC communication layer (see `docs/communication_setup.md`)
2. **gRPC Mode**: Implement gRPC communication layer (see `docs/communication_setup.md`)
3. **Docker Deployment**: Containerize services (see `docs/docker_deployment.md`)
4. **Multi-Machine Deployment**: Deploy services across multiple machines

## Timestamp Tracking

Every service invocation records:
- **Received Time**: When the service receives the request
- **Start Time**: When processing begins
- **End Time**: When processing completes
- **Duration**: Processing time in milliseconds

Timestamps propagate through the entire pipeline, allowing:
- Individual service performance measurement
- Pipeline total duration calculation
- Comparison between local, RPC, and gRPC execution modes

## Performance Comparison

This program is designed to compare:

1. **Local Execution** (current): Direct function calls (baseline)
2. **Local with RPC**: Services communicate via RPyC on same machine
3. **Local with gRPC**: Services communicate via gRPC on same machine
4. **Docker Containers with RPC**: Services in containers using RPC
5. **Docker Containers with gRPC**: Services in containers using gRPC
6. **Multi-Machine Deployment**: Services across network (future)

## Example Prompts

Try these prompts:

- "A space adventure about robots"
- "A fantasy tale with dragons and wizards"
- "A modern detective story"
- "An underwater exploration"
- "A time-traveling scientist"

## Output Files

The program generates:
- `pipeline_output.json`: Complete output package with all results and timestamps

## Notes

- Story generation uses template-based algorithms (not AI/ML models)
- Translations are simulated with keyword replacement (for demonstration)
- Processing times include simulated delays to showcase pipeline timing
- All timestamps are recorded in milliseconds for precision

## Troubleshooting

**Issue**: Module import errors
- **Solution**: Ensure you're running from the project root directory

**Issue**: No output file generated
- **Solution**: Check file permissions in the current directory

**Issue**: Timestamps not displaying correctly
- **Solution**: Ensure system clock is synchronized

## Next Steps

For implementing distributed communication:

1. Review `docs/communication_setup.md` for RPC/gRPC setup
2. Review `docs/docker_deployment.md` for containerization
3. Implement communication layers according to the guides
4. Compare performance metrics across different deployment modes

## License

This project is for educational purposes as part of CST435 Parallel and Cloud Computing assignment.

## Authors

Chong Yi Jian 

