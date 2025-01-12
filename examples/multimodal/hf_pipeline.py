# pip install scipy torch transformers
# NOTE: also need to install ffmpeg binary
import json

import torch
from transformers import pipeline

from datachain import C, DataChain, Mapper


class Helper(Mapper):
    def __init__(self, model, device, **kwargs):
        self.model = model
        self.device = device
        self.kwargs = kwargs

    def setup(self):
        self.helper = pipeline(model=self.model, device=self.device)

    def process(self, file):
        imgs = file.read()
        result = self.helper(
            imgs,
            **self.kwargs,
        )
        return (json.dumps(result), "")


image_source = "gs://datachain-demo/dogs-and-cats/"
audio_source = "gs://datachain-demo/speech-emotion-recognition-dataset/"
text_source = "gs://datachain-demo/nlp-cnn-stories"

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


if __name__ == "__main__":
    print("** HuggingFace pipeline helper model zoo demo **")
    print("\nZero-shot object detection and classification:")
    (
        DataChain.from_storage(
            image_source,
            anon=True,
            type="image",
        )
        .filter(C("file.name").glob("*.jpg"))
        .limit(1)
        .map(
            Helper(
                model="google/owlv2-base-patch16",
                device=device,
                candidate_labels=["cat", "dog", "squirrel", "unknown"],
            ),
            params=["file"],
            output={"model_output": dict, "error": str},
        )
        .select("file.source", "file.parent", "file.name", "model_output", "error")
        .show()
    )

    print("\nNot-safe-for-work image detection:")
    (
        DataChain.from_storage(
            image_source,
            anon=True,
            type="image",
        )
        .filter(C("file.name").glob("*.jpg"))
        .limit(1)
        .map(
            Helper(
                model="Falconsai/nsfw_image_detection",
                device=device,
            ),
            params=["file"],
            output={"model_output": dict, "error": str},
        )
        .select("file.source", "file.parent", "file.name", "model_output", "error")
        .show()
    )

    print("\nAudio emotion classification:")
    (
        DataChain.from_storage(
            audio_source,
            anon=True,
            type="binary",
        )
        .filter(C("file.name").glob("*.wav"))
        .limit(1)
        .map(
            Helper(
                model="Krithika-p/my_awesome_emotions_model",
                device=device,
            ),
            params=["file"],
            output={"model_output": dict, "error": str},
        )
        .select("file.source", "file.parent", "file.name", "model_output", "error")
        .show()
    )
    print("\nLong text summarization:")
    (
        DataChain.from_storage(
            text_source,
            anon=True,
            type="text",
        )
        .filter(C("file.name").glob("*.story"))
        .limit(1)
        .map(
            Helper(
                model="pszemraj/led-large-book-summary",
                device=device,
                max_length=150,
            ),
            params=["file"],
            output={"model_output": dict, "error": str},
        )
        .select("file.source", "file.parent", "file.name", "model_output", "error")
        .show()
    )
