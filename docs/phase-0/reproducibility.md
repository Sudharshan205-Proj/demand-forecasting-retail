# Reproducibility

## Objective

Another developer should be able to reproduce the important project workflow from the repository documentation.

## Requirements

The project will document:

- Python version
- R version
- Package dependencies
- Dataset source
- Dataset version
- Preprocessing decisions
- Feature-engineering decisions
- Model configurations
- Hyperparameters
- Evaluation metrics
- Random seeds where relevant
- Training/validation/test methodology
- Application configuration
- Deployment configuration

## Randomness

Random processes will use explicit seeds where appropriate.

## Time-Series Reproducibility

The project will preserve temporal ordering.

Random shuffling will not be used when it creates temporal leakage.

## Data Leakage

Training, validation and test data must remain conceptually separate.

Test data must not be used for model selection or tuning.

## Environment

The Python environment will use a virtual environment.

Dependencies will be recorded.

R dependencies will be documented separately.

## Dataset

Raw data will not be silently modified.

Processing scripts will produce processed datasets.

## Model Reproducibility

Important model parameters will be recorded.

Final model artifacts will be persisted.

## Results

Important evaluation results will be saved and documented.

No result will be presented as verified until it has actually been generated.