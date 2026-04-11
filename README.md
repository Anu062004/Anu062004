# Hi 👋, I'm Anubhav

**Web3Explorer,Crypto Enthusiast**

---

## 🧑 About Me

- 🏢 Student
- 💡 I love solving **real-world problems** through technology
- ✨ Passionate about **Blockchain Technologies**
- 🎓 2nd year undergrad at BMSIT Banglore
- 💬 Ask me about **Node.js,JavaScript,C++,TypeScript**
- 📫 Reach me at: `anubhavrajput572@gmail.com`

---

## 🚀 Tech Stack

[![react](https://skillicons.dev/icons?i=react)](https://skillicons.dev)
[![nextjs](https://skillicons.dev/icons?i=nextjs)](https://skillicons.dev)
[![nodejs](https://skillicons.dev/icons?i=nodejs)](https://skillicons.dev)
[![ts](https://skillicons.dev/icons?i=ts)](https://skillicons.dev)
[![py](https://skillicons.dev/icons?i=py)](https://skillicons.dev)
[![mongodb](https://skillicons.dev/icons?i=mongodb)](https://skillicons.dev)
[![js](https://skillicons.dev/icons?i=js)](https://skillicons.dev)
[![docker](https://skillicons.dev/icons?i=docker)](https://skillicons.dev)
[![postgresql](https://skillicons.dev/icons?i=postgresql)](https://skillicons.dev)
[![rust](https://skillicons.dev/icons?i=rust)](https://skillicons.dev)
[![aws](https://skillicons.dev/icons?i=aws)](https://skillicons.dev)
[![git](https://skillicons.dev/icons?i=git)](https://skillicons.dev)

---

## 🌐 Let's Connect!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://https://www.linkedin.com/in/anubhav-rajput-809b8521a/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:anubhavrajput572@gmail.com)



name: Generate Snake Animation

on:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: Platane/snk@v3
        with:
          github_user_name: Anu062004
          outputs: |
            dist/github-contribution-grid-snake.svg
            dist/github-contribution-grid-snake-dark.svg?palette=github-dark

      - uses: crazy-max/ghaction-github-pages@v3
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

<!--
**Anu062004/Anu062004** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
