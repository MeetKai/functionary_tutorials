import ast
import json
import os
import sys
from typing import Dict, List, Union

import fire
import requests
from openai import OpenAI
from termcolor import colored


def infer_model(messages: List[Dict], model: str):
    # Infer the model
    output = (
        llm_client.chat.completions.create(
            model=model, messages=messages, tools=tools, temperature=0.0
        )
        .choices[0]
        .message
    )

    # Postprocess model output
    if output.tool_calls is not None and len(output.tool_calls) > 0:
        fn_calls = []
        for tool_call in output.tool_calls:
            tool_call = tool_call.function.model_dump()
            tool_call["arguments"] = ast.literal_eval(tool_call["arguments"])
            fn_calls.append(tool_call)
        return fn_calls
    if output.function_call is not None:
        fn_calls = [output.function_call]
        return fn_calls

    return output.content


def call_hotels_com_provider_api(api_name: str, input_data: dict, rapidapi_key: str):
    urls = {
        "hotel_details": "https://hotels-com-provider.p.rapidapi.com/v2/hotels/details",
        "hotel_info": "https://hotels-com-provider.p.rapidapi.com/v2/hotels/info",
        "regions_search": "https://hotels-com-provider.p.rapidapi.com/v2/regions",
        "hotels_search": "https://hotels-com-provider.p.rapidapi.com/v2/hotels/search",
    }

    # Raise error if the api_name is not in urls
    assert api_name in urls, f"`api_name` is not a valid API name."

    # Add "domain" and "locale" into input_data if they are not present
    if "domain" not in input_data:
        input_data["domain"] = "US"
    if "locale" not in input_data:
        input_data["locale"] = "en_US"

    # Send the request and get the response
    url = urls[api_name]
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers, params=input_data)

    if response.status_code != 200:
        errors_json = json.loads(response.text)["detail"]
        errors_text = []
        if isinstance(errors_json, str):
            errors_text.append(errors_json)
        else:
            for error in errors_json:
                errors_text.append(f"{error['loc'][-1]}: {error['msg']}")
        return {"message": " | ".join(errors_text)}

    results = response.json()

    if api_name == "hotels_search":
        results = results["properties"]
        final_res = []
        for result in results:
            # Only append those that are available
            if result["availability"]["available"] is True:
                final_res.append(
                    {
                        "id": result["id"],
                        "name": result["name"],
                        "price_per_night": f"{result['price']['lead']['currencyInfo']['code']} {result['price']['lead']['currencyInfo']['symbol']}{result['price']['lead']['formatted']}",
                        "review_score": result["reviews"]["score"],
                        "hotel_id": result["id"],
                    }
                )
            # Just take top 5
            if len(final_res) == 5:
                break
        return final_res
    elif api_name == "regions_search":
        if results["data"][0]["@type"] == "gaiaRegionResult":
            return {"region_id": results["data"][0]["gaiaId"]}
        else:
            return {
                "hotel_id": results["data"][0]["hotelId"],
                "city_id": results["data"][0]["cityId"],
            }

    else:
        return {
            "hotel_info": results["propertyContentSectionGroups"]["aboutThisProperty"][
                "sections"
            ][0]["bodySubSections"][0]["elements"][0]["items"][0]["content"]["text"]
        }


def reset_messages(intro_msg: str):
    # Clear the previous conversation from the terminal
    os.system("cls" if os.name == "nt" else "clear")
    # Print the introductory messages
    print("===================")
    print("Welcome to the hotel planning chatbot program powered by Functionary.")
    print('Press ctrl+c anytime to stop. Enter "N" to start a new chat.')
    print("===================")

    return [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": intro_msg},
    ]


def get_user_input():
    user_input = input("> ")
    # Remove the printed user input from Terminal
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    return user_input


def print_message(message: Dict[str, str]):
    role_colors = {"user": "red", "assistant": "green", "tool": "blue"}

    if message["role"] == "tool":
        print(
            colored(f"{message['role'].upper()}", role_colors[message["role"]]),
            f": {message['name']} returned `{message['content']}`",
            sep="",
        )
    elif message["role"] == "assistant" and "name" in message:
        print(
            colored(f"{message['role'].upper()}", role_colors[message["role"]]),
            f": Calling `{message['name']}` with arguments `{message['content']}`",
            sep="",
        )
    else:
        print(
            colored(f"{message['role'].upper()}", role_colors[message["role"]]),
            f": {message['content']}",
            sep="",
        )


def execute_tools(
    messages: List[Dict[str, str]], model_output: Union[str, List], rapidapi_key: str
) -> List[Dict[str, str]]:
    if isinstance(model_output, str):
        messages.append({"role": "assistant", "content": model_output})
        print_message(message=messages[-1])
    else:
        for tool_call in model_output:
            messages.append(
                {
                    "role": "assistant",
                    "name": tool_call["name"],
                    "content": str(tool_call["arguments"]),
                }
            )
            print_message(message=messages[-1])
            fn_output = call_hotels_com_provider_api(
                api_name=tool_call["name"],
                input_data=tool_call["arguments"],
                rapidapi_key=rapidapi_key,
            )
            messages.append(
                {
                    "role": "tool",
                    "name": tool_call["name"],
                    "content": str(fn_output),
                }
            )
            print_message(message=messages[-1])
    return messages


def main(model: str):
    rapidapi_key = os.environ["RAPIDAPI_KEY"]

    intro_msg = "Welcome! I am a hotel planning bot for you! I can help you search for hotels and also find out hotels that you are interested in for you!"
    messages = reset_messages(intro_msg=intro_msg)
    print_message(message=messages[-1])

    while True:
        if messages[-1]["role"] != "tool":
            user_input = get_user_input()
            if user_input == "N":
                messages = reset_messages(intro_msg=intro_msg)
            else:
                messages.append({"role": "user", "content": user_input})
                print_message(message=messages[-1])
                output = infer_model(messages=messages, model=model)
                messages = execute_tools(
                    messages=messages, model_output=output, rapidapi_key=rapidapi_key
                )
        else:
            output = infer_model(messages=messages, model=model)
            messages = execute_tools(
                messages=messages, model_output=output, rapidapi_key=rapidapi_key
            )


if __name__ == "__main__":
    llm_client = OpenAI(base_url="http://localhost:8000/v1", api_key="functionary")
    with open("hotels_api_specification.json", "r") as file:
        tools = json.load(file)
    fire.Fire(main)
