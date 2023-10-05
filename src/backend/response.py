class Response:

    # Standard error codes and messages
    err_codes = {"success"           : ("Success.", 200),
                "no_network"         : ("Network with given ID is not present in the database.", 500),
                "no_snapshot"        : ("There is no snapshot of the given network taken at the given time.", 500),
                "no_user"            : ("User with given ID is not present in the database.", 500),
                "malformed_network"  : ("Provided network information is malformed.", 500),
                "malformed_settings" : ("Provided settings information is malformed.", 500),
                "malformed_device"   : ("Provided device information is malformed.", 500),
                "malformed_user"     : ("Provided user information is malformed.", 500),
                "dup_user"           : ("A user with that username already exists.", 500),
                "db_error"           : ("The database server encountered an error, please try again.", 500),
                "bad_input"          : ("Input was not numeric.", 500),
                "no_access"          : ("Current user does not have access to this resource.", 401),
                "malformed_auth"     : {"Provided authentication token is malformed.", 401},
                "expired_auth"       : {"Provided authenticaiton token has expired.", 401},
                "no_auth"            : {"No authentication token provided.", 401}}

    def __init__(self, code_str, content=""):

        if code_str not in self.err_codes.keys():
            print("[ERR ] Invalid err string: %s" % code_str)
            raise KeyError

        self.message, self.status = self.err_codes[code_str]
        self.content = content

    
    def to_json(self):

        return {"message" : self.message,
                "status"  : self.status,
                "content" : self.content}, self.status