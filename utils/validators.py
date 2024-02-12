""" Validators """

import re
from typing import Optional

from utils.transform_types import get_int


url_parse = re.compile(r'(http[s]?:\/\/)?([^\/\s]+\/)(catalog)\/(\d+)')  # product_id is 4 group


def validate_product_id(message: str) -> Optional[int]:
    """ Returns product id from user message to bot """

    #   message contain only product_id
    product_id = get_int(message)
    if product_id:
        return product_id

    # check product_id in url
    matching: Optional[re.Match] = re.match(url_parse, message)
    if matching:
        product_id: Optional[int] = matching.group(4)

    return get_int(product_id)

