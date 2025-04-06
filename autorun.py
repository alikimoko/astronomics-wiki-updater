from updaters import run_all, set_client
from mwcleric import AuthCredentials, WikiggClient

if __name__ == "__main__":
    # Run update scripts in order
    set_client(WikiggClient("astronomics", credentials=AuthCredentials(user_file="me")))
    run_all()
