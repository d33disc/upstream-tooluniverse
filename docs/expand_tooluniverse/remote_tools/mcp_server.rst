MCP Server Development
======================

Learn how to create MCP (Model Context Protocol) servers for remote tool integration with ToolUniverse.

What is MCP?
------------

MCP is a standardized protocol for tool communication that allows:
- **Standardized Interface**: Consistent tool discovery and execution
- **Language Agnostic**: Servers can be written in any language
- **Scalable**: Support for multiple tools on one server
- **Secure**: Built-in authentication and error handling

MCP Server Basics
-----------------

**Server Structure:**
.. code-block:: text

   my_mcp_server/
   ├── server.py              # Main server file
   ├── tools.py               # Tool implementations
   ├── requirements.txt       # Dependencies
   ├── README.md              # Documentation
   └── docker-compose.yml     # Optional: Docker setup

Basic MCP Server
~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI
   from tooluniverse.smcp import SMCP
   import uvicorn

   app = FastAPI(title="My MCP Server")
   mcp = SMCP()

   @mcp.tool("text_processor")
   def text_processor(text: str, operation: str = "uppercase") -> dict:
       """Process text with various operations."""
       if operation == "uppercase":
           result = text.upper()
       elif operation == "lowercase":
           result = text.lower()
       elif operation == "reverse":
           result = text[::-1]
       else:
           raise ValueError(f"Unknown operation: {operation}")
       
       return {
           "result": result,
           "operation": operation,
           "original": text
       }

   @mcp.tool("calculator")
   def calculator(a: float, b: float, operation: str) -> dict:
       """Basic calculator operations."""
       if operation == "add":
           result = a + b
       elif operation == "subtract":
           result = a - b
       elif operation == "multiply":
           result = a * b
       elif operation == "divide":
           if b == 0:
               raise ValueError("Division by zero")
           result = a / b
       else:
           raise ValueError(f"Unknown operation: {operation}")
       
       return {
           "result": result,
           "operation": operation,
           "inputs": {"a": a, "b": b}
       }

   # Mount MCP endpoints
   app.mount("/mcp", mcp.app)

   if __name__ == "__main__":
       uvicorn.run(app, host="0.0.0.0", port=8000)

Advanced MCP Server with Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI, HTTPException, Depends
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   from tooluniverse.smcp import SMCP
   import os

   app = FastAPI(title="Secure MCP Server")
   mcp = SMCP()
   security = HTTPBearer()

   def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
       """Verify API token."""
       if credentials.credentials != os.getenv("MCP_API_TOKEN"):
           raise HTTPException(status_code=401, detail="Invalid token")
       return credentials.credentials

   @mcp.tool("secure_data_processing")
   def secure_data_processing(data: dict, token: str = Depends(verify_token)) -> dict:
       """Process sensitive data with authentication."""
       # Process data securely
       processed_data = {k: v * 2 for k, v in data.items()}
       return {"processed_data": processed_data, "status": "success"}

   @mcp.tool("health_check")
   def health_check() -> dict:
       """Health check endpoint (no auth required)."""
       return {"status": "healthy", "service": "secure_mcp_server"}

   app.mount("/mcp", mcp.app)

   if __name__ == "__main__":
       uvicorn.run(app, host="0.0.0.0", port=8000)

MCP Server with Database Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI
   from tooluniverse.smcp import SMCP
   import sqlite3
   import json
   from typing import List, Dict, Any

   app = FastAPI(title="Database MCP Server")
   mcp = SMCP()

   def get_db_connection():
       """Get database connection."""
       return sqlite3.connect("data.db")

   @mcp.tool("create_user")
   def create_user(name: str, email: str, age: int) -> dict:
       """Create a new user in the database."""
       try:
           conn = get_db_connection()
           cursor = conn.cursor()
           
           cursor.execute(
               "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
               (name, email, age)
           )
           
           user_id = cursor.lastrowid
           conn.commit()
           conn.close()
           
           return {
               "user_id": user_id,
               "name": name,
               "email": email,
               "age": age,
               "status": "created"
           }
       except Exception as e:
           return {"error": str(e), "status": "failed"}

   @mcp.tool("get_users")
   def get_users(limit: int = 10) -> dict:
       """Get users from the database."""
       try:
           conn = get_db_connection()
           cursor = conn.cursor()
           
           cursor.execute("SELECT * FROM users LIMIT ?", (limit,))
           users = cursor.fetchall()
           conn.close()
           
           return {
               "users": [
                   {"id": user[0], "name": user[1], "email": user[2], "age": user[3]}
                   for user in users
               ],
               "count": len(users)
           }
       except Exception as e:
           return {"error": str(e), "users": []}

   @mcp.tool("search_users")
   def search_users(query: str) -> dict:
       """Search users by name or email."""
       try:
           conn = get_db_connection()
           cursor = conn.cursor()
           
           cursor.execute(
               "SELECT * FROM users WHERE name LIKE ? OR email LIKE ?",
               (f"%{query}%", f"%{query}%")
           )
           users = cursor.fetchall()
           conn.close()
           
           return {
               "users": [
                   {"id": user[0], "name": user[1], "email": user[2], "age": user[3]}
                   for user in users
               ],
               "query": query,
               "count": len(users)
           }
       except Exception as e:
           return {"error": str(e), "users": []}

   app.mount("/mcp", mcp.app)

   if __name__ == "__main__":
       uvicorn.run(app, host="0.0.0.0", port=8000)

