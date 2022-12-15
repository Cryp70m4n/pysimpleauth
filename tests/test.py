import sys
sys.path.append('../src')

from pysimpleauth import PySimpleAuth
import time

authorisation = PySimpleAuth("pysimpleauth", "root", "S3curE123#!", "127.0.0.1", 3306, "logs/auth.log")

def test():
    failures = []
    user = "test"
    auth = authorisation.generateAuthorisation(user, int(time.time())+5)
    authData = authorisation.getAuthorisationData(user)
    if auth == False:
        failures.append("generate auth test")
    if authData == False:
        failures.append("auth data test")
    if authData != False:
        if authData[0] != auth:
            failures.append("auth data test")
    if authorisation.authorisationExpiryCheck(auth) != True:
        failures.append("Expiry test")
    time.sleep(5)
    if authorisation.authorisationExpiryCheck(auth) != False:
        failures.append("Expiry test")
    if authorisation.deleteAuthorisation(auth) != True:
        failures.append("Delete auth test")

    return failures



print("[!] - Testing please wait...")
tests = test()
if len(tests) < 1:
    print("[+] - All testes passed!")
else:
    print(f"[X] - ({6-len(tests)}/6) passed")
    print("===FAILED TESTS===")
    for failure in tests:
        print(failure)

