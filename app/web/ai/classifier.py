import json
from json import JSONDecodeError
from typing import Dict

import backoff
import openai

from web.ai.prompts import CLASSIFY_CATEGORIES
from web.logger import get_logger

logger = get_logger(__name__)


@backoff.on_exception(
    backoff.expo, (openai.error.Timeout, openai.error.APIError), max_tries=10
)
async def chat_completion(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.0,
    frequency_penalty: float = -0.5,
):
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        frequency_penalty=frequency_penalty,
    )
    return response.get("choices")[0].get("message").get("content")


async def classify_product_category(
    product_name: str, product_description: str
) -> Dict[str, str]:
    prompt = CLASSIFY_CATEGORIES + "\n".join([product_name, product_description])
    try:
        return json.loads(await chat_completion(prompt))
    except (JSONDecodeError, TypeError) as e:
        logger.error(e)
        return {}
