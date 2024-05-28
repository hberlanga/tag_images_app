from images_api import models

def transactional(func):
    '''Wrap function inside a database transactional env'''

    def wrapper(*args, **kwargs):
        try:
            conn = models.start_transaction()
            result = func(*args, conn=conn, **kwargs)
            models.end_transaction(conn)
            return result
        except Exception as e:
            print(f"Exception on transaction execution => {str(e)}")
            models.rollback_transaction(conn)
    return wrapper