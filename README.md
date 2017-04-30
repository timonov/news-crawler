**#Simple news crawler**

News' crawler, which provide information from [news portal](http://www.reuters.com/) in the specified period (years, months, days). \
News can also be selected by tag, if tag was specified (-a option). \
Crawled articles save into $ROOT_FOLDER/files/$DATE.txt. \
Used Python 2.7 and Scrapy framework.

Usage:
 - install Scrapy 1.3.3 (pip install scrapy)
 - install Microsoft Visual C++ Compiler for Python 2.7 (if needed)
 - cd  my_crawler
 - scrapy crawl reu -a months=['02','03','04'] -a tags=['Technology', 'Data Mining']

 Other option:
  - -a years=['2017'] (['2017','2016'])
  - -a days=[['01', '07'],['20', '26']] ([[start_day, end_day], [start_day, end_day], ...])


Usefull links:
 - [Scrapy Tutorial](https://doc.scrapy.org/en/latest/intro/tutorial.html)
