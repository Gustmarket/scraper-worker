from processing.raw_items_processor.mapping.pre_processing.microdata.utils import better_map
from processing.raw_items_processor.mapping.utils import flatten_list, uniq_filter_none


def _map_microdata_product(microdata_item, extra_data):
    if extra_data is None:
        extra_data = {}
    properties = microdata_item.get('properties')

    def map_offer(offer):
        if offer is None:
            return {}
        offer_properties = offer.get('properties')
        url = extra_data.get('url')
        if url is None:
            url = better_map(offer_properties.get('url'))
        price = extra_data.get('price')
        if price is None:
            price = offer_properties.get('price')


        # todo: fix this for coronation
        availability = extra_data.get('availability')
        if availability is not None:
            if 'not in stock' in availability.lower() or 'no longer in stock' in availability.lower():
                availability = 'OutOfStock'
            else:
                availability = None
        if availability is None:
            availability = better_map(offer_properties.get('availability'))

        return {
            "images": better_map(properties.get('image')), #todo: get offer image if exists?
            "url": url,
            "sku": better_map(offer_properties.get('sku')),
            "availability": availability,
            "price": better_map(price),
            "list_price": better_map(offer_properties.get('listPrice')),
            "price_currency": better_map(offer_properties.get('priceCurrency')),
            "attributes": {
                "size": extra_data.get('size'),
                "color": extra_data.get('color'),
                "variant_labels": extra_data.get('variant_labels'),
            }
        }

    offers = properties.get('offers', [])
    if type(offers) is not list:
        offers = [offers]
    offers = list(map(map_offer, offers))

    return {
        "id": better_map(properties.get('productID')),
        "name": better_map([properties.get('name'), extra_data.get('name')]),
        "brand": better_map(properties.get('brand')),
        "images": better_map(properties.get('image')),
        "sku": better_map(properties.get('sku')),
        "url": better_map([properties.get('url'), extra_data.get('url')]),
        "offers": offers
    }


def _map_microdata_item_page(microdata_item, extra_data):
    if extra_data is None:
        extra_data = {}
    properties = microdata_item.get('properties')
    main_entity = properties.get('mainEntity')

    return _map_microdata_product(main_entity, extra_data)


def map_image_gallery(all_microdata):
    image_gallery = list(filter(lambda x: 'ImageGallery' in x.get('type', ''), all_microdata))
    if len(image_gallery) == 0:
        return []

    def extract_images(image_gallery_item):
        media = image_gallery_item.get('properties', {}).get('associatedMedia', [])
        if media is None:
            return []

        if type(media) is not list:
            media = [media]

        if len(media) == 0:
            return []

        def get_image(media_node):
            return media_node.get('properties', {}).get('contentUrl')

        return list(map(get_image, media))

    return uniq_filter_none(flatten_list(list(map(extract_images, image_gallery))))


def map_microdata(microdata, extra_data, all_microdata):
    item_type = microdata.get('type')
    if item_type is None:
        return None

    product = None
    if 'Product' in item_type:
        product = _map_microdata_product(microdata, extra_data)
    if 'ItemPage' in item_type:
        product = _map_microdata_item_page(microdata, extra_data)

    if product is not None:
        if product.get('images') is None or len(product.get('images')) == 0:
            product['images'] = uniq_filter_none(map_image_gallery(all_microdata))

    return product
