# FFA Skills Project: MCP and Claude Skills Demo

A demonstration project showcasing Model Context Protocol (MCP) servers and Claude Skills for indie authors and publishers.

## Overview

This project demonstrates how indie authors and publishers can leverage cutting-edge AI technologies to enhance their writing workflows. It features practical implementations of Model Context Protocol (MCP) servers and Claude Skills that address real-world challenges in the publishing industry.

## What's Included

### Word Tracker Skill
A comprehensive word counting and analytics tool designed specifically for authors:

- **Real-time word counting** across multiple file formats
- **Progress tracking** with daily, weekly, and monthly analytics
- **Goal setting and monitoring** for writing projects
- **Flexible scanning** of directories and individual files
- **Export capabilities** for progress reports

Located in `skills/word-tracker/`, this skill demonstrates how AI can assist with project management and productivity tracking for authors.

### Draft Management
The `drafts/` folder contains sample chapter files from "Moonlight on Maple Hollow," a paranormal romance novel targeting 70,000 words, that demonstrate the word tracker in action with a real manuscript project.

## Features

- **MCP Integration**: Demonstrates how to build and deploy Model Context Protocol servers
- **Claude Skills**: Shows practical implementation of Claude Skills for writing workflows
- **Author-Focused Tools**: Built specifically for the needs of indie authors and publishers
- **Cross-Platform Compatibility**: Works on macOS, Windows, and Linux
- **Easy Integration**: Designed to integrate seamlessly into existing writing workflows

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Claude Desktop application (for Claude Skills integration)
- Git (for version control)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ffa-skills-project.git
   cd ffa-skills-project
   ```

2. Install dependencies:
   ```bash
   cd skills/word-tracker
   pip install -r requirements.txt
   ```

3. Run the word tracker:
   ```bash
   python scripts/word_tracker_standalone.py
   ```

### Usage

#### Word Tracker
The word tracker can be used in several ways:

- **Standalone script**: Run directly for immediate word counts
- **Claude Skill**: Integrate with Claude for AI-powered writing assistance
- **MCP Server**: Deploy as a service for broader tool integration

See the detailed documentation in `skills/word-tracker/README.md` for complete usage instructions.

## Project Structure

```
ffa-skills-project/
├── drafts/                     # Sample manuscript chapters (Moonlight on Maple Hollow - 70K word target)
├── skills/
│   └── word-tracker/          # Word tracking skill implementation
│       ├── README.md          # Detailed documentation
│       ├── REFERENCE.md       # API reference
│       ├── SKILL.md          # Claude Skills configuration
│       └── scripts/          # Implementation files
└── README.md                 # This file
```

## Live promo page

The static promo site for "Moonlight on Maple Hollow" is published with GitHub Pages:

- Live URL: https://blossomz37.github.io/ffa-skills-project/

### Source of truth

- Edit the page at `docs/index.html` (this is the canonical file used by GitHub Pages).
- GitHub Pages is configured to deploy from the `main` branch, folder `/docs`.

### Chapter previews

- Previews are simple Markdown files under `docs/chapters/` (example files are provided):
   - `docs/chapters/chapter-1-homecoming-fog.md`
   - `docs/chapters/chapter-2-alpha-at-the-bar.md`
- To add more previews:
   1) Create a new `.md` file in `docs/chapters/`.
   2) In `docs/index.html`, add an entry to the `chapters` array in `ChaptersViewer` with `title`, `file`, and a short `blurb`.
   3) Commit and push to `main`; the site updates automatically.

### Preview locally

- Open `docs/index.html` in a browser. It’s a fully static page that loads React, ReactDOM, and Tailwind via CDNs.

### Updating the site

- Commit and push changes to `docs/index.html` on `main`; Pages will auto-redeploy within 1–2 minutes.

### Optional: Custom domain

- Add your domain in GitHub: Settings → Pages → Custom domain.
- Create a DNS CNAME record pointing to `blossomz37.github.io`.
- Add a `docs/CNAME` file containing your domain to persist it in the repo.

## For Indie Authors and Publishers

This project addresses common challenges faced by indie authors:

- **Progress Tracking**: Monitor daily writing goals and long-term project milestones
- **Productivity Analytics**: Understand writing patterns and optimize workflows
- **AI Integration**: Leverage Claude's capabilities for writing assistance and project management
- **Workflow Automation**: Reduce manual tasks and focus on creative work

## Technology Stack

- **Python**: Core implementation language
- **Model Context Protocol (MCP)**: For AI tool integration
- **Claude Skills**: For enhanced AI interactions
- **Cross-platform libraries**: Ensuring compatibility across operating systems

## Contributing

We welcome contributions from the indie author and publisher community! Whether you're adding new features, fixing bugs, or improving documentation, your input helps make this project better for everyone.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Future Development

Planned enhancements include:

- Additional writing analysis tools
- Integration with popular writing software
- Enhanced analytics and reporting
- Community-driven skill marketplace
- Publishing workflow automation

## About Future Fiction Academy

This project was created by **Carlo V. Santiago** for the Future Fiction Academy, an organization dedicated to helping indie authors and publishers navigate the evolving landscape of digital publishing and AI-assisted writing.

### Learn More

- **Future Fiction Academy**: [https://futurefictionacademy.com/](https://futurefictionacademy.com/)
- **Latest Publications**: [https://futurefictionpress.com/](https://futurefictionpress.com/)

Visit our website to discover more resources, tutorials, and tools designed specifically for the indie publishing community.

## License

This project is open source and available under the MIT License. See the LICENSE file for more details.

## Support

For questions, suggestions, or support:

- Check the documentation in each skill's folder
- Visit the Future Fiction Academy website
- Submit issues through GitHub

---

*Empowering indie authors and publishers with next-generation AI tools.*