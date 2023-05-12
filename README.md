# SmartGPT
An implemetation of "SmartGPT" as proposed by AI explained in this video: https://www.youtube.com/watch?v=wVzuvf9D9BU&t=434s

## Features:
✔️ The ability to use different models for each part of the way is available (You can use gpt3.5 and 4)

✔️ Offers the ability to change the # of outputs produced initially for the question

✔️ Automatically saves the messages after the script finishes


## To run this
Clone the repository:

```git clone https://github.com/JarodMica/SmartGPT.git```

Navigate into the repository folder and then set up the needed libraries. I recommend that you use a venv to do so and then run:

```pip install requirements.txt```

Setup your openai key in ```keys.yaml.example```. You will have to change the name to ```keys.yaml``` in order for this to work.
As well, you will need to enter your own API key which can be found on openai's website @https://platform.openai.com/overview

Once you have everything set-up, navigate to the folder in CMD and then run the script with:

```python smartGPT.py```

If you're using an IDE, run it as you would normally (debug).  If you're using a venv, make sure you have actually activated it as well!

## Some things to note
- [ ] Exact implementation may differ than that of what was discussed in Phillip's video.
- [ ] Credit to this exact implementation goes to Phillip

