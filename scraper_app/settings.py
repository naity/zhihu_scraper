BOT_NAME = "zhihu"

SPIDER_MODULES = ["scraper_app.spiders"]

ITEM_PIPELINES = {
    "scraper_app.pipelines.ZhihuPipeline": 300
}

DOWNLOAD_HANDLERS = {'s3': None}

DOWNLOAD_DELAY = 1.5
