from easygui import multenterbox

class Config:
    def __init__(self):
        self.name = ''
        self.host = ''

    def getConfigFromUser(self):
        title = "Configuration"
        msg = 'All fields are required'
        fieldNames = ['Player', 'Server']
        fieldValues = []
        fieldValues = multenterbox(msg, title, fieldNames)

        # make sure that none of the fields was left blank
        while 1:
            if fieldValues == None:
                break
            fieldValues = [val.strip() for val in fieldValues]
            errors = [1 for val in fieldValues if val == '']
            if not errors:
                self.name, self.host = fieldValues
                break
            fieldValues = multenterbox(msg, title, fieldNames, fieldValues)
