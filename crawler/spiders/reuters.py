import scrapy
import logging
import os


class NewsSpider(scrapy.Spider):
    name = 'reu'

    def __init__(self, years=None, months=None, days=None, tags=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)

        self.base_url = 'http://www.reuters.com/resources/archive/us/'
        self.years = ['2017'] if years is None else years           # 2016,2015
        self.months = ['03', '04'] if months is None else months    # 01,02, .., 12
        self.days = [['26', '29']] if days is None else days        # [[start_day, end_day], [start_day, end_day], ...]
        #self.tags = ['cyber', 'security'] if tags is None else tags  # key-word in title
        self.tags = ['tech', 'self-driving car'] if tags is None else tags  # key-word in title

    def start_requests(self):
        for year in self.years:
            yield scrapy.Request(url=self.base_url+str(year)+'.html', callback=self.parse_year)

    def parse_year(self, response):
        empty_request, do_request = False, False
        all_days = response.xpath("//p/a[starts-with(@href, '/resources/archive/us/')]")
        for day in all_days:
            day_url = day.xpath('@href').extract_first()
            date = day_url.split('/')[-1][:-5]
            if date[4:-2] in self.months:
                for my_day in self.days:
                    start_day, end_day = my_day[0], my_day[1]
                    empty_request, do_request = False, True
                    if start_day <= date[6:] <= end_day:
                        item = {'date': date}
                        yield scrapy.Request(url=response.urljoin(day_url), callback=self.parse_day,
                                             meta={'item': item})
            else:
                empty_request = True
                continue
        if empty_request and not do_request:
            logging.warning('Check parameters, please')

    def parse_day(self, response):
        items = response.xpath("//div/a[starts-with(@href, 'http://www.reuters.com/article/')]")
        for item in items:
            item_link = item.xpath('@href').extract_first()
            item_title = item.xpath('text()').extract_first()
            for tag in self.tags:
                if tag in item_title:
                    item = response.meta['item']
                    item['title'], item['link'] = item_title, item_link
                    yield scrapy.Request(url=response.urljoin(item_link), callback=self.parse_article,
                                         meta={'item': item})

    def parse_article(self, response):
        def save_in_file():
            path = os.path.join(os.getcwd(), 'files')
            if not os.path.exists(path):
                os.makedirs(path)
            with open(os.path.join(path, item['date'] + '.txt'), 'a') as out_file:
                out_file.write('date: ' + item['date'] + '\n')
                out_file.write('title: ' + item['title'] + '\n')
                out_file.write('text: ' + u''.join(item['text']).encode('utf-8').strip() + '\n')
                out_file.write('section: ' + item['section'] + '\n')
                out_file.write('link: ' + item['link'] + '\n\n')

        item = response.meta['item']
        item['section'] = response.xpath("//span[@class='article-section']/a/text()").extract_first().replace(' ', '_')
        item['text'] = response.xpath("//*[@id='article-text']/p/text()").extract()
        save_in_file()
