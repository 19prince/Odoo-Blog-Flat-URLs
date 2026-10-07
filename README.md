# Odoo Blog Flat URLs

> Clean blog URLs for Odoo websites: `/blog/<post>` instead of `/blog/blog-1/<post>`. By [19prince.com](https://www.19prince.com)

Odoo is built for websites that run several blogs, so it files every post inside its blog's folder:

```
/blog/<blog>/<post>
```

The folder name is the blog's name plus its database ID. A blog named "Blog" with ID 1 gets the folder `blog-1`, so every post URL looks like `/blog/blog-1/my-post-27`.

On a website with one blog, that folder does nothing useful, and Odoo answers `/blog` with a temporary redirect:

```
/blog                       -> 302 -> /blog/blog-1
/blog/blog-1/my-post-27     (the real post URL)
/blog/blog-1/feed           (the RSS feed)
```

The 302 tells Google that `/blog` has only moved temporarily, so the blog index never firmly owns its authority. Odoo's sitemap has listed the redirecting `/blog` too, which Search Console reports as "Page with redirect".

This module is for **single-blog websites**. It removes the folder and the redirect:

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

## Single blog vs. multiple blogs

**Install this on websites with one blog.** The folder is how Odoo tells several blogs apart, and this module removes it:

| | One blog | Several blogs |
|---|---|---|
| Post URLs | `/blog/my-post-27` | `/blog/my-post-27` (no way to tell which blog from the URL) |
| Blog index | `/blog` | every blog's index (`/blog/news-2`, `/blog/updates-3`) 301s to one combined `/blog` |
| RSS | `/blog/feed` | `/blog/feed` serves the first blog only; every other blog's feed 301s to it |
| Verdict | Use it | Keep Odoo's default URLs |

If you run several blogs, give each one a meaningful name so the folder reads `/blog/news-2` instead of `/blog/blog-1`.

## Limits

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
