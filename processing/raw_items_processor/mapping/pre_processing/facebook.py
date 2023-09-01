from processing.raw_items_processor.mapping.base import BaseItem


class FacebookPreProcessedItem(BaseItem):
    def __init__(self, id, text, post_text, time, timestamp, image_lowquality, images_lowquality, url, user_id, user_name, group_id, listing):
        self.id = id
        self.text = text
        self.post_text = post_text
        self.time = time
        self.timestamp = timestamp
        self.image_lowquality = image_lowquality
        self.images_lowquality = images_lowquality
        self.url = url
        self.user_id = user_id
        self.user_name = user_name
        self.group_id = group_id
        self.listing = listing

    def to_json(self):
        return {
            "id": self.id,
            "text": self.text,
            "post_text": self.post_text,
            "time": self.time,
            "timestamp": self.timestamp,
            "image_lowquality": self.image_lowquality,
            "images_lowquality": self.images_lowquality,
            "url": self.url,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "group_id": self.group_id,
            "listing": self.listing
        }

    @staticmethod
    def from_raw_item(crawled_item):
        return FacebookPreProcessedItem(
            id=crawled_item['post_id'],
            text=crawled_item['text'],
            post_text=crawled_item['post_text'],
            time=crawled_item['time'],
            timestamp=crawled_item['timestamp'],
            image_lowquality=crawled_item['image_lowquality'],
            images_lowquality=crawled_item['images_lowquality'],
            url=crawled_item['post_url'],
            user_id=crawled_item['user_id'],
            user_name=crawled_item['username'],
            group_id=crawled_item['group_id'],
            listing={
                "title": crawled_item['listing_title'],
                "price": crawled_item['listing_price'],
                "location": crawled_item['listing_location'],
            }
        )

    @staticmethod
    def from_json(json):
        return FacebookPreProcessedItem(
            id=json['id'],
            text=json['text'],
            post_text=json['post_text'],
            time=json['time'],
            timestamp=json['timestamp'],
            image_lowquality=json['image_lowquality'],
            images_lowquality=json['images_lowquality'],
            url=json['url'],
            user_id=json['user_id'],
            user_name=json['user_name'],
            group_id=json['group_id'],
            listing=json['listing']
        )
