from processing.raw_items_processor.mapping.base import BaseItem
from processing.raw_items_processor.mapping.entitites.price import GustmarketPrice


class NormalizedItemVariant(BaseItem):
    price: GustmarketPrice

    def __init__(self, price, in_stock, images, name, size, color, url):
        self.price = price
        self.in_stock = in_stock
        self.images = images
        self.name = name
        self.size = size
        self.color = color
        self.url = url

    def __str__(self):
        return f"NormalizedItemVariant({self.price}, {self.in_stock}, {self.images}, {self.size}, {self.color}, {self.url})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.price == other.price and self.name == other.name and self.size == other.size and self.color == other.color

    def __hash__(self):
        return hash((self.price, self.name, self.size, self.color))

    @property
    def get_price(self):
        return self.price

    def to_json(self):
        return {
            "price": self.price.to_json() if self.price is not None else None,
            "in_stock": self.in_stock,
            "images": self.images,
            "name": self.name,
            "size": self.size,
            "color": self.color,
            "url": self.url,
        }

    @staticmethod
    def from_json(json):
        return NormalizedItemVariant(
            price=GustmarketPrice.from_json(json['price']),
            in_stock=json['in_stock'],
            images=json['images'],
            name=json['name'],
            size=json['size'],
            color=json['color'],
            url=json['url'],
        )

class NormalizedItem(BaseItem):
    id: str
    internal_sku: str
    name: str
    raw_name: str
    url: str
    brand: str
    brand_slug: str
    category: str
    condition: str
    variants: [NormalizedItemVariant]
    images: [str]
    attributes: dict

    def __init__(self, id, is_standardised, url, internal_sku, name, unique_model_identifier,raw_name,brand, brand_slug, condition, category, variants, images, attributes):
        self.id = id
        self.is_standardised = is_standardised
        self.url = url
        self.internal_sku = internal_sku
        self.name = name
        self.unique_model_identifier = unique_model_identifier
        self.raw_name = raw_name
        self.brand = brand
        self.brand_slug = brand_slug
        self.condition = condition
        self.category = category
        self.variants = variants
        self.images = images
        self.attributes = attributes

    def __str__(self):
        return f"KiteItem({self.id}, {self.internal_sku}, {self.name}, {self.brand}, {self.attributes}, {self.brand_slug}, {self.condition}, {self.category}, {self.variants}, {self.images})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id and self.internal_sku == other.internal_sku and self.condition == other.condition and self.name == other.name and self.brand_slug == other.brand_slug and self.category == other.category

    def __hash__(self):
        return hash((self.id, self.internal_sku, self.name, self.brand_slug, self.attributes, self.condition, self.category))

    def to_json(self):
        return {
            "id": self.id,
            "is_standardised": self.is_standardised,
            "url": self.url,
            "internal_sku": self.internal_sku,
            "name": self.name,
            "unique_model_identifier": self.unique_model_identifier,
            "raw_name": self.raw_name,
            "brand": self.brand,
            "brand_slug": self.brand_slug,
            "attributes": self.attributes,
            "condition": self.condition,
            "category": self.category,
            "variants": list(map(lambda v: v.to_json(), self.variants)),
            "images": self.images,
        }

    @staticmethod
    def from_json(json):
        return NormalizedItem(
            id=json['id'],
            is_standardised=json['is_standardised'],
            url=json['url'],
            internal_sku=json['internal_sku'],
            name=json['name'],
            unique_model_identifier=json.get('unique_model_identifier'),
            raw_name=json.get('raw_name'),
            brand=json['brand'],
            brand_slug=json['brand_slug'],
            attributes=json['attributes'],
            category=json['category'],
            condition=json['condition'],
            variants=list(map(NormalizedItemVariant.from_json, json['variants'])),
            images=json['images'],
        )
