import json
from json import JSONDecodeError
from typing import Dict, Optional

import backoff
import openai
from openai import APIError, APITimeoutError, RateLimitError, AsyncOpenAI

from web.ai.prompts import CLASSIFY_CATEGORIES
from web.logger import get_logger

logger = get_logger(__name__)

client = AsyncOpenAI()


@backoff.on_exception(
    backoff.expo,
    (APITimeoutError, APIError, RateLimitError),
    max_tries=10,
)
async def chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-3.5-turbo",
):
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=1,
        frequency_penalty=0,
    )
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    logger.info(
        f"OpenAI approximate cost "
        f"${(input_tokens / 1000 * 0.0015) + (output_tokens / 1000 * 0.002)}"
    )
    output = response.choices[0].message.content
    logger.debug(f"AI response {output}")
    return output


async def classify_product_category(product_name: str) -> Optional[Dict[str, str]]:
    try:
        return json.loads(
            await chat_completion(
                CLASSIFY_CATEGORIES,
                f'"{product_name}"',
            )
        )
    except (JSONDecodeError, TypeError) as e:
        logger.error(e)
