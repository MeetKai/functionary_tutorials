# Hotel Planning Chatbot with Functionary and external APIs

This module contains the code to run the simple hotel planning chatbot using Functionary and external APIs. The tutorial is provided [here](https://app.archbee.com/public/PREVIEW-hxp_DUA-ZUQ1iDZeDwYM9/PREVIEW-3l3pn7rtmGko_Wi_ZPRFR).

## Prerequisite

This module requires subscription for RapidAPI's *Hotels-com-provider* APIs. Please follow [this section of the tutorial](https://app.archbee.com/public/PREVIEW-hxp_DUA-ZUQ1iDZeDwYM9/PREVIEW-3l3pn7rtmGko_Wi_ZPRFR#2DYqV) to sign up for a RapidAPI account and to subscribe to the APIs.

## Installation and Get Started

1. Follow [Functionary's installation and set up](https://github.com/MeetKai/functionary?tab=readme-ov-file#setup) a vLLM server with any [Functionary model](https://huggingface.co/meetkai).
2. Install this module's dependencies
```shell
pip install -r requirements.txt
```
3. Export your RapidAPI API key as an environment variable.
```shell
export RAPIDAPI_KEY=your_rapidapi_key
```
4. Run the main script with the same model name as what you are using for the vLLM server.
```shell
python main.py model_name
```