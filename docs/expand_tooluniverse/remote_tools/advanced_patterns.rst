Advanced Remote Tool Patterns
==============================

Learn advanced patterns for building robust, scalable remote tools and MCP servers.

Circuit Breaker Pattern
------------------------

Implement circuit breaker for resilient remote calls:

.. code-block:: python

   import time
   from enum import Enum
   from typing import Callable, Any

   class CircuitState(Enum):
       CLOSED = "closed"
       OPEN = "open"
       HALF_OPEN = "half_open"

   class CircuitBreaker:
       def __init__(self, failure_threshold=5, recovery_timeout=60):
           self.failure_threshold = failure_threshold
           self.recovery_timeout = recovery_timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED

       def call(self, func: Callable, *args, **kwargs) -> Any:
           """Execute function with circuit breaker protection."""
           if self.state == CircuitState.OPEN:
               if time.time() - self.last_failure_time > self.recovery_timeout:
                   self.state = CircuitState.HALF_OPEN
               else:
                   raise Exception("Circuit breaker is OPEN")

           try:
               result = func(*args, **kwargs)
               self._on_success()
               return result
           except Exception as e:
               self._on_failure()
               raise e

       def _on_success(self):
           self.failure_count = 0
           self.state = CircuitState.CLOSED

       def _on_failure(self):
           self.failure_count += 1
           self.last_failure_time = time.time()

           if self.failure_count >= self.failure_threshold:
               self.state = CircuitState.OPEN

   # Usage in MCP server
   from tooluniverse.smcp import SMCP

   mcp = SMCP()
   circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

   @mcp.tool("resilient_api_call")
   def resilient_api_call(url: str) -> dict:
       """Make API call with circuit breaker protection."""
       def make_request():
           import requests
           response = requests.get(url, timeout=10)
           response.raise_for_status()
           return response.json()

       try:
           result = circuit_breaker.call(make_request)
           return {"data": result, "status": "success"}
       except Exception as e:
           return {"error": str(e), "status": "failed"}

Load Balancing
--------------

Implement load balancing for multiple service instances:

.. code-block:: python

   import random
   import time
   from typing import List, Dict, Any

   class LoadBalancer:
       def __init__(self, instances: List[str], strategy="round_robin"):
           self.instances = instances
           self.strategy = strategy
           self.current_index = 0
           self.instance_weights = {instance: 1.0 for instance in instances}

       def get_instance(self) -> str:
           """Get next instance based on strategy."""
           if not self.instances:
               raise Exception("No instances available")

           if self.strategy == "round_robin":
               instance = self.instances[self.current_index]
               self.current_index = (self.current_index + 1) % len(self.instances)
               return instance
           elif self.strategy == "random":
               return random.choice(self.instances)
           elif self.strategy == "weighted":
               return self._weighted_selection()
           else:
               return self.instances[0]

       def _weighted_selection(self) -> str:
           """Select instance based on weights."""
           total_weight = sum(self.instance_weights.values())
           random_weight = random.uniform(0, total_weight)

           current_weight = 0
           for instance, weight in self.instance_weights.items():
               current_weight += weight
               if random_weight <= current_weight:
                   return instance

           return self.instances[0]

       def update_weight(self, instance: str, weight: float):
           """Update instance weight based on performance."""
           if instance in self.instance_weights:
               self.instance_weights[instance] = weight

   # Usage in MCP server
   load_balancer = LoadBalancer([
       "http://server1:8000",
       "http://server2:8000",
       "http://server3:8000"
   ], strategy="round_robin")

   @mcp.tool("load_balanced_request")
   def load_balanced_request(endpoint: str) -> dict:
       """Make request with load balancing."""
       instance = load_balancer.get_instance()
       url = f"{instance}/{endpoint.lstrip('/')}"

       try:
           import requests
           response = requests.get(url, timeout=10)
           response.raise_for_status()
           return {"data": response.json(), "instance": instance, "status": "success"}
       except Exception as e:
           return {"error": str(e), "instance": instance, "status": "failed"}

Retry with Exponential Backoff
------------------------------

Implement retry logic with exponential backoff:

