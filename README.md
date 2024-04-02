### Start Backend
```shell script
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

### Start Frontend
#### Change directory
```shell script
cd frontend
```

#### Install dependencies (First time only)
```react
npm install 
npm run build
```
#### Start the server
```react
npm run dev
```




Write a python client that integrates with the Vectara API. Use websockets for realtime updates of the query endpoint used in a user chat. The client will also need to lookup the corpus name using 'GET corpus' so the user can select the appropriate corpus for the chat. 

Write a python function that finds all properties with a key of 'intf' within all nested child objects and return a list of all key value pairs that match. 