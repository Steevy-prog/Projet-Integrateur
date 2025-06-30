from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_id = "tiiuae/falcon-7b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

output = pipe("How can I help you?", max_new_tokens=100)
print(output[0]["generated_text"])