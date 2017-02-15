
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
import sys

if __debug__:
    from workflow import Workflow, ICON_WEB, web
    from workflow.notify import notify



# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_spreadsheet_cell(service, spreadsheetId, projectStr="misc"):
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
    dateCells = "C15:H15"
    for sheet in spreadsheet['sheets']:
        sheetTitle = sheet['properties']['title']
        rangeName = "%s!%s" % (sheetTitle, dateCells)
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values',[])
        colNum = 0
        # TODO: replace current year with actual cell year, see http://stackoverflow.com/q/42216491/766570
        for row in values:
            for column in row:
                dateStr = "%s %s" % (column, datetime.date.today().year)
                cellDate = datetime.datetime.strptime(dateStr, '%b %d %Y')
                if cellDate.date() == datetime.date.today():
                    return get_project_cell(service, spreadsheetId, projectStr, sheetTitle, colNum)

                colNum +=1

def get_sheet_title_and_column(service, spreadsheetId):
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
    dateCells = "C15:H15"
    for sheet in spreadsheet['sheets']:
        sheetTitle = sheet['properties']['title']
        rangeName = "%s!%s" % (sheetTitle, dateCells)
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values',[])
        colNum = 0
        # TODO: replace current year with actual cell year, see http://stackoverflow.com/q/42216491/766570
        for row in values:
            for column in row:
                dateStr = "%s %s" % (column, datetime.date.today().year)
                cellDate = datetime.datetime.strptime(dateStr, '%b %d %Y')
                if cellDate.date() == datetime.date.today():
                    return sheetTitle, colNum

                colNum +=1

def get_projects_and_hours_for_sheet(service, spreadsheetId, sheetTitle, colNum):
    projectCells = 'B16:B19'
    initialProjectCellIndex = 16
    rangeName = "%s!%s" % (sheetTitle, projectCells)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName, majorDimension='COLUMNS').execute()
    return result.get('values',[])[0], result.get('values',[])[colNum]

def get_project_cell(service, spreadsheetId, projectStr, sheetTitle, colNum):
    cols = ['c','d','e','f','g','h']
    columnLetter = cols[colNum]
    # it's not likely that there wil be more than 4 projects at a time
    # but if there is, do logic that fetches all rows before the "total hours" row starts
    projectCells = 'B16:%s19' % columnLetter
    initialProjectCellIndex = 16
    rangeName = "%s!%s" % (sheetTitle, projectCells)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName, majorDimension='COLUMNS').execute()
    projectNames = list(map((lambda x: x.lower()), result.get('values',[])[0]))
    rowIndex = [i for i, s in enumerate(projectNames) if projectStr.lower() in s][0]
    initialCellValue = result['values'][colNum+1][rowIndex]

    return sheetTitle, '%s%s' % (columnLetter, initialProjectCellIndex + rowIndex), float(initialCellValue), projectNames[rowIndex]





def py_main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1tRziPgOwgPBCYIQZuwa7Me1vk5_tfsAWb3mcpPICxEI'

    sheetTitle, column = get_sheet_title_and_column(service, spreadsheetId)
    projects, hours = get_projects_and_hours_for_sheet(service, spreadsheetId, sheetTitle, column)
    index = 0
    items = []
    for project in projects:
        #sys.stderr.write("project: " + project + "\n")
        items.add_item(title=project,
                    subtitle=hours[index],
                    icon=ICON_WEB,
                    autocomplete=project, )
        index+=1

    print(items)


def main(wf):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    #sys.stderr.write("Log this to the console\n")

    if len(wf.args):
#        sys.stderr.write("there ARE arguments!\n")
#        sys.stderr.write(wf.args[0]+"\n")
        query = wf.args[0]
    else:
#        sys.stderr.write("there are no arguments!\n")
        query = None


    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1tRziPgOwgPBCYIQZuwa7Me1vk5_tfsAWb3mcpPICxEI'

    sheetTitle, column = get_sheet_title_and_column(service, spreadsheetId)
    projects, hours = get_projects_and_hours_for_sheet(service, spreadsheetId, sheetTitle, column)
    index = 0
    for project in projects:
        #sys.stderr.write("project: " + project + "\n")
        wf.add_item(title=project,
                    subtitle=hours[index],
                    icon=ICON_WEB,
                    autocomplete=project, )
        index+=1

    wf.send_feedback()

    # sheetTitle, cell, initialCellValue, projectName = get_spreadsheet_cell(service, spreadsheetId, projectStr)
    # rangeName = '%s!%s:%s' % (sheetTitle, cell, cell)
    # values = [[initialCellValue + hours]]
    # body = {
    #         'values': values
    #        }
    # result = service.spreadsheets().values().update(
    #         spreadsheetId=spreadsheetId, range=rangeName, body=body, valueInputOption="USER_ENTERED").execute()
    #
    # notify('success!','you have added %s hours to "%s", totalling %s hours' % (hours, projectName, hours + initialCellValue))


if __name__ == '__main__':
    if __debug__:
        wf = Workflow()
        sys.exit(wf.run(main))
    else:
        py_main()



