# Hill Green Techno Solutions Website

This package contains the complete multi-page HTML website.

## Files
- `index.html` — Home
- `about.html` — About and editable two-director profiles
- `software.html` — Software Consulting & Development
- `skills.html` — Skill Development & EV Training
- `research.html` — Market Research & Consulting
- `nipuna.html` — NIPUNA Programme
- `projects.html` — Projects & Impact
- `credentials.html` — Credentials & Partnerships
- `insights.html` — Insights & Resources
- `contact.html` — Contact
- `styles.css` — Shared responsive styles and accessibility refinements
- `app.js` — Shared page content, interactions, navigation and metadata
- `assets/hill-green-logo.png` — Hill Green logo

## Preview
Keep the folder structure intact. Open `index.html` in a modern browser. For best results, run a local static server from this folder (for example, `python3 -m http.server 8000`) and visit `http://localhost:8000`.

The Google Fonts and Unsplash images are loaded online. Replace image URLs with approved company photography before production. Telugu translations and a production contact-form backend still need to be added.

Director profiles are editable placeholders. Replace all bracketed placeholder copy with approved company information before publishing.


### Contact form integration
The Contact Us page now embeds the Google Form supplied by the site owner. Submissions are handled by Google Forms, not by the website files. Link the form to a Google Sheet and configure response notifications in the form owner's Google account. The iframe is responsive in width; its height is set to 900px and may need adjustment if the form's questions change.

## Latest contact and footer updates
- The Contact Us page now displays the supplied business address, phone numbers and email address.
- The footer uses the original full-colour logo on a light background for legibility.
- The Connect column retains only the Contact us link and includes address, phone and email details.
- The Google Forms enquiry embed remains on the Contact Us page.
- Note: the current site content remains in English. The Telugu button is a placeholder; full Telugu page translations have not been added or reviewed.


Latest correction: removed the obsolete language-toggle event handler that referenced a button no longer present in the navigation. This JavaScript error prevented the page-rendering function from running. The page content is rendered from app.js on each HTML route. The footer tagline has also been removed. The full Visakhapatnam postal address remains in the contact details as previously requested.
