# ELQuent
Combines multiple utilities automating tasks around Oracle's Eloqua Marketing Automation tool

---
## ELQuent.link
__Clean your links__
- RegEx helper
- Quick deletion of Eloqua Tracking from links
- Quick swapping of UTM Tracking Scripts in links

_ToDo:_
- _Catching wrong input (proper HTML with inproper UTM codes) - currently Index Error on line 155_

---
## ELQuent.page
__Create landing page__
- RegEx work automator
- Allows user to automatically swap Eloqua Form in Landing Page
- Allows to use built-in landing page templates for quick deployment
- Built-in wizard creating all Landing Pages required for campaign
- Cleans code, appends snippets, changes form code

_ToDo:_
- _Automated solution to upload created LPs to Eloqua_
- _Change from two (one and two column) LP templates to just one modular template_
- _When not recognized product name, try to find best matches from a list_

---
## ELQuent.webinar
__Add viewers to Eloqua__
- ClickMeeting API connector app
- Allows user specify time range for webinar data import
- Automatically gets all needed data via API and restructures it
- Uploads contacts to Eloqua shared list via ELQuent.api module

---
## ELQuent.database
__Create Eloqua-compliant contact upload file__
- Gets input from user
- Allows appending, trimming and intersecting e-mail uploads
- Outputs .csv file with correct structure and naming convention
- Uploads contacts to Eloqua shared list via ELQuent.api module

_ToDo:_
- _Ability to take .xls or .csv as input_

---
# Helper modules

## ELQuent.api
__Helper module for Eloqua API__
- Authenticates user
- Upload contact database to Eloqua shared lists

_ToDo:_
- _Broaden API with LP, Email and Form uploads_

---

[_Version: 1.3.5_]