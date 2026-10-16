# Static sites with Astro

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from Astro official docs (context7 `/withastro/docs`, Astro v6)._

## Reference snippet

```ts
// src/content.config.ts: content collections with types
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishDate: z.coerce.date(),     // changes string frontmatter to Date
    draft: z.boolean().default(false),
    tags: z.array(z.string()).optional(),
  }),
});

export const collections = { blog };
```

## Typical usage patterns

- The site is a static content site with **no UI framework**. It uses only `.astro` files with Markdown and MDX. (seen in `JasonLo/jasonlo.dev`)
- One `src/content.config.ts` file declares many typed collections, for example `blog`, `projects`, `publications`, `tools`, and `journey`. Each collection has a `glob()` loader and a detailed Zod `schema`. (seen in `JasonLo/jasonlo.dev:src/content.config.ts`)
- Pages query with `getCollection` and `getEntry`, and render bodies with `render(entry)` and `<Content />`. The `getStaticPaths` function builds the dynamic routes statically. (seen in `JasonLo/jasonlo.dev:src/pages/blog/[slug].astro`)

## Learnings

- **Frontmatter is untyped text** → **A collection schema validates and types the frontmatter.** Each Zod schema coerces and validates values at build time, for example with `z.coerce.date`, enums, and defaults. Then pages get real types, and content with errors stops the build before it gets to the browser.
- **The folder of a file defines its collection** → **You declare collections. Astro does not discover them.** In v6, you register each collection in `src/content.config.ts` with a specified `loader: glob({...})`. The source folder is a config value, and Astro removed the old automatic `src/content/<name>` model.
- **A site framework sends a JS runtime to the browser** → **Astro sends no JS by default, and you must request hydration.** Use a client island (`client:*`) only for interactive widgets. For static content and simple DOM work, use HTML with a plain `<script>`.

## Agent rules

- ALWAYS declare content collections in `src/content.config.ts` with a specified `loader: glob({ pattern, base })`.
- ALWAYS give every collection a Zod `schema`.
- ALWAYS use `z.coerce.date()` for dates in a collection schema.
- ALWAYS use `z.enum(...)` for fixed sets of values.
- ALWAYS use `.default(...)` or `.optional()` for optional frontmatter.
- ALWAYS access content through `getCollection` and `getEntry` from `astro:content`.
- NEVER read content files from disk directly.
- ALWAYS render entry bodies with `render(entry)` and then `<Content />`.
- NEVER call `entry.render()`.
- ALWAYS build dynamic content routes statically with `getStaticPaths`.
- ALWAYS set `site` in `astro.config.mjs` when you use sitemap, canonical URLs, or absolute URLs.
- NEVER add a UI-framework integration or a `client:*` directive for static content or simple DOM work.
- ALWAYS use a scoped `<script>` for simple DOM work.
- ALWAYS use `<script is:inline>` for pre-paint logic, for example theme and reduced motion, to prevent flashes.
- ALWAYS keep hydrated islands for stateful widgets only.
- ALWAYS emit generated files, for example search index, RSS, llms.txt, and robots, as endpoint routes that export `GET()`.
- ALWAYS make these endpoint routes read the same collections as the pages.
- ALWAYS filter drafts at query time, for example with a shared `getPublished` wrapper.
- NEVER let unpublished entries appear on a page.
