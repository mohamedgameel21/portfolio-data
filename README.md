# portfolio-data

Syncs GitHub projects -> portfolio JSON + resume PDF + WhatsApp reminder for LinkedIn.

1. Add the topic `portfolio` to each repo you want to show (and a description; put the Streamlit/demo link in the repo's Website field).
2. Repo Settings > Secrets and variables > Actions: add `WHATSAPP_PHONE` (with country code, e.g. +20...) and `CALLMEBOT_APIKEY`.
3. Actions tab > "Sync projects" > Run workflow. It also runs every 6 hours.
4. Portfolio reads: https://raw.githubusercontent.com/mohamedgameel21/portfolio-data/main/data/projects.json
5. Resume: resume/resume.pdf (edit data/profile.json for the non-project sections).
