---
layout: default
title: "GitHub Pages"
---

# GitHub Pages

[Home](../README.md) · [Game gallery](../examples/rocm-7.14/falling-blocks/index.html)

GitHub Pages renders this repository's Markdown using its standard Jekyll build. The explicit `index.md` is the home page. Public Markdown documents declare `layout: default` and a quoted page title in YAML front matter; the relative-links plugin resolves their Markdown links. The private temporary runbook is excluded from the site. HTML games, SVG graphs, CSV data and scripts remain static files. There is no custom Markdown parser or Python rendering dependency. See [GitHub's Jekyll documentation](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll).

## Enable hosting

Put the release contents at the root of the public repository. Select **Settings → Pages → Build and deployment → Source → GitHub Actions**. Push to `main`, or manually run the **GitHub Pages** workflow. If the publishing branch has another name, update the two branch conditions in `.github/workflows/pages.yml`.

The workflow uses GitHub's `actions/jekyll-build-pages` action, checks the resulting links, then deploys the standard Pages artefact. Pull requests build without deploying. `_config.yml` selects the supported Primer theme and Markdown/link settings. No GitHub remote or live deployment is configured in the current workspace.

## Preview

Use the standard [local Jekyll preview procedure](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/testing-your-github-pages-site-locally-with-jekyll), or review the built site artefact from the workflow. No separate Markdown conversion step is needed. After regenerating documentation, run `python3 tools/page_metadata.py` to add front matter to any newly generated page; the navigation generator also performs this step. The game HTML files can also be opened directly in a browser.

`tools/check_pages.py` validates local file and anchor links in an already-built site; it does not render or rewrite content. Data derivation and SVG chart generation are separate from site hosting.

<!-- NAVIGATION START -->

[Home](../index.md) · [Overview](../README.md) · [Latest campaign](RADIANCE-CAMPAIGN-2026-10-21.md) · [Charts](CHARTS.md)
