import scrapy
import json

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from mercado.items import MercadoItem

class MercadoSpider(CrawlSpider):
	name = 'mercado'
	item_count = 0 #inicializo mi contador para solo extraer el numero de datos que quiero
	allowed_domain = ['www.mercadolibre.com.pe'] #pagina de mercado libre PERÚ
	start_urls = ['https://listado.mercadolibre.com.pe/impresoras']
	
	#crear un user_agent para evitar el "error 403: el código de estado HTTP no se maneja o no se permite en scrapy"
	user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

	#parte de robotstxt
	custom_settings = {
        'ROBOTSTXT_OBEY': True,
    	}

	rules = {
		# Para cada item(uno para el sig pagina, y el otro, para entrar a cada producto)
		Rule(LinkExtractor(allow = (), restrict_xpaths = ('//li[@class="andes-pagination__button andes-pagination__button--next shops__pagination-button"]/a'))),
		Rule(LinkExtractor(allow =(), restrict_xpaths = ('//div[contains(@class,"ui-search-item__group ui-search-item__group--title shops__items-group")]')),
							callback = 'parse_item', follow = False)
	}

	def parse_item(self, response):
		ml_item = MercadoItem()

		#info de producto
		ml_item['titulo'] = response.xpath('normalize-space(//h1[@class="ui-pdp-title"]/text())').extract_first()
		ml_item['precio'] = response.xpath('normalize-space(//span[@class="andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact"]/meta/@content)').extract()
		ml_item['condicion'] = response.xpath('normalize-space(//div[@class="ui-pdp-header__subtitle"]/span[@class="ui-pdp-subtitle"]/text())').extract()
		ml_item['envio'] = response.xpath('normalize-space(//p[@class="ui-pdp-color--BLACK ui-pdp-family--REGULAR ui-pdp-media__title"]/span/text())').extract()
		ml_item['cantidad'] = response.xpath('//span[@class="ui-pdp-buybox__quantity__available"]/text()').extract()
		ml_item['opiniones'] = response.xpath('normalize-space(//div/p[@class="ui-review-capability__rating__average ui-review-capability__rating__average--desktop"]/text())').extract()
		
		#imagenes del producto
		#ml_item['image_urls'] = response.xpath('//*[@id="gallery"]/div/div[2]/span[1]/figure/img/@src').extract()
		#ml_item['image_name'] = response.xpath('normalize-space(//*[@id="gallery"]/div/div[2]/span[1]/figure/img/@alt)').extract_first()
		
		#info de la tienda o vendedor
		ml_item['vendedor_url'] = response.xpath('//div[@class="ui-box-component ui-box-component-pdp__visible--desktop"]/a/@href').extract()
		ml_item['atencion_vendedor'] = response.xpath('normalize-space(//li[@class="ui-pdp-seller__item-description"][2]/p[@class="ui-pdp-seller__text-description"]/text())').extract()
		ml_item['ventas_vendedor'] = response.xpath('normalize-space(//li[@class="ui-pdp-seller__item-description"]/strong/text())').extract()
		
		self.item_count += 1
		
		if self.item_count > 5: #para extraer los datos que quiero (limitador)
			raise CloseSpider('item_exceeded')
		yield ml_item