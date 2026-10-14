from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from backend import run_travel_agent

# res = tavily_search("Best hotels in Thekkady")
# print(res)

# res = search_flights("Show flights from Bengaluru to Tokyo")
# print(res)

user_input = input("Enter travel request:")

response = run_travel_agent(
    user_input=user_input,
    thread_id="test-user"
)

print("\n final response:\n")
print(response['answer'])