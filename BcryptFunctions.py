import bcrypt

def hashText(plainText):

    """
    Takes a plain value(passwords and secruity answers),
    hashes it using bcrypt, returns the hashed value as a string
    suitable for storing in a database
    """
    
    #defensive check, dont attempt to hash and empty input
    if plainText is None or plainText == '':
        return None
    
    #generate a salted bcrypt hash from the utf-8 encoded input
    hashed = bcrypt.hashpw(plainText.encode('utf-8'), bcrypt.gensalt())


    #convert bytes to string for database
    return hashed.decode('utf-8')

def checkHash(plainText, hashedText):
    #checks user input against a the bcrypt hash.
    #returns True if match, False otherwise.
    
    #both values must exist to perform comparison
    if plainText is None or hashedText is None:
        return False

    #encodes both values and use bcyrpty to verify the hash
    return bcrypt.checkpw(plainText.encode(), hashedText.encode('utf-8'))


