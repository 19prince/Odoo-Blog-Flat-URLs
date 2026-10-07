import re

import werkzeug

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_blog.controllers.main import WebsiteBlog


def sitemap_blog_post(env, rule, qs):
    website = env["website"].get_current_website()
    domain = website.website_domain() + [("website_published", "=", True)]
    for post in env["blog.post"].search(domain):
        if not qs or qs.lower() in post.website_url.lower():
            yield {"loc": post.website_url}


def _flat_blog_url(tag=None, **opt):
    return QueryURL("/blog", ["tag"], tag=tag, date_begin=opt.get("date_begin"),
                    date_end=opt.get("date_end"), search=opt.get("search"))


def _redirect(path):
    return request.redirect_query(path, request.httprequest.args, code=301)


class WebsiteBlogFlat(WebsiteBlog):

    # Core also routes /blog/<blog>; dropped here so /blog/<post> can use the slot.
    @http.route([
        "/blog",
        "/blog/page/<int:page>",
        "/blog/tag/<string:tag>",
        "/blog/tag/<string:tag>/page/<int:page>",
    ], type="http", auth="public", website=True, sitemap=True)
    def blog(self, blog=None, tag=None, page=1, search=None, **opt):
        if not blog:
            blogs = request.env["blog.blog"].search(request.website.website_domain())
            if len(blogs) == 1:
                blog = blogs  # render in place instead of core's 302 to /blog/<blog>
        response = super().blog(blog=blog, tag=tag, page=page, search=search, **opt)
        qcontext = getattr(response, "qcontext", None)
        if qcontext and "blog_url" in qcontext:
            qcontext["blog_url"] = _flat_blog_url(tag=tag, search=search, **opt)
        return response

    @http.route(["/blog/<string:slug>"], type="http", auth="public", website=True,
                sitemap=sitemap_blog_post)
    def blog_post(self, slug, tag_id=None, page=1, enable_editor=None, **post):
        IrHttp = request.env["ir.http"]
        domain = request.website.website_domain()

        blogs = request.env["blog.blog"].search(domain)
        # Old blog index URL, e.g. /blog/blog-1
        if any(IrHttp._slug(b) == slug for b in blogs):
            return _redirect("/blog")

        record_id = IrHttp._unslug(slug)[1]
        # search() applies record rules: visitors can't reach unpublished posts
        blog_post = record_id and request.env["blog.post"].search(domain + [("id", "=", record_id)], limit=1)
        if not (blog_post and IrHttp._slug(blog_post) == slug):
            if record_id in blogs.ids:
                # Index URL of a renamed blog (/blog/blog-1 after renaming to News).
                # ponytail: a stale slug of the post sharing that ID lands on /blog too
                return _redirect("/blog")
            if blog_post:
                return _redirect(blog_post.website_url)
            raise werkzeug.exceptions.NotFound()

        response = super().blog_post(blog_post.blog_id, blog_post, tag_id=tag_id, page=page,
                                     enable_editor=enable_editor, **post)
        qcontext = getattr(response, "qcontext", None)
        if qcontext and "blog_url" in qcontext:
            qcontext["blog_url"] = _flat_blog_url(tag=qcontext.get("tag"), **post)
        return response

    # ponytail: serves the website's first blog; multi-blog sites keep core's per-blog feeds
    @http.route(["/blog/feed"], type="http", auth="public", website=True, sitemap=True)
    def blog_feed_flat(self, limit="15", **kw):
        blog = request.env["blog.blog"].search(request.website.website_domain(), limit=1)
        if not blog:
            raise werkzeug.exceptions.NotFound()
        return super().blog_feed(blog, limit=limit, **kw)

    # ---- 301s from the old /blog/<blog>/... URLs ----

    @http.route(["/blog/<model('blog.blog'):blog>/feed"], type="http", auth="public", website=True,
                sitemap=False)
    def blog_feed(self, blog, **kw):
        return _redirect("/blog/feed")

    @http.route([
        "/blog/<model('blog.blog'):blog>/page/<int:page>",
        "/blog/<model('blog.blog'):blog>/tag/<string:tag>",
        "/blog/<model('blog.blog'):blog>/tag/<string:tag>/page/<int:page>",
    ], type="http", auth="public", website=True, sitemap=False)
    def blog_legacy(self, blog, **kw):
        return _redirect(re.sub(r"/blog/[^/]+", "/blog", request.httprequest.path, count=1))

    @http.route(["/blog/<model('blog.blog'):blog>/<model('blog.post'):blog_post>"],
                type="http", auth="public", website=True, sitemap=False)
    def blog_post_legacy(self, blog, blog_post, **kw):
        return _redirect(blog_post.website_url)
