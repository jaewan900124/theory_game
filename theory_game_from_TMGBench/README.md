# TMGBench: TMGBench: A Systematic Game Benchmark for Evaluating Strategic Reasoning Abilities of LLMs

This repository contains the code, data, and metadata for our NeurIPS 2025 Datasets and Benchmarks submission: **TMGBench: A Systematic Game Benchmark for Evaluating Strategic Reasoning Abilities of LLMs**. The benchmark evaluates the strategic reasoning of large language models using 2x2 matrix games with narrative contexts and theory-of-mind variations.

## Directory Structure
```
TMGBench
├── dataset/ # Contains the dataset files and prompt files(JSON/TXT)
    |── classic/ # Contains the classic games description files
    |── story-based/ # Contains the story-based games description files
├── scripts/ # Contains the scripts for evaluation
├── models/ # Contains the class definitions of the models to evaluate
├── requirements.txt # Python dependencies
└── README.md # Project readme
```

## Usage

```
./run_classic.sh # Runs the classic games evaluation
./run_story.sh # Runs the story-based games evaluation
```

Remember to install the required dependencies using `pip install -r requirements.txt` and configure the `config.env` file with your api keys and url paths of models.

## License

This dataset is licensed under the CC-BY 4.0 License.