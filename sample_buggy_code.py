def calculate_average(numbers):
    total = 0

    for number in numbers:
        total = total + number

    return total / len(numbers)


scores = []
average = calculate_average(scores)

print("Average score:", average)