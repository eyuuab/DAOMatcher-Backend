import requests
import uuid

ENDPOINT= "http://localhost:8000"

# Helper Functions:

def login():
    payload = {
        "email": "test@Daomatcher.io",
        "password": "test@Daomatcher!"
    }
    response = requests.post(ENDPOINT + "/api/auth/login", json=payload)
    data = response.json()
    
    token = data['data']['token']
    user_info = data['data']['user']
    user_id = user_info['id']

    return {
        "user_id": user_id,
        "token": token
    }

def get_user():
    auth_data=login()
    headers = {
    "Authorization": f"Bearer {auth_data['token']}"
    }
    response= requests.get(ENDPOINT + f"/api/user/{auth_data['user_id']}", headers=headers)
    
    data= response.json()
    return data



# Test Functions:

def test_sign_up():
    email= uuid.uuid4().hex
    payload= {
    "display_name":"test user",
	"email": f"{email}test@Daomatcher.io",
	"password": "test@Daomatcher!"
    }
    sign_up_response= requests.post(ENDPOINT + "/api/auth/register", json=payload)
    assert sign_up_response.status_code == 200
    pass

def test_login():
    payload= {
	"email": "test@Daomatcher.io",
	"password": "test@Daomatcher!"
    }
    login_response= requests.post(ENDPOINT + "/api/auth/login", json=payload)
    assert login_response.status_code == 200
    pass



def test_get_user():
    auth_data=login()
    headers = {
    "Authorization": f"Bearer {auth_data['token']}"
    }
    get_user_response= requests.get(ENDPOINT + f"/api/user/{auth_data['user_id']}", headers=headers)
    assert get_user_response.status_code == 200
    pass
    

def test_update_user():
    auth_data=login()
    headers = {
    "Authorization": f"Bearer {auth_data['token']}"
    }

    payload={
        "api_key": "still nothing ye"
    }
    update_user_response= requests.put(ENDPOINT + f"/api/user/{auth_data['user_id']}", headers=headers, json=payload)
    assert update_user_response.status_code == 200, f"Expected status code 200 but got {update_user_response.status_code}"


     # Get the updated user info
    updated_user_data = get_user()
    if not updated_user_data:
        print("Failed to retrieve updated user data.")
        return

    # Compare the updated attribute
    assert updated_user_data['data']['api_key'] == payload['api_key'], (
        f"Expected api_key to be '{payload['api_key']}' but got '{updated_user_data['data']['api_key']}'"
    )
    pass
    

    