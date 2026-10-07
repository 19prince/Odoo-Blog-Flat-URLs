from odoo import models


class BlogPost(models.Model):
    _inherit = "blog.post"

    def _compute_website_url(self):
        super()._compute_website_url()
        for post in self:
            if post.id:
                post.website_url = "/blog/%s" % self.env["ir.http"]._slug(post)
