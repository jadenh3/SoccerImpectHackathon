# Contributing to the Soccer Data Analytics Hackathon with FAQ

## Getting Started

### 1. Fork This Repository

Click the "Fork" button in the top-right corner of this repository to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/SoccerImpectHackathon.git
cd SoccerImpectHackathon
```

### 3. Set Up Your Environment

**Using conda:**
```bash
conda env create -f environment.yml
conda activate soccer-hackathon
```

**Using pip:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Create Your Team Branch (Optional)

```bash
git checkout -b team-yourteamname
```

## Working on Your Project

### Directory Structure

Organize your work as follows:

```
your-fork/
├── notebooks/          # Your analysis notebooks
├── src/               # Python modules and scripts
├── figures/           # Generated visualizations
├── slides/            # Your presentation deck
├── data/              # Processed data only
└── README.md          # Update with your approach
```

### Code Quality

- Write clean, readable code with comments
- Use meaningful variable and function names
- Follow PEP 8 style guidelines for Python
- Test your code runs from a fresh environment

### Documentation

Your final repository should include:
- **README.md**: Clear explanation of your approach, methodology, and findings
- **Code comments**: Explain complex logic
- **Docstrings**: For functions and classes
- **Requirements**: `environment.yml` or `requirements.txt`

## FAQ

1. Can we use additional data sources?
  - Any open data sources, with proper citation, may be used to supplement the project.
2. How do we handle missing data?
  - How you handle missing data will be part of the judges assessment of the final deliverables for the project.
3. Can we collaborate across teams?
  - To maintain the spirit of competition, teams are asked to not collaborate on their projects.
4. What if we attempt both prompts?
  - Teams are welcome to attempt both prompts, but ultimately must choose a single prompt/track to submit to and present to judges.


## Submission Guidelines

### Before Submitting

Complete this checklist:

- [ ] Choose one prompt (A: Starting Eleven OR B: Player Valuation)
- [ ] Create slide deck (PDF, max 8 slides, clear visualizations)
- [ ] Update README.md with your approach and findings
- [ ] Ensure code is reproducible (test in fresh environment)
- [ ] Include `environment.yml` or `requirements.txt`
- [ ] Add open-source license (MIT or Apache 2.0)
- [ ] Document any AI tool usage
- [ ] Name files correctly: `TeamName_Hackathon2026.pdf`

### File Naming Convention

- Slide deck: `TeamName_Hackathon2026.pdf`
- Repository: Keep as `SoccerImpectHackathon` or rename to `TeamName-Soccer-Hackathon`

### What to Submit

1. **GitHub repository URL** (your fork with all code)
2. **Slide deck PDF** (uploaded to repository in `slides/` folder)

Detailed submission instructions will be provided during the first day of the conference/hackathon presentation day: **Friday, February 27, 2026**

## Code of Conduct

### Do's ✅

- Collaborate within your team (2-5 members recommended)
- Use IMPECT Open Data for non-commercial purposes
- Cite all sources and data providers
- Document AI tool usage (e.g., ChatGPT, GitHub Copilot)
  - For example: This file was created with help from Claude Sonnet 4.5
- Ask questions if you're stuck

### Don'ts ❌

- Copy another team's code or approach
- Use IMPECT data for commercial purposes
- Plagiarize or fail to cite sources
- Submit work after the deadline
- Work alone if struggling (form or join a team!)

## Getting Help

- **Technical questions**: Post in GitHub Issues or Discussions
- **Data questions**: Review `notebooks/getting-started.ipynb`
- **Kloppy documentation**: https://kloppy.pysport.org/
- **General inquiries**: northeasternsportsanalytics@gmail.com

## Tips for Success

1. **Start early** - Don't wait until the last minute
2. **Use the checkpoint** - Submit a draft by February 2, 2026 for feedback
3. **Focus on one thing well** - Better to nail one aspect than do many poorly
4. **Visualize effectively** - Clear, readable figures > complex but confusing ones
5. **Tell a story** - Your presentation should have a clear narrative
6. **Test reproducibility** - Have a teammate run your code from scratch
7. **Mind the rubric** - Review the judging criteria in the main README

## Questions?

Contact: **northeasternsportsanalytics@gmail.com**
