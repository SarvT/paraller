
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from supabase import create_client, Client
from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
OPENAI_KEY = os.environ.get("OPENAI_KEY")

app = FastAPI()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_KEY)

# CORS for React frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://paraller.vercel.app/"],  # frontend
    allow_credentials=True,
    allow_methods=["*"],  # include OPTIONS
    allow_headers=["*"],
)

class FormData(BaseModel):
    name: str
    email: str
    password: str  # required for register/login

class QueryRequest(BaseModel):
    query: str


@app.post("/submit")
async def submit(data: FormData):
    # Do something with data
    return {"message": f"Hello {data.name}, your email is {data.email}"}



@app.post("/register")
async def register(data: FormData):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not response.user:
            raise HTTPException(status_code=400, detail="User not created.")

        return {"message": "User registered successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
async def login(data: FormData):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        if not response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        return {
            "message": "Login successful",
            "user": response.user.email,
            "access_token": response.session.access_token
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/insights")
def get_store_and_sku_insights():
    try:
        two_weeks_ago = (datetime.now() - timedelta(weeks=2)).date().isoformat()

        # Inventory data (average on_shelf_availability)
        inventory_data = supabase.table("store_inventory")\
            .select("store_id,on_shelf_availability")\
            .gte("inventory_date", two_weeks_ago).execute().data
        df_inventory = pd.DataFrame(inventory_data)
        top_stores = df_inventory.groupby("store_id")["on_shelf_availability"].mean().nlargest(5).reset_index()

        # Store names
        store_ids = top_stores["store_id"].tolist()
        store_info = supabase.table("stores").select("store_id,store_name").in_("store_id", store_ids).execute().data
        df_stores = pd.DataFrame(store_info)
        top_stores = top_stores.merge(df_stores, on="store_id")

        # Sales data
        sales_data = supabase.table("sales")\
            .select("sku_id,units_sold")\
            .gte("date", two_weeks_ago).execute().data
        df_sales = pd.DataFrame(sales_data)
        lowest_skus = df_sales.groupby("sku_id")["units_sold"].sum().nsmallest(5).reset_index()

        # SKU names
        sku_ids = lowest_skus["sku_id"].tolist()
        sku_info = supabase.table("products").select("sku_id,sku_name").in_("sku_id", sku_ids).execute().data
        df_skus = pd.DataFrame(sku_info)
        lowest_skus = lowest_skus.merge(df_skus, on="sku_id")

        # Build prompt
        store_lines = "\n".join(f"{row.store_name} ({row.on_shelf_availability:.2f})"
                                for _, row in top_stores.iterrows())
        sku_lines = "\n".join(f"{row.sku_name} ({row.units_sold} sold)"
                              for _, row in lowest_skus.iterrows())

        prompt = f"""
        The five stores with the highest average on-shelf availability in the last two weeks are:
        {store_lines}

        The SKUs that sold the least in the last two weeks are:
        {sku_lines}
        """

        # Ask ChatGPT
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Summarize this insight in plain English:\n{prompt}"}
            ]
        )
        summary = response.choices[0].message.content

        return {
            "summary": summary,
            "stores": top_stores.to_dict(orient="records"),
            "skus": lowest_skus.to_dict(orient="records")
        }

    except Exception as e:
        return {"error": str(e)}
    

@app.post("/query")
def run_custom_query(request: QueryRequest):
    try:
        user_query = request.query

        # 🧠 Ask ChatGPT to generate SQL
        prompt = f"""
You are an expert SQL assistant. Convert the following English query into a SQL query for a PostgreSQL database.
Assume the following tables and their columns exist:

products(sku_id, sku_name, category)
household_visits(id, household_id, store_id, sku_id, visit_date)
store_inventory(id, store_id, sku_id, inventory_date, on_shelf_availability)
stores(store_id, store_name, region)
sales(id, store_id, sku_id, sales_date, units_sold)

User Query: "{user_query}"

Give ONLY the SQL query. Do not explain or return any text other than the SQL.
"""

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        # sql_query = response.choices[0].message.content.strip().strip("```sql").strip("```")
        sql_query = (
            response.choices[0].message.content
            .strip()
            .strip("```sql")
            .strip("```")
            .rstrip(";")  # <-- remove trailing semicolon
        )

        # 🧾 Run the SQL query on Supabase
        # result = supabase.rpc("run_raw_sql", {"sql": sql_query}).execute()
        result = supabase.rpc("run_raw_sql", {"sql": sql_query}).execute()
        if result.data:
            return {"sql": sql_query, "result": result.data}
        else:
            return {"error": "No data returned", "sql": sql_query}
        # if hasattr(result, "data"):
        #     return {"sql": sql_query, "result": result.data}
        # else:
        #     return {"error": "Failed to fetch data", "sql": sql_query}

    except Exception as e:
        return {"error": str(e)}