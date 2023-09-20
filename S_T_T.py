import torch
from glob import glob

def recognize_audio(SPEECH_FILE):

    device = torch.device('cpu')  # gpu also works, but our models are fast enough for CPU
    
    model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                            model='silero_stt',
                                            language='en', # also available 'de', 'es'
                                            device=device)

    (read_batch, split_into_batches,
      read_audio, prepare_model_input) = utils  # see function signature for details
    
    test_files = glob(SPEECH_FILE)
    batches = split_into_batches(test_files, batch_size=10)
    input = prepare_model_input(read_batch(batches[0]),
                                device=device)
    
    output = model(input)
    for example in output:
        return decoder(example.cpu())