Error Handling and Validation
-----------------------------

Robust Error Handling
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from tooluniverse.smcp import SMCP
   from pydantic import BaseModel, ValidationError
   from typing import Optional

   app = FastAPI(title="Robust MCP Server")
   mcp = SMCP()

   class UserInput(BaseModel):
       name: str
       email: str
       age: Optional[int] = None

   @mcp.tool("create_user_robust")
   def create_user_robust(user_data: dict) -> dict:
       """Create user with robust validation and error handling."""
       try:
           # Validate input
           user = UserInput(**user_data)
           
           # Business logic validation
           if user.age and user.age < 0:
               return {
                   "error": "Age must be positive",
                   "field": "age",
                   "status": "validation_error"
               }
           
           if "@" not in user.email:
               return {
                   "error": "Invalid email format",
                   "field": "email",
                   "status": "validation_error"
               }
           
           # Simulate user creation
           user_id = hash(user.email) % 10000
           
           return {
               "user_id": user_id,
               "name": user.name,
               "email": user.email,
               "age": user.age,
               "status": "created"
           }
           
       except ValidationError as e:
           return {
               "error": "Validation failed",
               "details": str(e),
               "status": "validation_error"
           }
       except Exception as e:
           return {
               "error": "Internal server error",
               "details": str(e),
               "status": "server_error"
           }

   app.mount("/mcp", mcp.app)

Rate Limiting and Caching
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI, Request
   from tooluniverse.smcp import SMCP
   from functools import lru_cache
   import time
   from collections import defaultdict

   app = FastAPI(title="Rate Limited MCP Server")
   mcp = SMCP()

   # Simple in-memory rate limiter
   request_counts = defaultdict(list)
   RATE_LIMIT = 10  # requests per minute
   WINDOW_SIZE = 60  # seconds

   def check_rate_limit(client_ip: str) -> bool:
       """Check if client is within rate limit."""
       now = time.time()
       # Remove old requests outside the window
       request_counts[client_ip] = [
           req_time for req_time in request_counts[client_ip]
           if now - req_time < WINDOW_SIZE
       ]
       
       # Check if under limit
       if len(request_counts[client_ip]) >= RATE_LIMIT:
           return False
       
       # Add current request
       request_counts[client_ip].append(now)
       return True

   @mcp.tool("expensive_calculation")
   def expensive_calculation(n: int, request: Request) -> dict:
       """Expensive calculation with rate limiting and caching."""
       client_ip = request.client.host
       
       # Check rate limit
       if not check_rate_limit(client_ip):
           return {
               "error": "Rate limit exceeded",
               "retry_after": WINDOW_SIZE,
               "status": "rate_limited"
           }
       
       # Use cached result if available
       result = cached_calculation(n)
       
       return {
           "result": result,
           "input": n,
           "cached": True,
           "status": "success"
       }

   @lru_cache(maxsize=100)
   def cached_calculation(n: int) -> int:
       """Cached expensive calculation."""
       # Simulate expensive computation
       time.sleep(0.1)
       return sum(i * i for i in range(n))

   app.mount("/mcp", mcp.app)

Deployment Options
------------------

Docker Deployment
~~~~~~~~~~~~~~~~~

**Dockerfile:**
.. code-block:: dockerfile

   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

**docker-compose.yml:**
.. code-block:: yaml

   version: '3.8'
   services:
     mcp-server:
       build: .
       ports:
         - "8000:8000"
       environment:
         - MCP_API_TOKEN=your-secret-token
       volumes:
         - ./data:/app/data
       restart: unless-stopped

