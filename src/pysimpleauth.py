# CORE MODULES
import time
import secrets

# DATABASE MODULE
import mariadb

# UTILS
import logger

"""
 TO DO:
    - CONSIDER USING JSON FOR RETURN VALUES
"""

class PySimpleAuth:
    def __init__(self, db: str=None, dbUser: str=None, dbPassword: str=None, dbHost: str=None, dbPort: int=None, loggerPath: str=None):
        # LOGGER SETUP
        if loggerPath != None:
            try:
                logger.setupLogger('authLogger', r"{}".format(loggerPath))
                self.authLogger = logger.logging.getLogger('authLogger')
            except:
                self.authLogger = None
        else:
            self.authLogger = loggerPath
        #DB SETUP
        self.db = db
        self.dbUser = dbUser
        self.dbPassword = dbPassword
        self.dbHost = dbHost
        self.dbPort = dbPort
        try:
            self.connection = mariadb.connect(
                user=self.dbUser,
                password=self.dbPassword,
                host=self.dbHost,
                port = self.dbPort,
                database=self.db
            )
            self.cursor = self.connection.cursor()
        except mariadb.Error as mariadbError:
            raise mariadbError


    def throwError(self, errorCode: int=None, error: str=None):
        if self.authLogger != None:
            import inspect # this module is used to trace function names on stack so we import it only if logging is enabled
            if errorCode == None or error == None:
                return "errorCode or/and error cannot be None!"
            logError = "function:" + inspect.stack()[1][3] + " | " + "errorMessage:" + error.replace("\n", " | error:")
            match errorCode:
                case 1:
                    self.authLogger.warning(logError)
                case 2:
                    self.authLogger.debug(logError)
                case 3:
                    self.authLogger.error(logError)
                case 4:
                    self.authLogger.critical(logError)
                case _:
                    self.authLogger.critical("Invalid error code supplied!")
                    return "Invalid errorCode supplied to function throwError"
        return False

    def throwSuccess(self, success: str=None):
        if self.authLogger != None:
            self.authLogger.info(success)
        return True


    def authorisationExpiryCheck(self, authorisation: str=None):
        if authorisation == None:
            return self.throwError(2, "authorisation cannot be None!")
        sql = "SELECT expireDate FROM authorisations WHERE authorisation = ?"
        self.cursor.execute(sql, [authorisation])
        rows = self.cursor.fetchall()
        self.connection.commit()
        sqlRemove = "DELETE FROM authorisations WHERE authorisation = ?"
        if rows == []:
            return self.throwError(2, "INVALID authorisation!")
        authorisationExpireDate = rows[0][0]
        currentTime = int(time.time())
        if currentTime >= authorisationExpireDate:
            self.cursor.execute(sqlRemove, [authorisation])
            self.connection.commit()
            return self.throwError(1, "Expired authorisation")
        return self.throwSuccess("authorisation check completed!")

        
    def userAuthorisationAuthentication(self, user: str=None, authorisation: str=None):
        if user == None or authorisation == None:
            return self.throwError(2, "User and/or authorisation cannot be None!")
        sql = "SELECT authorisation FROM authorisations WHERE user = ?"
        self.cursor.execute(sql, [user])
        rows = self.cursor.fetchall()
        self.connection.commit()
        if rows == []:
            return self.throwError(1, "User error!\nGiven user were not found in database!")
        userAuthorisation = rows[0][0]
        print(userAuthorisation)
        print(authorisation)
        if userAuthorisation == authorisation:
            return self.throwSuccess("Authorised")
        return self.throwError(1, "Unauthorised")


    def generateAuthorisation(self, user: str=None, expireDate: int=None):
        if user == None or expireDate == None:
            return self.throwError(2, "User and/or expireDate cannot be None!")
        if expireDate < int(time.time()):
            return self.throwError(4, "EXPIRE DATE IS SMALLER THAN CURRENT TIME!")
        authorisation = secrets.token_urlsafe(32)
        authorisationCheck = "SELECT expireDate FROM authorisations WHERE user=?"
        self.cursor.execute(authorisationCheck, [user])
        authorisationExp = self.cursor.fetchall()
        self.connection.commit()
        if authorisationExp != []:
            if authorisationExp[0][0] > expireDate:
                return self.throwError(4, "EXPIRE DATE IS SMALLER THAN CURRENT AUTHROSATION EXPIRE TIME!")
            expireDate = expireDate+(authorisationExp[0][0]-int(time.time()))
            sql = "UPDATE IGNORE authorisations SET expireDate = ?"
            self.cursor.execute(sql, [expireDate])
            self.connection.commit()
            auth = "SELECT authorisation FROM authorisations WHERE user = ?"
            self.cursor.execute(auth, [user])
            rows = self.cursor.fetchall()
            self.connection.commit()
            return rows[0][0]
        duplicateAuthorisationCheck = "SELECT authorisation FROM authorisations WHERE authorisation=?"
        self.cursor.execute(duplicateAuthorisationCheck, [authorisation])
        rows = self.cursor.fetchall()
        self.connection.commit()
        if rows != []:
            return self.generateAuthorisation(user, expireDate)
        sql = "INSERT IGNORE INTO authorisations(user, authorisation, expireDate) VALUES(?, ?, ?)"
        self.cursor.execute(sql, [user, authorisation, expireDate])
        success = self.cursor.rowcount
        self.connection.commit()
        if success <= 0:
            return self.ThrowError(3, "SQL QUERY FAILURE!")
        self.throwSuccess(f"authorisation GENERATED SUCCESSFULLY FOR USER:{user}")
        return authorisation


    def getAuthorisationData(self, user: str=None):
        if user == None:
            return self.throwError(2, "User cannot be None!")
        sql = "SELECT authorisation, expireDate FROM authorisations WHERE user = ?"
        self.cursor.execute(sql, [user])
        rows = self.cursor.fetchall()
        self.connection.commit()
        if rows == []:
            return self.throwError(2, "User not found in database!")
        return rows[0]


    def deleteAuthorisation(self, authorisation: str=None):
        if authorisation == None:
            return self.throwError(2, "Authorisation cannot be None!")
        sql = "DELETE FROM authorisations WHERE authorisation = ?"
        self.cursor.execute(sql, [authorisation])
        self.connection.commit()
        return self.throwSuccess("AUTHORISATION DELETED SUCCESSFULLY!")

    def __del__(self):
        self.connection.close()
