# ELQuent
Combines multiple utilities automating tasks around Oracle's Eloqua Marketing Automation tool

_Interested in using this tool for your company? Can help with implementation_

---
## ELQuent.link
__Clean your links__
- RegEx helper
- Quick deletion of Eloqua Tracking from links
- Quick swapping of UTM Tracking Scripts in links
- Allows to update or create e-mail with new code via ELQuent.api module

---
## ELQuent.mail
__Constructs your email packages__
- RegEx & API builder
- Automatically adds image links, tracking scripts and pre-header to package
- Works with both HTML and MJML files

---
## ELQuent.page
__Create landing page__
- RegEx work automator
- Allows user to automatically swap Eloqua Form in Landing Page
- Allows to use built-in landing page templates for quick deployment
- Creates blindform for confirmation-ty-lp and automatically impelements it
- Built-in wizard creating all Landing Pages required for campaign
- Cleans code, appends snippets, changes form code

_ToDo:_
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
- Cleans data import dependency after succesful upload

_ToDo:_
- _Ability to take .xls or .csv as input_

---
# Helper modules

## ELQuent.api
__Helper module for Eloqua API__
- Authenticates user
- Upload contact database to Eloqua shared lists
- Cleans impor definition after successful upload to clean dependecies
- Checks if LP, Form, Mail already exists on Eloqua instance
- Upload landing page to specified folder
- Upload e-mail to json specified folder
- Update e-mail with new code
- Upload form to json specified folder
- Update form with html, css and processing steps

---

[_Version: 1.4.13_]