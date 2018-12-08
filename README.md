# ELQuent

Combines multiple utilities automating tasks around Oracle's Eloqua Marketing Automation tool

---

## Main modules

### [ELQuent.link](utils/link.py)

#### Clean your links

- RegEx helper
- Quick deletion of Eloqua Tracking from links
- Quick swapping of UTM Tracking Scripts in links
- Allows to update or create e-mail with new code via ELQuent.api module

---

### [ELQuent.mail](utils/mail.py)

#### Constructs your email packages

- RegEx & API builder
- Automatically uploads images and adds image links, tracking scripts and pre-header to package
- Works with both HTML and MJML files
- Outputs HTML, MJML, updates e-mail or creates new one directly in Eloqua
- Uses PURL to ensure field merges on linked sites will be working
- Adds elqTrack=true to all viable link (PURL excluded)
- Swaps CDN URLs to SSL on the fly
- Special campaign sub-flow for externally generated mails

---

### [ELQuent.page](utils/page.py)

#### Create landing page

- RegEx work automator
- Allows user to automatically swap Eloqua Form in Landing Page
- Allows to use built-in landing page templates for quick deployment
- Adds lead by phone mechanism with conditional validation
- Cleans code, appends snippets, changes form code

---

### [ELQuent.campaign](utils/campaign.py)

#### Builds Eloqua Campaigns

- Built-in wizard creating campaigns from scratch (FORM, LP, EML, Campaign)
- Simple Email Campaign without canvas for newsletters and one-offs
- Basic campaign canvas for mail+reminder flows
- Content campaign canvas for e-book/webinar/code flows

_ToDo:_

- [ ] _Randomized subject & pre-header generator for technical e-mail_
- [ ] _When not recognized product name, try to find best matches from a list_

---

### [ELQuent.webinar](utils/webinar.py)

#### Add viewers to Eloqua

- ClickMeeting API connector app
- Allows user specify time range for webinar data import
- Automatically gets all needed data via API and restructures it
- Uploads contacts to Eloqua shared list via ELQuent.api module

_ToDo:_

- [ ] _Save date of last sync in shared content_
- [ ] _Save data to external activity_

---

### [ELQuent.database](utils/database.py)

#### Create Eloqua-compliant contact upload file

- Gets input from user
- Allows appending, trimming and intersecting e-mail uploads
- Outputs .csv file with correct structure and naming convention
- Uploads contacts to Eloqua shared list via ELQuent.api module
- Cleans data import dependency after succesful upload

---

### [ELQuent.export](utils/export.py)

#### Module focused on exporting data from Eloqua instance

- Gets all types of eloqua activity data for chosen timeframe
- Gets predefined campaign data from chosen timeframe
- Saves exported data to .json/.csv files

---

### [ELQuent.validator](utils/validator.py)

#### Module focused on validating assets & campaigns

- Exports active multistep campaigns with member count, start and end dates
- Basic campaign validation (fields, assets, steps)

---

### [ELQuent.modifier](utils/modifier.py)

#### Module for modification of multiple assets

- Adds redirect script to completed campaigns landing pages and saves list in shared content

---

### [ELQuent.cert](utils/cert.py)

#### Module focused on creating certificates for Eloqua campaigns

- From template.pdf and database.csv creates personalized certificates for every customer
- Automatically uploads them to Eloqua and gets tracked links for .pdf files
- Builds contact upload .csv with certificate link for field merging in communication

---

### [ELQuent.admin](utils/admin.py)

#### Specialized utils for core admins made on demand

- Creates forms and shared lists for e-mail group control based on country splitted json file
- Creates program canvas and automatically adds above assets to program steps
- Creates report on subscription related processings steps within eloqua forms
- Creates report on asset dependencies

---

## Helper modules

### [ELQuent.api](utils/api/api.py)

#### Helper module for Eloqua API

- Authenticates user
- Uploads contact database to Eloqua shared lists
- Cleans import definition after successful upload to clean dependecies
- Checks if LP, Form, Mail already exists on Eloqua instance
- Uploads landing page to specified folder
- Gets all necessary data to upload an e-mail
- Uploads e-mail to json specified folder
- Updates e-mail with new code
- Adds Eloqua tracking to e-mail links
- Uploads form to json specified folder
- Updates form with html, css and processing steps
- Gets form fields and form fills data
- Creates campaign and program canvas
- Creates shared filters
- Uploads and updates images
- Uploads and updates files in file storage
- Creates export definition for activity API and downloads data from it
- Refreshes and download segment counts
- Gets campaign data
- Gets user data
- Gets dynamic content
- Gets and updates shared content
- Gets and creates field merges
- Gets data model fields
- Gets email groups
- Gets asset dependencies

---

### [ELQuent.helper](utils/helper.py)

#### Helper module for Eloqua conventions

- Gets valid campaign name from user (according to predefined naming convention)
- Gets converting asset name for the campaign
- Gets link to the asset
- Gets promoted product name either from campaign name (via naming convention) or from user
- Gets optional header text
- Gets users via api module
- Changes date format from US to EU and the other way round
- Converts epoch to readable date format
- Convert readable date format to epoch
- Gets date from user and return epoch

---

Copyright (c) 2018 Mateusz Dąbrowski [MIT License](LICENSE)

[_Version: 1.9.6_]