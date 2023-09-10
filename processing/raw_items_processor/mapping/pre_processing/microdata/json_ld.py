from processing.raw_items_processor.mapping.pre_processing.microdata.utils import better_map


def _map_json_ld_product(microdata_item, extra_data):
    if extra_data is None:
        extra_data = {}

    def map_offer(offer):
        if offer is None:
            return {}
        offer_extra_data = offer.get('extra_data')
        if offer_extra_data is None:
            offer_extra_data = {}
        offer_extra_data = {
            **extra_data,
            **offer_extra_data
        }
        url = offer_extra_data.get('url')
        if url is None:
            url = better_map(offer.get('url'))
        price = offer_extra_data.get('price')
        if price is None:
            price = offer.get('price')

        return {
            "images": better_map([microdata_item.get('image'), offer.get('image')]),
            "url": url,
            "sku": better_map(offer.get('sku')),
            "availability": better_map(offer.get('availability')),
            "price": better_map(price),
            "list_price": better_map(offer.get('listPrice')),
            "price_currency": better_map(offer.get('priceCurrency')),
            "attributes": {
                "size": offer_extra_data.get('size'),
                "color": offer_extra_data.get('color'),
                "variant_labels": offer_extra_data.get('variant_labels'),
            }
        }
    offers = microdata_item.get('offers', [])
    if type(offers) is not list:
        offers = [offers]
    offers = list(map(map_offer, offers))

    return {
        "id": better_map(microdata_item.get('productID')),
        "name": better_map([microdata_item.get('name'), extra_data.get('name')]),
        "brand": better_map(microdata_item.get('brand')),
        "images": better_map(microdata_item.get('image')),
        "sku": better_map(microdata_item.get('sku')),
        "url": better_map([microdata_item.get('url'), extra_data.get('url')]),
        "offers": offers
    }


def map_json_ld(microdata, extra_data):
    item_type = microdata.get('@type')
    if item_type is None:
        return None

    product = None
    if item_type.lower() == 'product':
        product = _map_json_ld_product(microdata, extra_data)

    return product
