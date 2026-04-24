---
marp: true
html: true
paginate: true
class: dark
style: |
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;800&family=Raleway:wght@100;200;300&display=swap');

  /* Light mode defaults */
  :root {
    --accent:  #2563eb;
    --bg:      #fafafa;
    --card:    #ffffff;
    --border:  #eeeeee;
    --body:    #555555;
    --muted:   #999999;
    --light:   #1a1a1a;
    --green:   #16a34a;
    --red:     #dc2626;
    --yellow:  #d97706;
  }

  /* Dark mode overrides — activated by class: dark in frontmatter */
  section.dark {
    --accent:  #ff6b1a;
    --bg:      #000000;
    --card:    #080808;
    --border:  #111111;
    --body:    #999999;
    --muted:   #555555;
    --light:   #ffffff;
    --green:   #22c55e;
    --red:     #ef4444;
    --yellow:  #f5a623;
  }

  section {
    background: var(--bg);
    color: var(--light);
    font-family: 'Raleway', sans-serif;
    font-weight: 200;
    padding: 56px 72px;
  }
  h1 { font-family: 'Outfit'; font-weight: 800; font-size: 3em; color: var(--light); margin: 0; }
  h2 { font-family: 'Raleway'; font-weight: 100; font-size: 1.3em; color: var(--body); margin: 0.2em 0 0; }
  h3 { font-family: 'Outfit'; font-weight: 600; font-size: 0.6em; color: var(--muted); text-transform: uppercase; letter-spacing: 0.2em; margin: 0 0 0.8em; }
  strong { color: var(--accent); font-weight: 300; }
  section.lead { display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
  section > ul, section > ol { color: var(--body); font-size: 0.9em; line-height: 1.9; }
---

<!-- _class: lead -->

# Presentation Title
## Subtitle or tagline

---

### Section Label

# Slide Title

Content goes here.

- Point one
- Point two
- Point three
