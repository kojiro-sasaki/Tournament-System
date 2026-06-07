from connection import supabase

try:
    response = (
        supabase
        .table("games")
        .select("*")
        .execute()
    )

    print("Database connection successful")
    print(response)

except Exception as e:
    print(f"Database connection failed: {e}")