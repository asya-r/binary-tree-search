from dotenv import load_dotenv


def load_config(env_path):
    load_dotenv(env_path)


load_config("../.env/postgres.env")