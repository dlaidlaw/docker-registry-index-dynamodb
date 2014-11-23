# -*- coding: utf-8 -*-
'''Simple utilities for dealing with DynamoDB tables
'''

from boto.dynamodb2.table import Table

from time import sleep

def describe(table):
    """Get the table description if the table exists, assume that any exception
    means that the table does not exist and return None.
    """
    try:
        return table.describe()
    except:
        return None

def table_exists(table):
    """Check for table existence. The table exists if the describe(table)
    call returns a description and the table status is not 'DELETING'.
    """
    descrip = describe(table)
    if descrip is None:
        return False
    if descrip['Table']['TableStatus'] == 'DELETING':
        return False
    return True
    
def create_table_if_not_exists(table, waitForDeleting=True, maxAttempts=1, waitTime=0.5):
    """Create a table if it does not exist, and return its description. Note that this
    method does not wait until the table is actually created by the Amazon framework,
    it merely makes the request, if the table does not already exist.
    
    waitForDeleting defaults to True, and will wait until a table being deleted by the
    Amazon framework is deleted, before attempting to create it again. If set to False 
    the description may be returned with 'DELETING' as the table status.
    
    waitTime is the amount of time to wait for a deleting table to become deleted
    before testing again (unlimited number of checks for this), and the amount of
    time to pause between table creation attempts.
    
    maxAttempts is the maximum number of attemts to create the table. A pause of
    waitTime seconds is performed between each unsuccessful attempt. An attempt
    may be unsuccessful if another thread had already created the table. If maxAttempts
    is exceeeded, then None is returned. The default is to keep trying to create the table
    until it succeeds.
    """
    
    descrip = describe(table)
    if descrip is not None:
        if not waitForDeleting:
            return descrip
        # wait for the table to be deleted, that is, descrip == None
        while descrip is not None and descrip['Table']['TableStatus'] == 'DELETING':
            sleep(waitTime)
            descrip = describe(table)

    createAttempts = 0
    while descrip is None and (maxAttempts <= 0 or createAttempts < maxAttempts):
        ++createAttempts
        try:
            Table.create(table.table_name,
                        table.schema,
                        table.throughput,
                        table.indexes,
                        table.global_indexes,
                        table.connection)
        except:
            # no description, can't create, try again
            # print 'create table exception, pausing for 0.5 seconds'
            sleep(waitTime)
        descrip = describe(table)
                    
    return descrip

    
def wait_for_table_active(table, waitTime=0.5, maxAttempts=0):
    """Waits for the status of the table to become ACTIVE. Note that it is assumed
    that the table exists. If it does not, then an exception will be thrown from boto.
    Boto is used to query the Amazon framework for the table status via the table
    describe() method.
    
    maxAttempts is the number of queries sent to boto. A
    pause of waitTime is made between each query. Set this to 0 (the default) to keep
    trying forever.
    
    waitTime is the number of seconds to pause between queries to boto.
    """
    # print 'waiting for table ', table.table_name
    ready = table.describe()['Table']['TableStatus'] == 'ACTIVE'
    count = 0
    while not ready and (maxAttempts <= 0 or count < maxAttempts):
        ++count
        if (count >= 2 * 60 * 2):
            break
        sleep(waitTime)
        descrip = table.describe()
        ready = descrip['Table']['TableStatus'] == 'ACTIVE'
