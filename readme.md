---
title: Study Buddy
emoji: 📚
colorFrom: purple
colorTo: gray
sdk: streamlit
sdk_version: 1.21.0
app_file: app.py
pinned: false
license: apache-2.0
---
# Study Buddy

## Introduction
------------
StudyBuddy is an AI study app for college students that transforms course material into customized content, designed to match students' learning styles, existing knowledge, and goals, promoting deeper understanding and comprehension.


## Installation
------------
# Step 1: Create the virtual environment
python -m venv ~/venv/studyenv

# Step 2: Create an alias for activating the virtual environment
alias pyld='source ~/venv/studyenv/bin/activate'

# Step 3: Activate the virtual environment
pyld

# Step 4: Install necessary packages
pip install -r requirements.txt

# Step 5: Run the application
streamlit run app.py
