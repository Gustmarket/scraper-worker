from abc import abstractmethod

from processing.data.cleanup import replace_string_word_ignore_case
from processing.data.utils import uniq_filter_none, flatten_list
from processing.interfaces import BaseItem
from processing.entitites.price import GustmarketPrice


class PreProcessedItemVariant:
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
        return PreProcessedItemVariant(
            id=json.get('id'),
            url=json.get('url'),
            price=GustmarketPrice.from_json(json.get('price')),
            in_stock=json['in_stock'],
            images=json.get('images'),
            name=json.get('name'),
            name_variants=json.get('name_variants', []),
            attributes=json['attributes'],
        )


class PreProcessedItem(BaseItem):
    id: str
    name: str
    name_variants: [str]
    url: str
    brand: str
    category: str
    subcategories: [str]
    condition: str
    variants: [PreProcessedItemVariant]
    images: [str]

    def __init__(self, id, name, name_variants, url, brand, category, subcategories, condition, variants, images):
        self.id = id
        self.name = name
        self.name_variants = name_variants
        self.url = url
        self.brand = brand
        self.category = category
        self.subcategories = subcategories
        self.condition = condition
        self.variants = variants
        self.images = images

    def __str__(self):
        return f"PreProcessedItem({self.id}, {self.name}, {self.brand}, {self.category}, {self.subcategories}, {self.condition}, {self.variants}, {self.images})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.brand == other.brand and self.category == other.category

    def __hash__(self):
        return hash((self.id, self.name, self.brand, self.category, self.variants, self.images))

    def get_all_variant_labels(self):
        all_variant_labels = uniq_filter_none(
            flatten_list(list(map(lambda kv: kv.attributes.get('variant_labels', []), self.variants))))
        all_variant_labels = uniq_filter_none(
            flatten_list(list(map(lambda x: x.split(' '), all_variant_labels))))
        return all_variant_labels

    def get_all_cleaned_name_variants(self):
        all_variant_labels = self.get_all_variant_labels()
        variant_name_variants = uniq_filter_none(
            flatten_list([v.name_variants for v in self.variants if hasattr(v, 'name_variants')]))
        variant_names = [v.name for v in self.variants if v.name]

        all_variants = (
            [self.name] +
            self.name_variants +
            variant_name_variants +
            variant_names +
            all_variant_labels
        )

        cleaned_variants = []
        for variant in all_variants:
            cleaned_variant = variant
            for variant_label in all_variant_labels:
                cleaned_variant = replace_string_word_ignore_case(cleaned_variant, variant_label, '')
            cleaned_variants.append(cleaned_variant.strip())

        all_variants = cleaned_variants

        return uniq_filter_none(all_variants)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "name_variants": self.name_variants,
            "brand": self.brand,
            "url": self.url,
            "category": self.category,
            "subcategories": self.subcategories,
            "condition": self.condition,
            "variants": list(map(lambda v: v.to_json(), self.variants)),
            "images": self.images,
        }

    @staticmethod
    def from_json(json):
        return PreProcessedItem(
            id=json['id'],
            url=json['url'],
            name=json['name'],
            name_variants=json.get('name_variants', []),
            brand=json['brand'],
            condition=json.get('condition'),
            category=json.get('category'),
            subcategories=json.get('subcategories'),
            variants=list(map(PreProcessedItemVariant.from_json, json['variants'])),
            images=json.get('images'),
        )


class PreProcessedItemImpl(PreProcessedItem):

    @staticmethod
    @abstractmethod
    def from_raw_item(self):
        pass
