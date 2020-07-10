import operator as op

def convertHex(val,nbits):
    """ Function to convert an integer number to hex
    @val: integer value to convert
    @nbits: number of bits (important for negative values)
    @return: value represented in hex
    """
    return hex((val + (1 << nbits)) % (1 << nbits))
    
    
def twos_to_dec(val, nbits):
    """"
    Function to convert a 2s complement number to decimal form
    
    Args:
        val (int): integer value in 2s complement format
        nbits (int): number of bits
    
    Return:
        dec (int): Decimal number representation
    """
    if val > (2**(nbits-1))-1:
        # number is negative
        dec = ((~val & (2**nbits)-1) + 1) * -1
    else:
        dec = val
        
    return dec
    
    
def clamp(value,min,max,returnType='int'):
    """ Function to clamp a numeric value and return the result 
    @value: value to be clamped
    @min: minimum allowable value
    @max: maximum allowable value
    @returnType: int, float
    
    @return: clamped value of the appropriate type
    """
    value = min if value < min else value
    value = max if value > max else value
    
    if returnType.lower() == 'float':
        return float(value)
    else:
        return int(value)
        
    
    
def inRange(value,Min,Max):
    """ Function to determine if a value is in between a min/max range
    
    Args:
        value (float, list): value (or list of values) to be tested
        Min (float): minimum value in range
        Max (float): maximum value in range
        
    Returns:
        result (bool): True if value is in range [Min Max] else false
    """
    if type(value) is type(list()):
        #iterate over the list
        for val in value:
            if (val < Min) or (val > Max):
                return False
        return True     #got through list without returning false, so return true
        
    else:
        if (value >= Min) and (value <= Max):
            return True
        else:
            return False
        
     
def validateList(dataList,compareType,limit):
    """ Function to check if a list of data meets the 'compareType' criteria relative to 'limit'
    @dataList: list of data to check
    @compareType: '>', '<', '>=', '<=','=','!='
    @limit: value to compare against, can be a single value or 2 element list in the form [min, max]
            if limit is a list, the compareType is ignored and the validation will see if all 'dataList' values are 
            in the range: max >= dataList >= min
    """
    o = {'>':op.gt,'>=':op.ge,'<':op.lt,'<=':op.le,'=':op.eq,'!=':op.ne}
    if type(limit) is list:
        if len(limit) != 2:
            raise Exception('argument "limit" is list type but length is %d - valid length is 2' %len(limit))
        else:
            min = limit[0]
            max = limit[1]
            for val in dataList:
                if val < min or val > max:
                    return False    #data point failed
            
            return True     #all data points passed
    
    else:
        #assume limit is a single number
        mop = o[compareType]    #get the math operator binding
        for val in dataList:
            if mop(val,limit):
                #data point passed
                pass
            else:
                return False    #data point didn't meet critera
        
        return True
        
               