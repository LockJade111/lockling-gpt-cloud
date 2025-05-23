import supabase
from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def check_permission(persona: str, required: str) -> bool:
    response = supabase.table("roles").select("permissions").eq("name", persona).execute()
    if not response.data:
        return False
    perms = response.data[0]["permissions"]
    return required in perms