Cloud Deployment
~~~~~~~~~~~~~~~~

**Heroku (app.json):**
.. code-block:: json

   {
     "name": "my-mcp-server",
     "description": "MCP server for ToolUniverse",
     "image": "heroku/python",
     "addons": [
       {
         "plan": "heroku-postgresql:hobby-dev"
       }
     ],
     "env": {
       "MCP_API_TOKEN": {
         "description": "API token for authentication"
       }
     },
     "formation": {
       "web": {
         "quantity": 1,
         "size": "basic"
       }
     }
   }

**AWS Lambda (serverless.yml):**
.. code-block:: yaml

   service: mcp-server

   provider:
     name: aws
     runtime: python3.9
     region: us-east-1

   functions:
     api:
       handler: server.handler
       events:
         - http:
             path: /{proxy+}
             method: ANY
       environment:
         MCP_API_TOKEN: ${env:MCP_API_TOKEN}

Testing MCP Servers
-------------------

Unit Testing
~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from fastapi.testclient import TestClient
   from server import app

   client = TestClient(app)

   def test_text_processor():
       """Test text processing tool."""
       response = client.post("/mcp/tools/text_processor", json={
           "text": "hello",
           "operation": "uppercase"
       })
       
       assert response.status_code == 200
       data = response.json()
       assert data["result"] == "HELLO"
       assert data["operation"] == "uppercase"

   def test_calculator():
       """Test calculator tool."""
       response = client.post("/mcp/tools/calculator", json={
           "a": 10,
           "b": 5,
           "operation": "add"
       })
       
       assert response.status_code == 200
       data = response.json()
       assert data["result"] == 15

   def test_error_handling():
       """Test error handling."""
       response = client.post("/mcp/tools/calculator", json={
           "a": 10,
           "b": 0,
           "operation": "divide"
       })
       
       assert response.status_code == 200
       data = response.json()
       assert "error" in data

Integration Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests
   import time

   def test_server_integration():
       """Test full server integration."""
       base_url = "http://localhost:8000"
       
       # Test health check
       response = requests.get(f"{base_url}/mcp/tools/health_check")
       assert response.status_code == 200
       
       # Test tool discovery
       response = requests.get(f"{base_url}/mcp/tools")
       assert response.status_code == 200
       tools = response.json()
       assert "text_processor" in tools
       
       # Test tool execution
       response = requests.post(f"{base_url}/mcp/tools/text_processor", json={
           "text": "test",
           "operation": "uppercase"
       })
       assert response.status_code == 200
       data = response.json()
       assert data["result"] == "TEST"

Performance Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   import concurrent.futures

   def test_performance():
       """Test server performance under load."""
       base_url = "http://localhost:8000"
       
       def make_request():
           response = requests.post(f"{base_url}/mcp/tools/expensive_calculation", json={
               "n": 1000
           })
           return response.json()
       
       # Test with 10 concurrent requests
       start_time = time.time()
       
       with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
           futures = [executor.submit(make_request) for _ in range(10)]
           results = [future.result() for future in futures]
       
       end_time = time.time()
       duration = end_time - start_time
       
       print(f"10 requests completed in {duration:.2f} seconds")
       print(f"Average response time: {duration/10:.2f} seconds")
       
       # All requests should succeed
       assert all(result.get("status") == "success" for result in results)

Best Practices
--------------

**1. Error Handling**
- Always return structured error responses
- Include helpful error messages
- Log errors for debugging

**2. Input Validation**
- Validate all inputs thoroughly
- Use Pydantic models for complex validation
- Return clear validation error messages

**3. Performance**
- Implement caching for expensive operations
- Use async/await for I/O operations
- Add rate limiting for public APIs

**4. Security**
- Implement authentication for sensitive tools
- Validate and sanitize all inputs
- Use HTTPS in production

**5. Monitoring**
- Add health check endpoints
- Log important operations
- Monitor server performance

**6. Documentation**
- Document all tools and parameters
- Provide usage examples
- Include deployment instructions

Next Steps
----------

* 🔧 **Advanced Patterns**: :doc:`advanced_patterns` - Circuit breakers, load balancing, etc.
* 🚀 **Contributing**: :doc:`../contributing/remote_tools` - Submit your MCP server to ToolUniverse
* 📚 **Tutorial**: :doc:`tutorial` - Learn about remote tool integration
* 🔍 **Architecture**: :doc:`../reference/architecture` - Understand ToolUniverse internals

.. tip::
   **Development tip**: Start with simple servers and gradually add complexity. Test thoroughly and document everything!
