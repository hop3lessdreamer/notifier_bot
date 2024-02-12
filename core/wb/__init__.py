""" Init wb package """


def form_url_from_product_id(product_id: int | str) -> str:
    if not product_id:
        return ''
    return f'https://www.wildberries.ru/catalog/{str(product_id)}/detail.aspx'
