# Generative AI Usage Declaration — Ching Yun Hsu

## Tools Used

- Gemini (gemini.google.com)



## Conversation Log

- Part 1 : System Architecture & Backend DevOps

  https://gemini.google.com/share/831fd70a0702

- Part 2 : Frontend Interface & UI/UX Design

  https://gemini.google.com/share/cfebc9bb5231

- Part 3 : Advanced Feature Integration

  https://gemini.google.com/share/694e5d83af99


## What I Used AI For

### System Architecture & Backend DevOps: 

  Used AI to build a foundational understanding of full-stack workflows, specifically clarifying Flask's role as the middleware connecting the frontend and database. Sought guidance on containerization concepts, including the differences between Dockerfile and docker-compose.yml, and modern Python dependency management using uv and uv.lock. Additionally, I utilized AI for DevOps troubleshooting—specifically learning how to safely resolve Git merge conflicts (<<<<<<< HEAD) and addressing EC2 out-of-memory (OOM) limitations by replacing continuous scraping loops with resource-efficient Linux Cron Jobs.

### Frontend Interface & UI/UX Design: 

  Consulted AI to optimize frontend architecture and improve user experience. I used AI to learn Jinja2 template inheritance (base.html and {% block content %}) to eliminate code duplication across multiple pages. Furthermore, I sought implementation strategies for interactive UI elements using Vanilla JavaScript, such as real-time email format validation, password visibility toggles, and URL hash-based cross-page tab navigation. I also used AI to understand how to dynamically render Jinja elements based on backend states, such as displaying login error messages safely and personalizing the navigation bar based on cookie status.

### Advanced Feature Integration: 

  Leveraged AI to navigate complex system integrations and security protocols. I used AI to understand state management (differentiating between Sessions and Cookies for persistent logins) and to resolve Cross-Origin Resource Sharing (CORS) errors between frontend scripts and backend APIs. To ensure security, I consulted AI on how to safely inject Google Maps API keys into the frontend using .env variables without hardcoding them. I also used AI to guide the development of interactive mapping features (plotting dynamic, color-coded markers based on occupancy data) and to understand the data flow required to serve predictions from a Python Machine Learning model (.pkl) to the frontend for visualization via CSS progress bars.

## Reflection

- All AI-generated explanations, JavaScript logic, and Jinja2 syntax were treated as educational guides. I personally tested, adapted, and integrated all code into the actual project codebase to ensure it met our specific requirements.

- Security implementations suggested by the AI—particularly the handling of .env variables for API keys and the theoretical understanding of Session/Cookie management—were manually verified to ensure production-level safety and prevent data exposure.

- System configurations, such as the EC2 Cron Job schedules and Docker setups, were tested in local and staging environments before final deployment.

- The AI served primarily as an interactive technical tutor to bridge my knowledge gaps. All final architectural decisions, logic structures, and UI designs were made and validated by me personally.
