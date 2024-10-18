from abc import abstractmethod

from processing.raw_items_processor.mapping.base import BaseItem
from processing.raw_items_processor.mapping.entitites.price import GustmarketPrice


class PreProcessedProductVariant:
    price: GustmarketPrice

    #todo: maybe directly map attributes instead of size, color and create KiteAttributes, BoardAttributes, etc..
    #todo: sku
    def __init__(self, id, url, price, in_stock, images, name, name_variants, attributes):
        self.id = id
        self.url = url
        self.price = price
        self.in_stock = in_stock
        self.images = images
        self.name = name
        self.name_variants = name_variants
        self.attributes = attributes

    def __str__(self):
        return f"PreProcessedProductVariant({self.id}, {self.url}, {self.price}, {self.in_stock}, {self.name}, {self.attributes})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id and self.price == other.price and self.name == other.name

    def __hash__(self):
        return hash((self.id, self.price, self.name, self.attributes))

    def to_json(self):
        return {
            "id": self.id,
            "url": self.url,
            "price": self.price.to_json() if self.price is not None else None,
            "in_stock": self.in_stock,
            "images": self.images,
            "name": self.name,
            "name_variants": self.name_variants,
            "attributes": self.attributes,
        }

    @staticmethod
    def from_json(json):
        return PreProcessedProductVariant(
            id=json.get('id'),
            url=json.get('url'),
            price=GustmarketPrice.from_json(json.get('price')),
            in_stock=json['in_stock'],
            images=json.get('images'),
            name=json.get('name'),
            name_variants=json.get('name_variants', []),
            attributes=json['attributes'],
        )


class PreProcessedProduct(BaseItem):
    id: str
    name: str
    name_variants: [str]
    url: str
    brand: str
    category: str
    condition: str
    scraped_category: str
    scraped_condition: str
    variants: [PreProcessedProductVariant]
    images: [str]

    def __init__(self, id, name, name_variants, url, brand, category, condition, scraped_category, scraped_condition, variants, images):
        self.id = id
        self.name = name
        self.name_variants = name_variants
        self.url = url
        self.brand = brand
        self.category = category
        self.condition = condition
        self.scraped_category = scraped_category
        self.scraped_condition = scraped_condition
        self.variants = variants
        self.images = images

    def __str__(self):
        return f"PreProcessedItem({self.id}, {self.name}, {self.brand}, {self.category}, {self.condition}, {self.scraped_category}, {self.scraped_condition}, {self.variants}, {self.images})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.brand == other.brand and self.category == other.category and self.scraped_category == other.scraped_category and self.scraped_condition == other.scraped_condition

    def __hash__(self):
        return hash((self.id, self.name, self.brand, self.category, self.variants, self.images))

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "name_variants": self.name_variants,
            "brand": self.brand,
            "url": self.url,
            "category": self.category,
            "condition": self.condition,
            "scraped_category": self.scraped_category,
            "scraped_condition": self.scraped_condition,
            "variants": list(map(lambda v: v.to_json(), self.variants)),
            "images": self.images,
        }

    @staticmethod
    def from_json(json):
        return PreProcessedProduct(
            id=json['id'],
            url=json['url'],
            name=json['name'],
            name_variants=json.get('name_variants', []),
            brand=json['brand'],
            condition=json.get('condition'),
            category=json.get('category'),
            scraped_category=json.get('scraped_category'),
            scraped_condition=json.get('scraped_condition'),
            variants=list(map(PreProcessedProductVariant.from_json, json['variants'])),
            images=json.get('images'),
        )


class PreProcessedProductImpl(PreProcessedProduct):

    @staticmethod
    @abstractmethod
    def from_raw_item(self):
        pass