.. code-block:: python

   import time
   import random
   from typing import Callable, Any, Optional

   class RetryWithBackoff:
       def __init__(self, max_retries=3, base_delay=1, max_delay=60, jitter=True):
           self.max_retries = max_retries
           self.base_delay = base_delay
           self.max_delay = max_delay
           self.jitter = jitter

       def execute(self, func: Callable, *args, **kwargs) -> Any:
           """Execute function with retry and exponential backoff."""
           last_exception = None

           for attempt in range(self.max_retries + 1):
               try:
                   return func(*args, **kwargs)
               except Exception as e:
                   last_exception = e
                   
                   if attempt == self.max_retries:
                       break

                   # Calculate delay with exponential backoff
                   delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                   
                   # Add jitter to prevent thundering herd
                   if self.jitter:
                       delay *= (0.5 + random.random() * 0.5)

                   time.sleep(delay)

           raise last_exception

   # Usage in MCP server
   retry_handler = RetryWithBackoff(max_retries=3, base_delay=1)

   @mcp.tool("retry_api_call")
   def retry_api_call(url: str) -> dict:
       """Make API call with retry logic."""
       def make_request():
           import requests
           response = requests.get(url, timeout=10)
           response.raise_for_status()
           return response.json()

       try:
           result = retry_handler.execute(make_request)
           return {"data": result, "status": "success"}
       except Exception as e:
           return {"error": str(e), "status": "failed"}

Caching Strategies
------------------

Implement various caching strategies:

.. code-block:: python

   import time
   import hashlib
   import json
   from typing import Any, Optional, Dict
   from functools import lru_cache

   class CacheManager:
       def __init__(self, ttl=300):  # 5 minutes default TTL
           self.cache = {}
           self.ttl = ttl

       def get(self, key: str) -> Optional[Any]:
           """Get value from cache if not expired."""
           if key in self.cache:
               value, timestamp = self.cache[key]
               if time.time() - timestamp < self.ttl:
                   return value
               else:
                   del self.cache[key]
           return None

       def set(self, key: str, value: Any):
           """Set value in cache with timestamp."""
           self.cache[key] = (value, time.time())

       def generate_key(self, *args, **kwargs) -> str:
           """Generate cache key from arguments."""
           key_data = {"args": args, "kwargs": sorted(kwargs.items())}
           key_string = json.dumps(key_data, sort_keys=True)
           return hashlib.md5(key_string.encode()).hexdigest()

   # Usage in MCP server
   cache_manager = CacheManager(ttl=600)  # 10 minutes

   @mcp.tool("cached_expensive_operation")
   def cached_expensive_operation(n: int, operation: str) -> dict:
       """Expensive operation with caching."""
       # Generate cache key
       cache_key = cache_manager.generate_key(n, operation)
       
       # Try to get from cache
       cached_result = cache_manager.get(cache_key)
       if cached_result:
           return {"result": cached_result, "cached": True, "status": "success"}

       # Perform expensive operation
       if operation == "fibonacci":
           result = fibonacci(n)
       elif operation == "prime_check":
           result = is_prime(n)
       else:
           return {"error": "Unknown operation", "status": "failed"}

       # Cache the result
       cache_manager.set(cache_key, result)
       
       return {"result": result, "cached": False, "status": "success"}

   def fibonacci(n: int) -> int:
       """Calculate nth Fibonacci number."""
       if n <= 1:
           return n
       return fibonacci(n-1) + fibonacci(n-2)

   def is_prime(n: int) -> bool:
       """Check if number is prime."""
       if n < 2:
           return False
       for i in range(2, int(n**0.5) + 1):
           if n % i == 0:
               return False
       return True

Rate Limiting
-------------

Implement rate limiting for API protection:

