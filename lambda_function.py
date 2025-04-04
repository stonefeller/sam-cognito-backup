from email import header
import boto3
import datetime
from datetime import datetime
import time
import argparse
import traceback
import os

class Logs:
    @staticmethod
    def warning(logBody):
        print("[WARNING] {}".format(logBody))

    @staticmethod
    def critical(logBody):
        print("[CRITICAL] {}".format(logBody))

    @staticmethod
    def info(logBody):
        print("[INFO] {}".format(logBody))

class Cognito:

    # INIT userpool id, region and column names to be exported.
    # Currently region is not used. The export lambda must be in the same region as the Cognito service
    def __init__(self, userPoolId, region):
        self.COGNITO_ID = userPoolId
        self.REGION = region

    def getAttributes (self):
        try:
            boto = boto3.client('cognito-idp')
            headers = boto.get_csv_header(
                UserPoolId=self.COGNITO_ID
            )
            self.ATTRIBUTES = headers["CSVHeader"]
            return self.ATTRIBUTES
        except Exception as e:
            Logs.critical("There is an error listing users attributes")
            Logs.critical(traceback.format_exc())
            exit()

    # List all cognito users with only the predefined columns in ATTRIBUTES variable
    # As there is a limit of 60 users per query, a multiple queries are executed separated in so called pages.
    def listUsers (self):
        try:
            boto = boto3.client('cognito-idp')
            users = []
            next_page = None
            kwargs = {
                'UserPoolId': self.COGNITO_ID,
            }
            users_remain = True
            while(users_remain):
                if next_page:
                    kwargs['PaginationToken'] = next_page
                response = boto.list_users(**kwargs)
                users.extend(response['Users'])
                next_page = response.get('PaginationToken', None)
                users_remain = next_page is not None
                # COOL DOWN BEFORE NEXT QUERY
                time.sleep(0.15)

            return users
        except Exception as e:
            Logs.critical("There is an error listing cognito users")
            Logs.critical(traceback.format_exc())
            exit()

class CSV:
    FILENAME = ""
    FOLDER = "/tmp/"
    CSV_LINES = []

    # INIT titles and filename
    def __init__(self, attributes, prefix):
        self.ATTRIBUTES = attributes
        self.FILENAME = "cognito_backup_" + prefix + "_" + datetime.now().strftime("%Y%m%d-%H%M") + ".csv"
        self.CSV_LINES = []

    # Generate CSV content. Every column in a row is split with ","
    # First are added the titles and then all users are looped.
    def generateUserContent (self, records):
        try:
            #ADD TITLES
            csv_new_line = self.addTitles()

            #ADD USERS
            for user in records:
                """ Fetch Required Attributes Provided """
                csv_line = csv_new_line.copy()
                for requ_attr in self.ATTRIBUTES:
                    csv_line[requ_attr] = ''
                    if requ_attr in user.keys():
                        csv_line[requ_attr] = str(user[requ_attr])
                        continue
                    for usr_attr in user['Attributes']:
                        if usr_attr['Name'] == requ_attr:
                            csv_line[requ_attr] = str(usr_attr['Value'])
                csv_line["cognito:mfa_enabled"] = "false"
                csv_line["phone_number_verified"] = "false"
                csv_line["cognito:username"] = csv_line["email"]
                self.CSV_LINES.append(",".join(csv_line.values()) + '\n')
            return self.CSV_LINES
        except Exception as e:
            Logs.critical("Error generating csv content")
            Logs.critical(traceback.format_exc())
            exit()

    # Add titles to first row and return it as a template.
    def addTitles (self):
        csv_new_line = {self.ATTRIBUTES[i]: '' for i in range(len(self.ATTRIBUTES))}
        self.CSV_LINES.append(",".join(csv_new_line) + '\n')
        return csv_new_line

    # Save generated content to a file.
    def saveToFile(self):
        try:
            csvFile = open(self.FOLDER + "/" + self.FILENAME, 'a')
            csvFile.writelines(self.CSV_LINES)
            csvFile.close()
        except Exception as e:
            Logs.critical("Error saving csv file")
            Logs.critical(traceback.format_exc())
            exit()

class S3:
    BUCKET = ""
    REGION = ""

    # INIT bucket name and region. Currently region is not used.
    def __init__(self, bucket, region):
        self.BUCKET = bucket
        self.REGION = region

    # Upload file to s3 bucket
    def uploadFile(self, src, dest):
        try:
            boto3.resource('s3').meta.client.upload_file(src, self.BUCKET, dest)
        except Exception as e:
            Logs.critical("Error uploading the backup file")
            Logs.critical(traceback.format_exc())
            exit()

def lambda_handler(event, context):
    ### MAIN ###
    # VARIABLES
    REGION = os.environ['REGION']
    COGNITO_ID = os.environ['COGNITO_ID']
    BACKUP_BUCKET = os.environ['BACKUP_BUCKET']

    # INIT CLASSES
    cognito = Cognito(COGNITO_ID, REGION)
    cognitoS3 = S3(BACKUP_BUCKET, REGION)

    # GET USERS ATTRIBUTES AND INIT CSV CLASS
    ATTRIBUTES = cognito.getAttributes()
    csvUsers = CSV(ATTRIBUTES, "users")
    # LIST ALL USERS
    user_records = cognito.listUsers()
    # SAVE USERS TO FILE
    csvUsers.generateUserContent(user_records)
    csvUsers.saveToFile()
    # DISPLAY INFO
    Logs.info("Total Exported User Records: "+str(len(csvUsers.CSV_LINES)))
    # UPLOAD FILE
    cognitoS3.uploadFile (csvUsers.FOLDER + "/" + csvUsers.FILENAME, csvUsers.FILENAME)
