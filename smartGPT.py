import openai
import yaml

gpt3 = "gpt-3.5-turbo"
gpt4 = "gpt-4"
temperature = 0.5
gpt3_tokens = 0
gpt4_tokens = 0
rate_of_3 = 0.002/1000
rate_of_4 = 0.06/1000
total_cost = (gpt3_tokens*rate_of_3 + gpt3_tokens*rate_of_4)
keys = "keys.yaml"

with open(keys, "r") as file:
    keys = yaml.safe_load(file)

OPENAI_KEY = keys['OPENAI_KEY']
openai.api_key = OPENAI_KEY

def initial_output(user_input):
    responses = []
    initial_prompt = (f"Question. {user_input}.\n"
                "Answer: Let's work this out in a step"
                " by step way to be sure we have the right answer:" )
    for _ in range(3):
        messages = [{"role" :"user", "content" : initial_prompt}]
        completion = openai.ChatCompletion.create(
            model = gpt3,
            messages = messages,
            temperature = temperature
        )
        response = completion.choices[0].message.content
        tokens = completion.usage.total_tokens
        responses.append(response)
        print(response)
        print(tokens)
        global gpt3_tokens
        gpt3_tokens+=tokens
    return responses, initial_prompt

def researcher(answer_list, initial_prompt):
    prompt = ("You are a researcher tasked with investigating the three response options provided. "
              "List the flaws and faulty logic of each answer option. "
              "Let's work this out in a step by step way to be sure we have all the errors:")

    messages = [{"role": "user", "content": initial_prompt},
                {"role" : "assistant", "content" : answer_list},
                {"role" : "user", "content" : prompt}
                ]

    completion = openai.ChatCompletion.create(
        model=gpt3,
        messages=messages,
        temperature = temperature
    )
    response = completion.choices[0].message.content
    tokens = completion.usage.total_tokens
    print(response)
    print(tokens)
    global gpt3_tokens
    gpt3_tokens+=tokens

    messages.append({"role" : "assistant", "content" : response})

    return messages

def resolver(messages):
    prompt = ("The previous responses are from the researcher. You are a resolver tasked with 1)"
            "finding which of the three answer options the researcher thought was best 2)"
            "improving that answer, and 3) Printing the improved answer in full. "
            "Let's work this out in a step by step way to be sure we have the right answer: ")

    messages.append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=gpt4,
        messages=messages,
        temperature = temperature
    )
    
    response = completion.choices[0].message.content
    tokens = completion.usage.total_tokens
    print(response)
    print(tokens)
    global gpt4_tokens
    gpt4_tokens+=tokens

    return response

def final_output(final_response):
    prompt = ("Based on the following response, extract out only the improved " 
            "response and nothing else.  DO NOT include typical responses and "
            "the answer should only have the improved response: \n\n"
            f"{final_response}")
    
    messages = [{"role" : "user", "content" : prompt}]

    completion = openai.ChatCompletion.create(
        model = gpt3,
        messages=messages,
        temperature = temperature
    )

    response = completion.choices[0].message.content
    tokens = completion.usage.total_tokens
    print(response)
    print(tokens)
    global gpt3_tokens
    gpt3_tokens+=tokens

def concat_output(responses):
    '''
    Concatenate the initial outputs to label which answer they are
    '''
    answer_prompt = ""
    for i, response in enumerate(responses, start=1):
        answer_prompt += f"Answer Option {i}: {response}\n\n"

    return answer_prompt

def main():
    user_input = input("Question: ")
    # user_input = ("I left 5 clothes to dry out in the sun. " 
    #             "It took them 5 hours to dry completely. "
    #             "How long would it take to dry 30 clothes.")
    initial_responses, initial_prompt = initial_output(user_input)
    answer_list = concat_output(initial_responses)
    print("--------------------------------------------")
    researcher_response = researcher(answer_list, initial_prompt)
    print("--------------------------------------------")
    final_response = resolver(researcher_response)
    print("--------------------------------------------")
    final_output(final_response)

    # update tokens and calculate total cost
    global gpt3_tokens, gpt4_tokens
    total_calc = ((gpt3_tokens * rate_of_3) + (gpt4_tokens * rate_of_4))
    total_cost = f"${total_calc:.2f}"
    print(f"You used {gpt3_tokens} gpt3.5 tokens")
    print(f"You used {gpt4_tokens} gpt4 tokens")
    print(f"So this query cost you {total_cost}")


if __name__ == "__main__":
    main()

    
