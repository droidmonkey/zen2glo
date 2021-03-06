# zen2glo 

A live demo can be found here: https://zen2glo.dmapps.us

## Zen2Glo App Description

Zen2Glo is a migration tool used for importing zenhub workspaces and github repos directly to the Glo Boards.

Two included libraries, gloBoards.py and zenhub.py, were created to contain the business logic for their respective API calls.


## How to Use:

1) Press the Authorize Glo Access button and log in.

2) Authorize the GitHub Account and log in.

3) Enter the ZenHub API Access Token and log in. (To get ZenHub Access Token, use the link below or in the Zen2Glo App.)
This may take a moment to work.

4) Click the ZenHub Workspace you wish to import and select the destination Glo Board.

5) Press the Transfer Button!


## Problems:
We encountered two Glo API bugs that prevented us from completing a working product:

### 1) Edit Card Glo API Bug: 
Glo Board cards cannot be moved or editted.
We think the problem is, when a Glo Board is connected to GitHub, the cards cannot be moved or edited.

### 2) Cannot Determine if Card is Locked Github Integration Glo API Bug:
The Glo API has no way to tell if a Github repo is synced to a board, and what cards are locked because of it.


## How to generate your ZenHub API Access Token

Login to ZenHub and generate a ZenHub API Access Token here:
https://app.zenhub.com/dashboard/tokens

*Note: this link is included in the website where necessary.

Save the ZenHub API Access Token locally and enter it into the Zen2Glo Application when requested.

