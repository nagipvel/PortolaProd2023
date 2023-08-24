#!/usr/bin/python3
from boxsdk import JWTAuth, Client
from boxsdk.object.collaboration import CollaborationRole


class boxClient:

    def __init__(self):
        self.getClient() #connect on creation

    def getClient(self):
        auth = JWTAuth.from_settings_file('boxTokens.txt')
        self.client = Client(auth)
        service_account = self.client.user().get()
        print('Service Account logged in as user ID {0}'.format(service_account.id))

    def getManagedUsers(self):
        '''
        returns a dictionary of users by email
        '''
        userDict={}
        users = self.client.users(user_type='managed')
        for user in users:
            print('{0} (User ID: {1} Email: {2} )'.format(user.name, user.id, user.login))
            userDict[user.login] = user.id
        return userDict

    def collaborateWithUser(self, user_id='6877343957'):
        '''
        user_id is defaulted to mark.davis@pvel.com as the user to colab
        this code is a stub for later
        '''
        user = self.client.user(user_id=self.user_id) # That's me
        collaboration = self.client.folder(folder_id='72911007945').collaborate(user, CollaborationRole.VIEWER)

        collaborator = collaboration.accessible_by
        item = collaboration.item
        has_accepted = 'has' if collaboration.status == 'accepted' else 'has not'
        print('{0} {1} accepted the collaboration to folder "{2}"'.format(collaborator.name, has_accepted, item.name))

    def downloadFile(self):
        pass

    def uploadFile(self, folder_id, file):
        new_file = self.client.folder(folder_id).upload(file)
        print('File "{0}" uploaded to Box with file ID {1}'.format(new_file.name, new_file.id))
        return new_file.id

    def updateFile(self, file_id, file):
        updated_file = self.client.file(file_id).update_contents(file)
        print('File "{0}" has been updated'.format(updated_file.name))


def main():
    myClient = boxClient()

    # remember if you're calling underlying box APIs they are behind the class
    root_folder = myClient.client.root_folder().get()
    items = root_folder.get_items()
    # Create folder
    # folder = boxClient.root_folder().create_subfolder('FOO') # folder_id:72911007945

    for item in items:
        print('{0} {1} is named "{2}"'.format(item.type.capitalize(), item.id, item.name))

    try:
        # this only works when creating a new file
        myClient.uploadFile('72911007945','README.md')
    except:
        # file of the same name exists, need to extract ID from error
        myClient.updateFile('438352948424','README.md')

    # userDict = getManagedUsers(boxClient)
    # print(userDict)

if __name__ == '__main__':
    main()


'''
time to think about whath this is going to do.
post_receive this script will get called

login to box
get the list of files committed
for each file:
    push them to the right place on box
logout

'''