.. code-block:: python

   import time
   from collections import defaultdict, deque
   from typing import Dict, Deque

   class RateLimiter:
       def __init__(self, max_requests=100, window_size=60):
           self.max_requests = max_requests
           self.window_size = window_size
           self.requests: Dict[str, Deque] = defaultdict(deque)

       def is_allowed(self, client_id: str) -> bool:
           """Check if client is within rate limit."""
           now = time.time()
           client_requests = self.requests[client_id]

           # Remove old requests outside the window
           while client_requests and now - client_requests[0] > self.window_size:
               client_requests.popleft()

           # Check if under limit
           if len(client_requests) >= self.max_requests:
               return False

           # Add current request
           client_requests.append(now)
           return True

       def get_retry_after(self, client_id: str) -> int:
           """Get seconds until next request is allowed."""
           if not self.requests[client_id]:
               return 0

           oldest_request = self.requests[client_id][0]
           return int(self.window_size - (time.time() - oldest_request))

   # Usage in MCP server
   rate_limiter = RateLimiter(max_requests=10, window_size=60)  # 10 requests per minute

   @mcp.tool("rate_limited_operation")
   def rate_limited_operation(data: str, client_id: str = "default") -> dict:
       """Operation with rate limiting."""
       if not rate_limiter.is_allowed(client_id):
           retry_after = rate_limiter.get_retry_after(client_id)
           return {
               "error": "Rate limit exceeded",
               "retry_after": retry_after,
               "status": "rate_limited"
           }

       # Process the request
       result = f"Processed: {data}"
       return {"result": result, "status": "success"}

Health Checks and Monitoring
----------------------------

Implement comprehensive health checks:

.. code-block:: python

   import time
   import psutil
   from typing import Dict, Any, List

   class HealthChecker:
       def __init__(self):
           self.start_time = time.time()
           self.checks = []

       def add_check(self, name: str, check_func: callable):
           """Add a health check function."""
           self.checks.append((name, check_func))

       def get_health_status(self) -> Dict[str, Any]:
           """Get overall health status."""
           status = {
               "status": "healthy",
               "timestamp": time.time(),
               "uptime": time.time() - self.start_time,
               "checks": {}
           }

           all_healthy = True
           for name, check_func in self.checks:
               try:
                   check_result = check_func()
                   status["checks"][name] = {
                       "status": "healthy",
                       "result": check_result
                   }
               except Exception as e:
                   status["checks"][name] = {
                       "status": "unhealthy",
                       "error": str(e)
                   }
                   all_healthy = False

           if not all_healthy:
               status["status"] = "unhealthy"

           return status

   # Usage in MCP server
   health_checker = HealthChecker()

   def check_database():
       """Check database connectivity."""
       # Simulate database check
       return {"connected": True, "response_time": 0.05}

   def check_external_api():
       """Check external API availability."""
       # Simulate API check
       return {"available": True, "response_time": 0.1}

   def check_system_resources():
       """Check system resource usage."""
       cpu_percent = psutil.cpu_percent()
       memory_percent = psutil.virtual_memory().percent
       
       if cpu_percent > 90 or memory_percent > 90:
           raise Exception(f"High resource usage: CPU {cpu_percent}%, Memory {memory_percent}%")
       
       return {"cpu_percent": cpu_percent, "memory_percent": memory_percent}

   # Add health checks
   health_checker.add_check("database", check_database)
   health_checker.add_check("external_api", check_external_api)
   health_checker.add_check("system_resources", check_system_resources)

   @mcp.tool("health_check")
   def health_check() -> dict:
       """Comprehensive health check."""
       return health_checker.get_health_status()

   @mcp.tool("simple_health")
   def simple_health() -> dict:
       """Simple health check."""
       return {"status": "healthy", "timestamp": time.time()}

Async Operations
----------------

Implement async operations for better performance:

.. code-block:: python

   import asyncio
   import aiohttp
   from typing import List, Dict, Any

   async def fetch_data_async(url: str) -> Dict[str, Any]:
       """Fetch data asynchronously."""
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return await response.json()

   @mcp.tool("async_batch_requests")
   def async_batch_requests(urls: List[str]) -> dict:
       """Make multiple requests asynchronously."""
       async def fetch_all():
           tasks = [fetch_data_async(url) for url in urls]
           return await asyncio.gather(*tasks, return_exceptions=True)

       try:
           results = asyncio.run(fetch_all())
           
           successful = []
           failed = []
           
           for i, result in enumerate(results):
               if isinstance(result, Exception):
                   failed.append({"url": urls[i], "error": str(result)})
               else:
                   successful.append({"url": urls[i], "data": result})

           return {
               "successful": successful,
               "failed": failed,
               "total": len(urls),
               "status": "completed"
           }
       except Exception as e:
           return {"error": str(e), "status": "failed"}

   @mcp.tool("async_parallel_processing")
   def async_parallel_processing(data: List[Dict[str, Any]]) -> dict:
       """Process multiple items in parallel."""
       async def process_item(item: Dict[str, Any]) -> Dict[str, Any]:
           # Simulate async processing
           await asyncio.sleep(0.1)
           return {"processed": item, "result": f"processed_{item.get('id', 'unknown')}"}

       async def process_all():
           tasks = [process_item(item) for item in data]
           return await asyncio.gather(*tasks)

       try:
           results = asyncio.run(process_all())
           return {"results": results, "count": len(results), "status": "success"}
       except Exception as e:
           return {"error": str(e), "status": "failed"}

