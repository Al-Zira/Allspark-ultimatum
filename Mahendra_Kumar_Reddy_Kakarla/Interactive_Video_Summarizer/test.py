
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch

# Use correct local path
model_path = "/local_model"  # Ensure this matches your saved directory

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Load the model from local storage
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_path, torch_dtype=torch_dtype, low_cpu_mem_usage=True
)
model.to(device)

# Load the processor
processor = AutoProcessor.from_pretrained(model_path)

# Create ASR pipeline
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    chunk_length_s=30,
    batch_size=8,  # Adjust batch size based on your hardware
    torch_dtype=torch_dtype,
    device=device,
    return_timestamps=True
)

print("Model loaded successfully from local storage!")
