---
layout: default
title: "GitHub Pages"
---

# GitHub Pages

[Home](../index.md) · [Game gallery](../examples/rocm-7.14/falling-blocks/index.html)

GitHub Pages renders this repository's Markdown using its standard Jekyll build. The explicit `index.md` is the home page. Public Markdown documents declare `layout: default` and a quoted page title in YAML front matter; the relative-links plugin resolves their Markdown links. The private temporary runbook is excluded from the site. HTML games, SVG graphs, CSV data and scripts remain static files. There is no custom Markdown parser or Python rendering dependency. See [GitHub's Jekyll documentation](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll).

## Enable hosting

Put the release contents at the root of the public repository. Select **Settings → Pages → Build and deployment → Source → GitHub Actions**. Push to `main`, or manually run the **GitHub Pages** workflow. If the publishing branch has another name, update the two branch conditions in `.github/workflows/pages.yml`.

The workflow uses GitHub's `actions/jekyll-build-pages` action, checks the resulting links, then deploys the standard Pages artefact. Pull requests build without deploying. `_config.yml` retains the supported Primer dependency and Markdown/link settings. The repository’s `_layouts/default.html` and `assets/css/editorial.css` provide the responsive editorial presentation using standard Jekyll; no custom plugin or client-side framework is needed. Publication remains controlled by the repository’s configured GitHub Pages workflow; a local editorial edit does not publish anything.

## Editorial sources and preview

`README.md` is the canonical main article. Run `python3 tools/build_home.py` to regenerate the same story in `index.md` with its home permalink. The original Humans and RTFM sections are preserved verbatim. Earlier results and their deep-link targets live in `HISTORICAL-OVERVIEW.md`.

The setup story, research history, code corner and disclosure live in `docs/ENVIRONMENT.md`, `docs/RESEARCH-HISTORY.md`, `docs/CODE-CORNER.md` and `docs/REPRODUCIBILITY.md`. `AGENTS.md` is versioned repository maintenance guidance and remains excluded from the site. The marked code inventory is generated; the surrounding narrative is edited by hand.

The two engine hubs are `docs/VLLM-RADIANCE.md` and `docs/RADIANCE.md`; the comparison page links their campaign evidence. Rebuild the derived comparison with `python3 tools/build_comparison_data.py`, figures with `python3 tools/render_editorial.py`, and navigation/gallery/front matter with `python3 tools/build_navigation.py`. The archive-derived release builder is separate and is not required for an editorial change.

Use the standard [local Jekyll preview procedure](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/testing-your-github-pages-site-locally-with-jekyll), or review the built site artefact from the workflow. No separate Markdown conversion step is needed. Use the same GitHub Pages dependencies as CI; test both root hosting and a repository base path when modifying the layout.

`python3 tools/check_pages.py _site` validates local files and anchors in the built site. For a project-site build, pass `--base-path /REPOSITORY`. It does not render or rewrite content. Check wide and narrow viewports, table scrolling, chart labels and the explicit full-size chart links. Games remain independent static HTML.

<!-- NAVIGATION START -->

[Home](../index.md) · [Compare](RADIANCE-VS-VLLM.md) · [vllm-radiance](VLLM-RADIANCE.md) · [radiance](RADIANCE.md) · [Charts](CHARTS.md) · [Stuff for nerds](CODE-CORNER.md) · [Disclosure](REPRODUCIBILITY.md)
<!-- NAVIGATION END -->
