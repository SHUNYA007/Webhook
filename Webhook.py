from fastapi import FastAPI, Request, HTTPException
import json
import os
import uvicorn

app = FastAPI()

data_store = {}
current_id = 0
previous_data_stores = []
data_file_path = "data_store.json"

def save_to_file():
    all_data = previous_data_stores + [data_store]
    with open(data_file_path, 'w') as file:
        json.dump(all_data, file)

def load_from_file():
    global data_store, previous_data_stores
    if os.path.exists(data_file_path):
        with open(data_file_path, 'r') as file:
            all_data = json.load(file)
            if all_data:
                previous_data_stores = all_data[:-1]
                data_store = all_data[-1]

@app.get("/save/")
async def save_data():
    save_to_file()
    return get_all_data()

@app.post("/data/")
async def create_data(request: Request):
    global current_id, data_store
    try:
        json_body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    headers = dict(request.headers)
    current_id += 1
    data_store[current_id] = {
        "headers": headers,
        "body": json_body
    }


    return {"id": current_id, "data": data_store[current_id], "latest_data_store": data_store}

@app.get("/")
@app.get("/data/")
def read_data():
    sorted_data = sorted(data_store.items(), key=lambda item: item[0], reverse=True)
    return [{"id": item[0], "data": item[1]} for item in sorted_data]

@app.get("/useNew/")
def use_new():
    global data_store, previous_data_stores, current_id
    previous_data_stores.append(data_store.copy())
    data_store = {}
    current_id = 0
    return {"message": "Started using a new dictionary", "previous_data_stores": previous_data_stores}

@app.get("/clear/")
def clear_data():
    global data_store, current_id
    data_store.clear()
    current_id = 0
    return {"message": "Current data store cleared", "current_data_store": data_store}

@app.get("/clearAll/")
def clear_all_data():
    global data_store, previous_data_stores, current_id
    data_store.clear()
    previous_data_stores.clear()
    current_id = 0
    return {"message": "All data stores cleared", "current_data_store": data_store, "previous_data_stores": previous_data_stores}

@app.get("/getAllData/")
def get_all_data():
    load_from_file()
    return {"all_data_stores": previous_data_stores + [data_store]}

if __name__ == '__main__':
    uvicorn.run(app, port=80, host='0.0.0.0')

