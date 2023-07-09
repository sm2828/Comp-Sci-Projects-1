import requests
import re

url = "https://michaelgathara.com/api/python-challenge"

response = requests.get(url)
challenges = response.json()

# Solve the problems and print the answers
for challenge in challenges:
    problem_id = challenge['id']
    problem = challenge['problem']

    # Extract necessary information from the problem using regex pattern
    pattern = r'(\d+)\s*([-+*/])\s*(\d+)\?'
    match = re.match(pattern, problem)
    if match:
        first_number = int(match.group(1))
        operation = match.group(2)
        second_number = int(match.group(3))

        # Solve the problem based on the operation
        if operation == '+':
            answer = first_number + second_number
        elif operation == '-':
            answer = first_number - second_number
        elif operation == '*':
            answer = first_number * second_number
        elif operation == '/':
            if second_number != 0:
                answer = first_number / second_number
            else:
                print(f"Invalid problem #{problem_id}: Division by zero error")
                continue
        else:
            print(f"Invalid problem #{problem_id}: Unsupported operation '{operation}'")
            continue

        # Print the problem and its answer
        print(f"Problem #{problem_id}: {problem} = {answer}")
    else:
        print(f"Invalid problem #{problem_id}: Invalid format")

# Add your name and Blazer ID at the top
print("\nName: Sean-Morgan Neville")
print("Blazer ID: seannev")
