# Odoo Blog Flat URLs

> Clean blog URLs for Odoo websites: `/blog/<post>` instead of `/blog/blog-1/<post>`. By [19prince.com](https://www.19prince.com)

Every Odoo website with a single blog puts an extra folder in every post URL, and answers `/blog` itself with a temporary redirect:

```
/blog                       -> 302 -> /blog/blog-1
/blog/blog-1/my-post-27     (the real post URL)
/blog/blog-1/feed           (the RSS feed)
```

`blog-1` is the slug of the blog Odoo creates for you. It means nothing to readers or search engines, and the 302 tells Google that `/blog` is only temporarily somewhere else, so the blog index never firmly owns its authority. Odoo's own sitemap has listed the redirecting `/blog` URL too, which Search Console reports as "Page with redirect".

This module removes the folder and the redirect:

```
/blog                       -> 200, the blog index renders in place
/blog/my-post-27            -> 200, the post
/blog/feed                  -> 200, the RSS feed
/blog/blog-1/my-post-27     -> 301 -> /blog/my-post-27
```

The Odoo module inside this repository is `website_blog_flat_url` (its technical name).

- **Odoo:** 18.0 (Community or Enterprise)
- **Depends on:** `website_blog`
- **License:** LGPL-3
- **Author:** [19 Prince](https://www.19prince.com), Odoo consultancy

---

## Why a website redirect can't fix this

The `/blog/<blog>/` segment is hard-coded across Odoo, not in one place:

- the `/blog` controller, which issues the 302 when there is only one blog (unchanged from Odoo 18 through 20)
- `blog.post.website_url`
- the post list, cover, teaser, heading, "read next" and comment sign-in templates
- the RSS feed route and its `<link>` tags
- the sitemap generator

On top of that, Odoo's URL routing rewrites any record URL to its canonical form and 301s if they differ, so a hand-made route to `/blog/<post>` bounces straight back to `/blog/blog-1/<post>`. A redirect rule in **Website > Configuration > Redirects** only adds a hop; every link Odoo renders still points at the old URL.

## What the module changes

| Area | Before | After |
|---|---|---|
| Blog index | `/blog` 302s to `/blog/blog-1` | `/blog` renders in place (200) |
| Post URL | `/blog/blog-1/my-post-27` | `/blog/my-post-27` |
| Tags and paging | `/blog/blog-1/tag/odoo-3/page/2` | `/blog/tag/odoo-3/page/2` |
| RSS | `/blog/blog-1/feed` | `/blog/feed` |
| `sitemap.xml` | lists `/blog` (a redirect), `/blog/blog-1`, `/blog/blog-1/feed` and every post under `/blog/blog-1/` | lists `/blog`, `/blog/feed`, and every published post at its flat URL. No redirecting URLs. |
| Old URLs | | Every `/blog/<blog>/...` URL 301s to its flat equivalent, keeping query strings |
| Internal links | | Post links, "read next", cover images, comment sign-in and RSS `<link>` tags point straight at the flat URL, with no 301 hop |

### RSS subscribers

The feed's Atom `<id>` is left unchanged, so existing subscribers keep their subscription and don't see posts as new. The old feed URL 301s to `/blog/feed`, which feed readers follow.

### Unpublished posts

Posts are looked up with normal record rules, so visitors get a 404 for unpublished posts exactly as before. Editors still see their drafts.

---

## Installation

### Odoo.sh / on-premise

1. Copy the `website_blog_flat_url/` folder into your addons path (on Odoo.sh, into the branch that backs your build).
2. In developer mode, go to **Apps > Update Apps List**.
3. In Apps, remove the **Apps** filter (this is a module, not an app), search **"Blog Flat"**, and click **Install**.

### After installing on a live site

1. **Rebuild the sitemap.** Odoo caches `sitemap.xml` as an attachment for 12 hours. Delete it (**Settings > Technical > Attachments**, search `sitemap`) so the next request regenerates it with the flat URLs.
2. **Resubmit the sitemap** in Google Search Console.
3. Old URLs need nothing: they 301 forever, so backlinks, shared links and indexed pages carry over.

### Odoo Online (SaaS)

Odoo Online doesn't allow custom Python modules, so this can't be installed there.

---

## Limits

- **Built for one blog per website.** If a website has several blogs, posts still get flat URLs and old URLs still redirect, but `/blog/feed` serves the first blog only, and `/blog` shows all blogs as core does.
- **The trailing ID stays** (`my-post-27`). Dropping it means looking posts up by title, which breaks when a post is renamed or two posts share a title.
- Uninstalling restores Odoo's default URLs. The flat URLs would then 404, so add redirects before you uninstall a site with traffic.

---

## Tests

```
odoo-bin -d <db> -i website_blog_flat_url --test-tags=/website_blog_flat_url --stop-after-init
```

Covers the 200s on `/blog`, the flat post URL and `/blog/feed`, and the 301s from the old post, index and feed URLs.

---

## About 19 Prince

[19 Prince](https://www.19prince.com) helps businesses on Odoo drive more demand with the tool they already own. More free modules: [19prince.com/resources](https://www.19prince.com/resources).
