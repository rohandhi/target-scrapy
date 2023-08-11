import re
import logging
import scrapy


logger = logging.getLogger()


class TargetSpider(scrapy.Spider):
    """
    @rohangandhi
    """
    name = 'target'
    
    def start_requests(self):
        url = getattr(self, 'url', None)
        if url is not None:
            yield scrapy.Request(url, self.parse)
        else:
            self.logger.error("Please provide a valid URL using the 'url' argument.")
    
    def parse(self, response):
        specs_bullet = response.xpath('//div[@data-test="item-details-specifications"]//div//b/text()').getall()
        specs_value = list(filter(lambda x: x.strip() not in ["", ":"], response.xpath('//div[@data-test="item-details-specifications"]//div[not(self::a)]/text()').getall()))
        pattern = r'\\\"current_retail\\\":([\d,\.]+)'
        data_script = response.xpath('//script[contains(text(), "deepFreeze")]//text()').get()
        match = re.search(pattern, data_script)
        product_info = {
            'url': response.xpath('//meta[@property="og:url"]//@content').get(),
            'tcin': response.xpath('//b[contains(text(), "TCIN")]//parent::div//text()[2]').get(),
            "upc": response.xpath('//b[contains(text(), "UPC")]//parent::div//text()[2]').get(), 
            "price_amount": float(match.group(1).replace(',', '')) if match else None,
            "currency": "USD",
            "description": response.xpath('//meta[@name="description"]//@content').get(), 
            "specs": None,
            "ingredients": [], 
            "bullets": response.xpath('//ul//li[contains(@class, "styles__Bullet")]//text()').getall(), 
            "features": [f"{item1.strip().replace(':', '')}: {item2.strip()}" for item1, item2 in zip(specs_bullet, specs_value)]
        }
        
        yield product_info