from page_objects.PageTiktok import PageTiktok
import time

class TiktokAudit(PageTiktok):
    def test_random(self):
        self.fetch_tiktok(1)
        self.iterate_through_batches_random()
        time.sleep(10)

    def test_random2(self):
        self.fetch_tiktok(1)
        self.iterate_through_batches_random()
        time.sleep(10)


