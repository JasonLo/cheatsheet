# Static sites with Astro

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Astro official docs (context7 `/withastro/docs`, Astro v6)._

## Reference snippet

```ts
// src/content.config.ts — typed content collections
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishDate: z.coerce.date(),     // string frontmatter -> Date
    draft: z.boolean().default(false),
    tags: z.array(z.string()).optional(),
  }),
});

export const collections = { blog };
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',           // required for sitemap/canonical URLs
  integrations: [mdx(), sitemap()],
});
```

```astro
---
// src/pages/blog/[slug].astro — static page from a collection
import { getCollection, getEntry, render } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({ params: { slug: post.id } }));
}

const post = await getEntry('blog', Astro.params.slug!);
const { Content } = await render(post);   // v6: render(entry), not entry.render()
---
<BaseLayout>
  <h1>{post.data.title}</h1>
  <Content />
</BaseLayout>
```

## Typical usage patterns

- Content-focused static site, **no UI framework** — pure `.astro` + Markdown/MDX; ships zero client JS by default. (`JasonLo/jasonlo.dev`)
- One `src/content.config.ts` with many typed collections (`blog`, `projects`, `publications`, `tools`, `journey`), each a `glob()` loader + a rich Zod `schema`. (`JasonLo/jasonlo.dev:src/content.config.ts`)
- Schemas do real work: `z.coerce.date()` for dates, `z.enum(...)` for status, `.default(false)` for `draft`, nested `z.object`/`z.array` for structured frontmatter.
- Query via `getCollection` / `getEntry`, render bodies via `render(entry)` → `<Content />`; dynamic routes built statically through `getStaticPaths`. (`JasonLo/jasonlo.dev:src/pages/blog/[slug].astro`)
- Thin reusable filter wrapping the framework API, e.g. a `getPublished(name)` that drops `draft` entries, so every page filters consistently. (`JasonLo/jasonlo.dev:src/utils/collections.ts`)
- Non-HTML outputs as endpoint routes: `search-index.json.ts`, `llms.txt.ts`, `robots.txt.ts` export `GET()` and read the same collections. (`JasonLo/jasonlo.dev:src/pages/search-index.json.ts`)
- Layout owns `<head>`; pages inject SEO via a named `<slot name="head" />`; `ClientRouter` adds View Transitions. (`JasonLo/jasonlo.dev:src/layouts/BaseLayout.astro`)
- Interactivity is small vanilla TS in `<script>` blocks (theme toggle, search, scroll); pre-paint logic uses `<script is:inline>` to avoid flashes — no hydrated component islands needed.
- Integrations kept minimal: `@astrojs/mdx` + `@astrojs/sitemap`, Shiki for code highlighting, sharp image service.

## Learnings

- **Frontmatter is untyped text** → **a collection schema is the validated, typed contract.** Define a Zod schema per collection; coerce/validate at build (`z.coerce.date`, enums, defaults) so pages consume real types and bad content fails the build, not the browser.
- **"Where files live = a folder convention"** → **collections are declared, not discovered.** In v6 you register collections in `src/content.config.ts` with an explicit `loader: glob({...})`; the source dir is a config value, not magic. The legacy auto-`src/content/<name>` collection model is gone.
- **A site framework means shipping a JS runtime** → **Astro ships zero JS by default; hydration is opt-in per component.** Reach for a client island (`client:*`) only for genuinely interactive widgets; static content and light DOM work stay HTML + a plain `<script>`.
- **"Render the entry" is a method on the entry** → **rendering is a free function: `render(entry)`.** v6 removed `entry.render()`; import `render` from `astro:content`. Same shift for data access — query through `getCollection`/`getEntry`, never by reading files yourself.
- **Generated data (search index, RSS, llms.txt) is a side build step** → **it's just another route.** A `*.json.ts` / `*.txt.ts` page exporting `GET()` reads your collections at build time — one source of truth, no separate pipeline.
- **Interactivity = pull in React/Vue** → **most "interactive" needs are a scoped `<script>`.** Add a UI-framework integration only when component state/reuse justifies it; otherwise vanilla TS keeps the bundle empty.

## Agent rules

- ALWAYS declare content collections in `src/content.config.ts` with an explicit `loader: glob({ pattern, base })`.
- ALWAYS give every collection a Zod `schema`; use `z.coerce.date()` for dates, `z.enum(...)` for fixed sets, `.default(...)`/`.optional()` for optional frontmatter.
- ALWAYS access content through `getCollection` / `getEntry` from `astro:content`; NEVER read content files from disk directly.
- ALWAYS render entry bodies with `render(entry)` then `<Content />`; NEVER call `entry.render()` (removed in v6).
- ALWAYS build dynamic content routes statically via `getStaticPaths`.
- ALWAYS set `site` in `astro.config.mjs` when using sitemap or canonical/absolute URLs.
- NEVER add a UI-framework integration or `client:*` directive for static content or trivial DOM work; use a scoped `<script>` instead.
- ALWAYS use `<script is:inline>` for pre-paint logic (theme, reduced-motion) to avoid flashes; reserve hydrated islands for genuinely stateful widgets.
- ALWAYS emit generated artifacts (search index, RSS, llms.txt, robots) as endpoint routes exporting `GET()` that read the same collections.
- ALWAYS filter drafts at query time (e.g. a shared `getPublished` wrapper) so unpublished entries never reach a page.
