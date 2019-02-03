import websockets
from scrapy.http import HtmlResponse
from logging import getLogger
import asyncio
import pyppeteer
import logging
from concurrent.futures._base import TimeoutError

pyppeteer_level = logging.WARNING
logging.getLogger('websockets.protocol').setLevel(pyppeteer_level)
logging.getLogger('pyppeteer').setLevel(pyppeteer_level)


class PyppeteerMiddleware:
    def __init__(self, **args):
        """
        init logger, loop, browser
        :param args:
        """
        self.logger = getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.browser = self.loop.run_until_complete(
            pyppeteer.launch(headless=True))
        self.args = args

    def __del__(self):
        """
        close loop
        :return:
        """
        self.loop.close()

    def render(self, url, script, scrolldown):
        """
        render page with pyppeteer
        :param url: page url
        :param retries: max retry times
        :param script: js script to evaluate
        :param wait: number of seconds to wait after execute script or scrolldown
        :param scrolldown: how many times to page down
        :param timeout: the longest wait time, otherwise raise timeout error
        :param browser: pyppetter browser object
        :return: content, result, status
        """

        # define async render
        retries = self.args.get('retry') or 1
        wait = self.args.get('wait') or 0.3
        timeout = self.args.get('timeout') or 8.0

        async def async_render(url, script, scrolldown, wait, timeout):
            try:
                # basic render
                page = await self.browser.newPage()
                await asyncio.sleep(0.3)
                response = await page.goto(url, options={'timeout': int(timeout * 1000)})
                if response.status != 200:
                    return None, None, response.status

                # evaluate with script and get the execute result
                result = None
                if script:
                    result = await page.evaluate(script)
                    await asyncio.sleep(wait)

                # scroll down for {scrolldown} times
                if scrolldown:
                    for _ in range(scrolldown):
                        await page._keyboard.down('PageDown')
                        await asyncio.sleep(wait)

                # get html of page
                content = await page.content()
                return content, result, response.status

            except TimeoutError:
                self.logger.warning('Time out when rendering %s' % url)
                return None, None, 500
            finally:
                await page.close()

        content, result, status = [None] * 3

        # retry for {retries} times
        for i in range(retries):
            if not content:
                content, result, status = self.loop.run_until_complete(
                    async_render(url=url, script=script, wait=wait,
                                 scrolldown=scrolldown, timeout=timeout))
            else:
                break

        # if need to return js evaluation result
        return content, result, status

    def process_request(self, request, spider):
        """
        :param request: request object
        :param spider: spider object
        :return: HtmlResponse
        """
        if request.meta.get('render'):
            try:
                self.logger.debug('rendering %s', request.url)
                html, result, status = self.render(request.url)
                return HtmlResponse(url=request.url, body=html, request=request, encoding='utf-8',
                                    status=status)
            except websockets.exceptions.ConnectionClosed:
                pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(**crawler.settings.get('PYPPETEER_ARGS', {}))
