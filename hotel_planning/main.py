import os
from typing import Dict, List

import requests
from openai import OpenAI


def infer_model(messages: List[Dict], model: str):
    output = openai_client.chat.completions.create(
        model=model, messages=messages, tools=tools, temperature=0.0
    )


def call_hotels_com_provider_api(api_name: str, input_data: dict, rapidapi_key: str):
    urls = {
        "hotel_details": "https://hotels-com-provider.p.rapidapi.com/v2/hotels/details",
        "hotel_info": "https://hotels-com-provider.p.rapidapi.com/v2/hotels/info",
        "regions_search": "https://hotels-com-provider.p.rapidapi.com/v2/regions",
        "hotels_search": "https://hotels-com-provider.p.rapidapi.com/v2/hotels/search",
    }

    if urls.get(api_name):
        url = urls[api_name]
    else:
        print(f"Invalid API Name: `{api_name}`")
        return None

    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=input_data)

    if response.status_code != 200:
        print(
            f"API call error: code-> {response.status_code} | message: {response.text}"
        )
        return None

    results = response.json()

    breakpoint()

    if api_name == "hotels_search":
        results = results["properties"]
        final_res = []
        for result in results:
            final_res.append(
                {
                    "id": result["id"],
                    "name": result["name"],
                }
            )
        return final_res
    elif api_name == "regions_search":
        region_id = results["data"][0]["gaiaId"]
        return {"region_id": region_id}


if __name__ == "__main__":
    rapidapi_key = os.environ["RAPIDAPI_KEY"]
    openai_client = OpenAI(base_url="http://localhost:8000/v1", api_key="functionary")

    query = "What hotels in Singapore are available today and checking out tomorrow?"

    input_data = {"query": "Singapore", "domain": "US", "locale": "en_US"}

    response = call_hotels_com_provider_api(
        api_name="regions_search", input_data=input_data, rapidapi_key=rapidapi_key
    )

    input_data = {
        "region_id": "2872",
        "locale": "en_GB",
        "checkin_date": "2024-09-26",
        "sort_order": "REVIEW",
        "adults_number": "1",
        "domain": "AE",
        "checkout_date": "2024-09-27",
    }

    call_hotels_com_provider_api(
        api_name="hotels_search", input_data=input_data, rapidapi_key=rapidapi_key
    )
