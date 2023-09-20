from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def translate(translate_input) -> str:
    # Load the tokenizer and model for translation
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-fr")
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-fr")
    
    # Encode the input text
    input_ids = tokenizer.encode(translate_input, return_tensors="pt")
    
    # Generate the translation
    outputs = model.generate(input_ids, max_length=512)
    
    # Decode the generated output
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(decoded)
    return decoded

