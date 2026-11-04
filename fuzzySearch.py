
def normalise(Text):

    """
    Normalise the text to make the search more reliable
    -converts all chars to lowercase
    -removes punctuation
    -keep on spaces and alphanuemreics
    -get rid of leading and ending whitespace
    """

    if Text is None:
        return ''
    
    return ''.join(c.lower() for c in Text if c.isalnum() or c.isspace()).strip()

def similarity(Query, Target):

    """
    Calculates a similarity score between two strings, returna  value between 1.0 and 0.0
    uses
    -strong prefix matching
    -weaker word level prefix matching
    -substring matching
    -character overlap scoring
    """

    #if empty no score can be made
    if not Query or not Target:
        return 0.0 
    
    #strong match- target starts with the query
    if Target.startswith(Query):
        return 1.0
    
    #medium/strong match- any word in teh target starats with the query
    for word in Target.split():
        if word.startswith(Query):
            return 0.9
        
    #weaker match - query appears anywhere in the target string
    if Query in Target:
        return 0.7
    
    #weak match- calculate character overlap between query and target
    Matches = sum(1 for c in Query if c in Target)

    #normalise score by string length to keep result between 0 and 1
    return Matches / max(len(Query), len(Target))

def PatientIndex(PatientRows):

    """
    Build an in memory searchable index of patient data
    each entry in the index has:
    -patient id
    -a fully normalised string containg earchable feilds
    (improves performance by avoiding repeated noramlisation)
    """

    Index = []

    for row in PatientRows:
        pid, fname, lname, dob, email, address, ph, atype = row

        #combines mutiple fields into one searcable string
        searchableText = f"""
            {fname or ''}
            {lname or ''}
            {email or ''}
            {address or ''}
        """

        #store patient id with normalised searchable text
        Index.append((pid, normalise(searchableText)))

    return Index



def FuzzySearchPatient(Query, index_patients, Threshold=0.3):

    """
    performs a fuzzzy search over th patient index
    -normalises the query
    -caluclates similarity scores for each patient
    -filters out weak matches using a threshold
    -returns patient ids ranked by similarity -highest first
    """

    Query = normalise(Query)
    Results = []

    for PatientID, NameText in index_patients:
        Score = similarity(Query, NameText)

        #only keep results that are above the threshold
        if Score >= Threshold:
            Results.append((Score, PatientID))

    Results.sort(reverse=True)

    return Results
    
