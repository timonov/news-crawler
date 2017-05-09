# -*- coding: utf-8 -*-
import scrapy
import logging
import os


class NewsSpider(scrapy.Spider):
    name = 'reu'

    def __init__(self, years=None, months=None, days=None, tags=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)

        self.base_url = 'http://www.reuters.com/resources/archive/us/'
        self.years = ['2017'] if years is None else years.split(',')            # 2016,2015
        self.months = ['03'] if months is None else months.split(',')           # 01,02, .., 12
        self.days = [['27', '29']] if days is None else self.prepare(days)      # [[st_day, e_day],[st_day, edn_day],..]
        self.tags = ['climate', 'park'] if tags is None else tags.split(',')  # key-word in title

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
                        info = {'date': date}
                        yield scrapy.Request(url=response.urljoin(day_url), callback=self.parse_day,
                                             meta={'info': info})
            else:
                empty_request = True
                continue
        if empty_request and not do_request:
            logging.warning('Check parameters, please')

    def parse_day(self, response):
        info = response.meta['info']
        items = response.xpath("//div/a[starts-with(@href, 'http://www.reuters.com/article/')]")
        for item in items:
            title, link = item.xpath('text()').extract_first(), item.xpath('@href').extract_first()
            for tag in self.tags:
                if tag in title:
                    info['title'], info['link'] = title, link
                    yield scrapy.Request(url=response.urljoin(link), callback=self.parse_article, meta={'info': info})

    def parse_article(self, response):
        n_info = response.meta['info']
        n_info['title'], n_info['link'] = response.meta['info']['title'], response.url
        n_info['section'] = response.xpath("//span[@class='article-section']/a/text()").extract_first().\
            replace(" ", "_")
        n_info['text'] = response.xpath("//*[@id='article-text']/p/text()").extract()
        self.save_in_file(n_info)

    @staticmethod
    def save_in_file(_item):
        path = os.path.join(os.getcwd())
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, 'res' + '.txt'), 'a') as out_file:
            out_file.write('date: ' + _item['date'] + '\n')
            out_file.write('title: ' + _item['title'] + '\n')
            out_file.write('text: ' + u''.join(_item['text']).encode('utf-8').strip() + '\n')
            out_file.write('section: ' + _item['section'] + '\n')
            out_file.write('link: ' + _item['link'] + '\n\n')
            out_file.close()

    @staticmethod
    def prepare(_days):
        s = _days.split(';')
        return [x.split(',') for x in s]
