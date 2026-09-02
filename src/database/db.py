from src.database.config import supabase
import bcrypt

def hash_pass(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def check_teacher_exists(username):
    # check for unique username, returns true when exists
    response = supabase.table("teachers").select('username').eq('username', username).execute()
    return len(response.data) > 0

def create_teacher(username, password,name):
    # create a new teacher with hashed password
    data = {
        "username": username,
        "password":hash_pass(password),
        "name": name
    }
    response = supabase.table("teachers").insert(data).execute()
    return response.data 


def teacher_login(username, password):
    # check if teacher exists and password matches
    response = supabase.table("teachers").select('*').eq('username', username).execute()
    if response.data:
        teacher = response.data[0]
        if check_password(password, teacher['password']):
            return teacher
    return None


def get_all_students():
    response = supabase.table("students").select('*').execute()
    return response.data