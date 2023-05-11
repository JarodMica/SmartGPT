import openai
import yaml
import os

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'

# Set-up variables
gpt3 = "gpt-3.5-turbo"
gpt4 = "gpt-4"
temperature = 0.5
token_counts = {gpt3: 0, gpt4: 0}
rate_of_3 = 0.002/1000
rate_of_4 = 0.06/1000
keys = "keys.yaml"

with open(keys, "r") as file:
    keys = yaml.safe_load(file)

OPENAI_KEY = keys['OPENAI_KEY']
openai.api_key = OPENAI_KEY

def generation(gpt_model, messages):
    '''
    Calls the OpenAI API to complete a ChatCompletion

    Args:
        gpt_model (str) - OpenAI model to use
        messages (list) - A list of dictionaries formatted for OpenAI ChatCompletions

    Returns:
        response (str)  - GPT "assistant" response based on messages
        tokens (int)    - number of tokens used
    '''
    completion = openai.ChatCompletion.create(
            model=gpt_model,
            messages=messages,
            
            temperature=temperature
        )
    response = completion.choices[0].message.content
    tokens = completion.usage.total_tokens

    # update global token counts
    global token_counts
    token_counts[gpt_model] += tokens

    return response, tokens

def concat_output(responses):
    '''
    Concatenate the initial outputs to label which answer they are, formatted to
    start with "Answer Option X:" and then the answer following it

    Args:
        responses (list) - A list of responses from initial_output()

    Returns:
        answer_prompt (str) - A concatenated string of the answers listed in responses
    '''
    answer_prompt = ""
    for i, response in enumerate(responses, start=1):
        answer_prompt += f"Answer Option {i}: {response}\n\n"
    return answer_prompt

def initial_output(user_input, outputs):
    '''
    Produces x initial outputs where x is the number of answers.  In this case,
    it's 3 answers but this can be changed based on needs.

    Args:
        user_input (str) - The main question that is being asked and answered

    Retuns:
        responses (list) - A list of responses that is x in length
        initial_prompt (str) - The specificly formatted prompt that is sent to the OpenAI API 
    '''
    responses = []
    initial_prompt = (f"Question. {user_input}\n"
                "Answer: Let's work this out in a step "
                "by step way to be sure we have the right answer:" )
    for _ in range(outputs):
        messages = [{"role" :"user", "content" : initial_prompt}]
        response, tokens = generation(gpt3, messages)
        responses.append(response)

    # print(response)   #Debugging Purposes
    # print(tokens)     #Debugging Purposes
    return responses, initial_prompt

def researcher(answers, initial_prompt, outputs):
    '''
    Provides feedback on the answers from initial_output, listing all of the flaws and faulty logic used.

    Args:
        answers (str) - All of the answers from intital_output
        initial_prompt (str) - The specificly formatted prompt that is sent to the OpenAI API, comes from intial_output()

    Returns:
        messages (list) - Includes everything that has been answered and analyzed so far, 
                        and is a list in the accepted format for OpenAI ChatCompletions.
    '''
    prompt = (f"You are a researcher tasked with investigating the {outputs} response options provided. "
              "List the flaws and faulty logic of each answer option. "
              "Let's work this out in a step by step way to be sure we have all the errors:")

    messages = [{"role": "user", "content": initial_prompt},
                {"role" : "assistant", "content" : answers},
                {"role" : "user", "content" : prompt},
                ]
    response, tokens = generation(gpt3, messages)
    messages.append({"role" : "assistant", "content" : response})

    # print(response)   #Debugging Purposes
    # print(tokens)     #Debugging Purposes
    return messages

def resolver(messages, outputs):
    prompt = ("The previous responses are from the researcher. You are a resolver tasked with 1) "
            f"finding which of the {outputs} answer options the researcher thought was best 2) "
            "improving that answer, and 3) Printing the improved answer in full. "
            "Let's work this out in a step by step way to be sure we have the right answer: ")

    messages.append({"role": "user", "content": prompt})

    response, tokens = generation(gpt4, messages)

    print(f"{Colors.YELLOW}\nResolved Response:\n{Colors.ENDC}") 
    print(response)   #Debugging Purposes
    # print(tokens) #Debugging Purposes

    data = "Messages:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in messages]) + "\n\nSmartGPT Final Answer:\n" + response
    save_to_file(data)
    
    return response

def final_output(final_response):
    prompt = ("Based on the following response, extract out only the improved " 
            "response and nothing else.  DO NOT include typical responses and "
            "the answer should only have the improved response: \n\n"
            f"{final_response}")
    
    messages = [{"role" : "user", "content" : prompt}]
    response, tokens = generation(gpt3, messages)

    print(f"{Colors.YELLOW}SmartGPT response:\n{Colors.ENDC}", response) 
    # print(tokens) #Debugging Purposes

def save_to_file(data, filename_prefix="question"):
    # check if 'conversations' directory exists and if not, create it
    if not os.path.exists('conversations'):
        os.makedirs('conversations')

    # check for existing files and increment file number
    suffix = 1
    while os.path.exists(f"conversations/{filename_prefix}_{suffix}.txt"):
        suffix += 1

    with open(f"conversations/{filename_prefix}_{suffix}.txt", "w", encoding='utf-8') as file:
        file.write(data)

def main():
    valid_range = range(1, 5)
    outputs=0
    while outputs not in valid_range:
        try:
            outputs = int(input("Enter the # of outputs you want (1 to 4):  "))
        except:
            print("The only valid choices are 1-4.")
    user_input = input("Question: ")
    # user_input = ("I left 5 clothes to dry out in the sun. It took them 5 hours to dry completely. How long would it take to dry 30 clothes?")
    print(f"\n{Colors.YELLOW}Process Starting{Colors.ENDC}")
    
    print(f"Generating answers: {Colors.GREEN}1/4 complete{Colors.ENDC}")
    initial_responses, initial_prompt = initial_output(user_input, outputs)
    answers = concat_output(initial_responses)
    
    print(f"Researching answers: {Colors.GREEN}2/4 complete{Colors.ENDC}")
    researcher_response = researcher(answers, initial_prompt, outputs)
    
    print(f"Resolving answers: {Colors.GREEN}3/4 complete\n{Colors.ENDC}")
    final_response = resolver(researcher_response, outputs)
    
    # final_output(final_response)

     # update tokens and calculate total cost
    total_calc = ((token_counts[gpt3] * rate_of_3) + (token_counts[gpt4] * rate_of_4))
    total_cost = f"${total_calc:.2f}"
    print(f"\nYou used {token_counts[gpt3]} gpt3.5 tokens")
    print(f"You used {token_counts[gpt4]} gpt4 tokens")
    print(f"So this query cost you {Colors.GREEN}{total_cost}{Colors.ENDC}")

if __name__ == "__main__":
    main()

    
