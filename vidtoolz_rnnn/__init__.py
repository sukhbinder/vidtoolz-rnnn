import vidtoolz
from vidtoolz.utils import determine_output_path
import subprocess
from pathlib import Path


def get_available_models():
    """Get available RNNoise models from the models directory."""
    models_dir = Path(__file__).parent / "models"
    if not models_dir.exists():
        return []

    # Get all .rnnn files and return their names without extension
    model_files = [f.stem for f in models_dir.glob("*.rnnn") if f.is_file()]
    return sorted(model_files)


def create_parser(subparser):
    parser = subparser.add_parser(
        "rnnn", description="Noise reduction using ffmpeg rnnn model"
    )
    # Add subprser arguments here.
    parser.add_argument(
        "-i",
        "--input_audio",
        type=str,
        required=True,
        help="Path to input audio file (e.g. mp3, wav)",
    )
    parser.add_argument(
        "-o", "--output_wav", type=str, default=None, help="Path to output WAV file"
    )

    # Get available models for choices
    available_models = get_available_models()
    model_help = f"RNNoise model to use. (default: %(default)s) Available models: {', '.join(available_models) if available_models else 'none found'}"

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="mp",
        choices=available_models,
        help=model_help,
    )
    parser.add_argument(
        "--mix",
        type=float,
        default=0.9,
        help="Wet/dry mix ratio (0.0 = original, 1.0 = fully denoised) (default: %(default)s)",
    )
    return parser


def denoise_audio(
    input_audio: str, output_wav: str, model_path: str, mix: float = 0.6
) -> None:
    """
    Apply RNNoise-based denoising using FFmpeg arnndn filter.

    :param input_audio: Path to input audio file (e.g. mp3, wav)
    :param output_wav: Path to output WAV file
    :param model_path: Path to RNNoise .rnnn model file or model name
    :param mix: Wet/dry mix ratio (0.0 = original, 1.0 = fully denoised)
    """

    input_audio = Path(input_audio)
    output_wav = Path(output_wav)

    if model_path.endswith(".rnnn"):
        model_path = Path(model_path)
    else:
        # Construct the full model path from the chosen model name
        models_dir = Path(__file__).parent / "models"
        model_path = models_dir / f"{model_path}.rnnn"

    if not input_audio.exists():
        raise FileNotFoundError(f"Input audio not found: {input_audio}")

    if not model_path.exists():
        raise FileNotFoundError(f"RNNoise model not found: {model_path}")

    if not (0.0 <= mix <= 1.0):
        raise ValueError("mix must be between 0.0 and 1.0")

    cmd = [
        "ffmpeg",
        "-y",  # overwrite output if exists
        "-i",
        str(input_audio),
        "-filter:a",
        f"arnndn=model={model_path}:mix={mix}",
        "-codec:a",
        "pcm_s24le",
        str(output_wav),
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("FFmpeg denoising failed") from e


class ViztoolzPlugin:
    """Noise reduction using ffmpeg rnnn model"""

    __name__ = "rnnn"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        output = determine_output_path(args.input_audio, args.output_wav, "denoise")
        if not output.endswith(".wav"):
            output = f"{output}.wav"
        # Construct the full model path from the chosen model name
        models_dir = Path(__file__).parent / "models"
        model_path = models_dir / f"{args.model}.rnnn"

        # Call the denoise_audio function with the provided arguments
        denoise_audio(
            input_audio=args.input_audio,
            output_wav=output,
            model_path=str(model_path),
            mix=args.mix,
        )

    def hello(self, args):
        # this routine will be called when "vidtoolz "rnnn is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


rnnn_plugin = ViztoolzPlugin()
