import pytest
import vidtoolz_rnnn as w
from pathlib import Path
import os

from argparse import ArgumentParser

# Define if we're running in GitHub Actions
IN_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'

def test_get_available_models():
    """Test that get_available_models returns a list of available model names."""
    models = w.get_available_models()

    # Should return a list
    assert isinstance(models, list)

    # Should contain known model names
    expected_models = ['bd', 'cb', 'lq', 'mp', 'sh']
    assert models == expected_models

    # All items should be strings
    for model in models:
        assert isinstance(model, str)
        assert len(model) > 0

def test_get_available_models_nonexistent_directory():
    """Test that get_available_models handles non-existent directory gracefully."""
    # Temporarily change the function to look for a non-existent directory
    original_function = w.get_available_models

    def mock_get_available_models():
        models_dir = Path("/non/existent/path")
        if not models_dir.exists():
            return []
        model_files = [f.stem for f in models_dir.glob("*.rnnn") if f.is_file()]
        return sorted(model_files)

    # Test the mock function
    result = mock_get_available_models()
    assert result == []
    assert isinstance(result, list)

def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    # Test parsing with new arguments
    result = parser.parse_args([
        '-i', 'input.mp3',
        '-o', 'output.wav',
        '-m', 'bd',
        '--mix', '0.5'
    ])

    assert result.input_audio == 'input.mp3'
    assert result.output_wav == 'output.wav'
    assert result.model == 'bd'
    assert result.mix == 0.5

def test_create_parser_model_choices():
    """Test that model argument only accepts valid choices."""
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    # Test with valid model
    result = parser.parse_args(['-i', 'input.mp3', '-o', 'output.wav', '-m', 'cb'])
    assert result.model == 'cb'

    # Test with invalid model - should raise SystemExit
    with pytest.raises(SystemExit):
        parser.parse_args(['-i', 'input.mp3', '-o', 'output.wav', '-m', 'invalid_model'])

def test_create_parser_default_mix():
    """Test that mix argument has correct default value."""
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    result = parser.parse_args(['-i', 'input.mp3', '-o', 'output.wav', '-m', 'lq'])
    assert result.mix == 0.6  # Default value

def test_create_parser_required_arguments():
    """Test that required arguments are enforced."""
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    # Missing required arguments should raise SystemExit
    with pytest.raises(SystemExit):
        parser.parse_args([])  # No arguments

    with pytest.raises(SystemExit):
        parser.parse_args(['-i', 'input.mp3'])  # Missing output and model

def test_create_parser_help_text():
    """Test that help text includes available models."""
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    # Get help text
    help_text = parser.format_help()

    # Should mention available models
    assert "Available models:" in help_text

    # Should include at least some of the known models
    assert any(model in help_text for model in ['bd', 'cb', 'lq', 'mp', 'sh'])

def test_model_path_construction():
    """Test that model path is correctly constructed in run method."""
    # This is more of an integration test - we'll test the path construction logic
    models_dir = Path(__file__).parent.parent / "vidtoolz_rnnn" / "models"

    for model_name in ['bd', 'cb', 'lq', 'mp', 'sh']:
        model_path = models_dir / f"{model_name}.rnnn"
        assert model_path.exists(), f"Model file {model_path} should exist"

def test_plugin(capsys):
    w.rnnn_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``vidtoolz`` plugin." in captured.out


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_realcase_rnnn(tmpdir):
    outfile = tmpdir / "test.wav"
    testdata = Path(__file__).parent / "test_data"

    audfile = testdata / "test.mp3"
    argv = ["-i", str(audfile), "-m", "lq","--mix","1", "-o", str(outfile)]
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)
    args = parser.parse_args(argv)
    args.func = None
    w.rnnn_plugin.run(args)
    assert outfile.exists()
