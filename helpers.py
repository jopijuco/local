from app import db
from controller import session

def validate_user(id):
    validate_user = db.execute(f"SELECT s.id FROM stores AS s INNER JOIN business AS b ON s.business_id = b.id WHERE s.id = :store AND b.user_id = :user",
        store=id, user=session['user_id'])
    
    if int(id) is not validate_user[0]["id"]:
        return "You have no permission to access this page"