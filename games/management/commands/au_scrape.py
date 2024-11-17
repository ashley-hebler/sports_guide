import scrapy

class AUSpider(scrapy.Spider):
    print("Scraping AU Sports")
    name = "sports_softball_au"
    start_urls = [
        'https://auprosports.com/softball/schedule/2024/wk1-g1/',
        'https://auprosports.com/softball/schedule/2024/wk1-g2/',
        'https://auprosports.com/softball/schedule/2024/wk1-g3/',
        'https://auprosports.com/softball/schedule/2024/wk1-g4/',
        'https://auprosports.com/softball/schedule/2024/wk1-g5/',
        'https://auprosports.com/softball/schedule/2024/wk1-g6/',
        'https://auprosports.com/softball/schedule/2024/wk2-g7/',
        'https://auprosports.com/softball/schedule/2024/wk2-g8/',
        'https://auprosports.com/softball/schedule/2024/wk2-g9/',
        'https://auprosports.com/softball/schedule/2024/wk2-g10/',
        'https://auprosports.com/softball/schedule/2024/wk2-g11/',
        'https://auprosports.com/softball/schedule/2024/wk2-g12/',
        'https://auprosports.com/softball/schedule/2024/wk3-g13/',
        'https://auprosports.com/softball/schedule/2024/wk3-g14/',
        'https://auprosports.com/softball/schedule/2024/wk3-g15/',
        'https://auprosports.com/softball/schedule/2024/wk3-g16/',
        'https://auprosports.com/softball/schedule/2024/wk3-g17/',
        'https://auprosports.com/softball/schedule/2024/wk3-g18/',
        'https://auprosports.com/softball/schedule/2024/wk4-g19/',
        'https://auprosports.com/softball/schedule/2024/wk4-g20/',
        'https://auprosports.com/softball/schedule/2024/wk4-g21/',
        'https://auprosports.com/softball/schedule/2024/wk4-g22/',
        'https://auprosports.com/softball/schedule/2024/wk4-g23/',
        'https://auprosports.com/softball/schedule/2024/wk4-g24/',
        'https://auprosports.com/softball/schedule/2024/wk5-g25/',
        'https://auprosports.com/softball/schedule/2024/wk5-g26/',
        'https://auprosports.com/softball/schedule/2024/wk5-g27/',
        'https://auprosports.com/softball/schedule/2024/wk5-g28/',
        'https://auprosports.com/softball/schedule/2024/wk5-g29/',
        'https://auprosports.com/softball/schedule/2024/wk5-g30/',
    ]

    def parse(self, response):
        for quote in response.css("main"):
            yield {
                "date": quote.css(".text-base-24>span").attrib["data-time"],
                "network": quote.css(".hero-b__links>p>a::text").get(),
                'link': quote.css(".hero-b__links>p>a::attr(href)").get(),
                "name": quote.css("h1::text").get(),
            }