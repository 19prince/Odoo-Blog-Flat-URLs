from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestFlatUrl(HttpCase):

    def test_flat_urls(self):
        website = self.env["website"].get_current_website()
        self.env["blog.blog"].search([]).write({"website_id": False, "active": False})
        blog = self.env["blog.blog"].create({"name": "Blog", "website_id": website.id})
        post = self.env["blog.post"].create({"name": "Flat Post", "blog_id": blog.id, "is_published": True})
        slug = self.env["ir.http"]._slug
        flat = "/blog/%s" % slug(post)

        self.assertEqual(post.website_url, flat)
        self.assertEqual(self.url_open("/blog", allow_redirects=False).status_code, 200)
        self.assertEqual(self.url_open(flat, allow_redirects=False).status_code, 200)

        old = self.url_open("/blog/%s/%s" % (slug(blog), slug(post)), allow_redirects=False)
        self.assertEqual(old.status_code, 301)
        self.assertTrue(old.headers["Location"].endswith(flat))

        index = self.url_open("/blog/%s" % slug(blog), allow_redirects=False)
        self.assertEqual(index.status_code, 301)
        self.assertTrue(index.headers["Location"].endswith("/blog"))

        self.assertEqual(self.url_open("/blog/feed", allow_redirects=False).status_code, 200)
        feed = self.url_open("/blog/%s/feed" % slug(blog), allow_redirects=False)
        self.assertEqual(feed.status_code, 301)
        self.assertTrue(feed.headers["Location"].endswith("/blog/feed"))