Testing Advanced Patterns
-------------------------

Test your advanced patterns:

.. code-block:: python

   import pytest
   import time
   from unittest.mock import patch, Mock

   class TestCircuitBreaker:
       def test_circuit_breaker_opens_after_failures(self):
           """Test circuit breaker opens after threshold failures."""
           breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
           
           def failing_func():
               raise Exception("Test failure")

           # First failure
           with pytest.raises(Exception):
               breaker.call(failing_func)
           assert breaker.state == CircuitState.CLOSED

           # Second failure - should open circuit
           with pytest.raises(Exception):
               breaker.call(failing_func)
           assert breaker.state == CircuitState.OPEN

       def test_circuit_breaker_recovers_after_timeout(self):
           """Test circuit breaker recovers after timeout."""
           breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
           
           def failing_func():
               raise Exception("Test failure")

           # Open circuit
           with pytest.raises(Exception):
               breaker.call(failing_func)
           assert breaker.state == CircuitState.OPEN

           # Wait for recovery
           time.sleep(0.2)
           
           # Should be half-open
           assert breaker.state == CircuitState.HALF_OPEN

   class TestLoadBalancer:
       def test_round_robin_selection(self):
           """Test round robin load balancing."""
           instances = ["server1", "server2", "server3"]
           lb = LoadBalancer(instances, strategy="round_robin")
           
           # Should cycle through instances
           assert lb.get_instance() == "server1"
           assert lb.get_instance() == "server2"
           assert lb.get_instance() == "server3"
           assert lb.get_instance() == "server1"

       def test_random_selection(self):
           """Test random load balancing."""
           instances = ["server1", "server2", "server3"]
           lb = LoadBalancer(instances, strategy="random")
           
           # Should return one of the instances
           result = lb.get_instance()
           assert result in instances

   class TestRateLimiter:
       def test_rate_limiting(self):
           """Test rate limiting functionality."""
           limiter = RateLimiter(max_requests=2, window_size=1)
           
           # First two requests should be allowed
           assert limiter.is_allowed("client1") == True
           assert limiter.is_allowed("client1") == True
           
           # Third request should be blocked
           assert limiter.is_allowed("client1") == False

       def test_rate_limiter_resets_after_window(self):
           """Test rate limiter resets after window."""
           limiter = RateLimiter(max_requests=1, window_size=0.1)
           
           # First request allowed
           assert limiter.is_allowed("client1") == True
           
           # Second request blocked
           assert limiter.is_allowed("client1") == False
           
           # Wait for window to reset
           time.sleep(0.2)
           
           # Should be allowed again
           assert limiter.is_allowed("client1") == True

Best Practices Summary
----------------------

**1. Error Handling**
- Use circuit breakers for external dependencies
- Implement retry with exponential backoff
- Provide meaningful error messages

**2. Performance**
- Use caching for expensive operations
- Implement load balancing for scalability
- Use async operations for I/O bound tasks

**3. Reliability**
- Add comprehensive health checks
- Implement rate limiting
- Monitor system resources

**4. Testing**
- Test all failure scenarios
- Use mocks for external dependencies
- Test under load conditions

**5. Monitoring**
- Log important operations
- Track performance metrics
- Set up alerts for failures

Next Steps
----------

* 🚀 **Contributing**: :doc:`../contributing/remote_tools` - Submit your advanced MCP server
* 📚 **Tutorial**: :doc:`tutorial` - Learn basic remote tool integration
* 🔧 **MCP Server**: :doc:`mcp_server` - Learn MCP server development
* 🔍 **Architecture**: :doc:`../reference/architecture` - Understand ToolUniverse internals

.. tip::
   **Advanced tip**: Start with basic patterns and gradually add complexity. Always test thoroughly and monitor performance in production!
