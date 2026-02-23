import pytest
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any
from data_pipeline import extract_data, transform_data, load_data, validate_data

# Constants for test data
VALID_INPUT_DATA = [
    {"patient_id": 1, "age": 45, "diagnosis": "diabetes"},
    {"patient_id": 2, "age": 60, "diagnosis": "hypertension"},
]

INVALID_INPUT_DATA = [
    {"patient_id": 1, "age": -5, "diagnosis": "diabetes"},  # Invalid age
    {"patient_id": None, "age": 60, "diagnosis": "hypertension"},  # Missing patient_id
]

TRANSFORMED_DATA = [
    {"patient_id": 1, "age_group": "40-50", "diagnosis": "diabetes"},
    {"patient_id": 2, "age_group": "60+", "diagnosis": "hypertension"},
]

VALIDATED_DATA = [
    {"patient_id": 1, "age_group": "40-50", "diagnosis": "diabetes", "valid": True},
    {"patient_id": 2, "age_group": "60+", "diagnosis": "hypertension", "valid": True},
]

# Fixtures for setup and teardown
@pytest.fixture
def mock_data_source():
    """Fixture to mock the data source."""
    return MagicMock(return_value=VALID_INPUT_DATA)

@pytest.fixture
def mock_data_sink():
    """Fixture to mock the data sink."""
    return MagicMock()

@pytest.fixture
def mock_transform_function():
    """Fixture to mock the transformation function."""
    return MagicMock(return_value=TRANSFORMED_DATA)

@pytest.fixture
def mock_validation_function():
    """Fixture to mock the validation function."""
    return MagicMock(return_value=VALIDATED_DATA)

# Test cases
def test_extract_data_happy_path(mock_data_source):
    """Test the extract_data function with valid input."""
    data = extract_data(mock_data_source)
    assert data == VALID_INPUT_DATA, "Extracted data does not match expected output."

def test_extract_data_empty_source():
    """Test the extract_data function with an empty data source."""
    mock_data_source = MagicMock(return_value=[])
    data = extract_data(mock_data_source)
    assert data == [], "Extracted data should be empty when the source is empty."

def test_transform_data_happy_path(mock_transform_function):
    """Test the transform_data function with valid input."""
    transformed_data = transform_data(VALID_INPUT_DATA, mock_transform_function)
    assert transformed_data == TRANSFORMED_DATA, "Transformed data does not match expected output."

@pytest.mark.parametrize("invalid_data", INVALID_INPUT_DATA)
def test_transform_data_invalid_input(invalid_data, mock_transform_function):
    """Test the transform_data function with invalid input."""
    with pytest.raises(ValueError, match="Invalid input data"):
        transform_data([invalid_data], mock_transform_function)

def test_load_data_happy_path(mock_data_sink):
    """Test the load_data function with valid input."""
    load_data(TRANSFORMED_DATA, mock_data_sink)
    mock_data_sink.assert_called_once_with(TRANSFORMED_DATA)

def test_load_data_empty_input(mock_data_sink):
    """Test the load_data function with empty input."""
    load_data([], mock_data_sink)
    mock_data_sink.assert_called_once_with([])

def test_validate_data_happy_path(mock_validation_function):
    """Test the validate_data function with valid input."""
    validated_data = validate_data(TRANSFORMED_DATA, mock_validation_function)
    assert validated_data == VALIDATED_DATA, "Validated data does not match expected output."

def test_validate_data_invalid_input(mock_validation_function):
    """Test the validate_data function with invalid input."""
    mock_validation_function.side_effect = ValueError("Validation failed")
    with pytest.raises(ValueError, match="Validation failed"):
        validate_data(TRANSFORMED_DATA, mock_validation_function)

# Edge case tests
def test_extract_data_large_dataset():
    """Test the extract_data function with a large dataset."""
    large_data = [{"patient_id": i, "age": 30 + i % 50, "diagnosis": "condition"} for i in range(10000)]
    mock_data_source = MagicMock(return_value=large_data)
    data = extract_data(mock_data_source)
    assert len(data) == 10000, "Extracted data size does not match expected size."

def test_transform_data_boundary_conditions(mock_transform_function):
    """Test the transform_data function with boundary conditions."""
    boundary_data = [{"patient_id": 1, "age": 0, "diagnosis": "unknown"}]
    transformed_data = transform_data(boundary_data, mock_transform_function)
    mock_transform_function.assert_called_once_with(boundary_data)
    assert transformed_data is not None, "Transformation failed for boundary condition."

def test_load_data_failure(mock_data_sink):
    """Test the load_data function when the sink fails."""
    mock_data_sink.side_effect = RuntimeError("Data sink failure")
    with pytest.raises(RuntimeError, match="Data sink failure"):
        load_data(TRANSFORMED_DATA, mock_data_sink)

def test_validate_data_partial_failure(mock_validation_function):
    """Test the validate_data function with partial validation failure."""
    partial_validated_data = [
        {"patient_id": 1, "age_group": "40-50", "diagnosis": "diabetes", "valid": True},
        {"patient_id": 2, "age_group": "60+", "diagnosis": "hypertension", "valid": False},
    ]
    mock_validation_function.return_value = partial_validated_data
    validated_data = validate_data(TRANSFORMED_DATA, mock_validation_function)
    assert validated_data == partial_validated_data, "Partial validation results do not match expected output."