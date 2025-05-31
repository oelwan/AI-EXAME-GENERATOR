"""
Python question bank module containing predefined questions for the Python programming quiz application.
"""

# Define the question bank as a dictionary of topics with corresponding difficulty levels
question_bank = {
    "Basic Python": {
        "Beginner": [
            {
                "type": "multiple_choice",
                "question": "What is the correct way to create a variable in Python?",
                "answers": [
                    "variable_name = value", 
                    "var variable_name = value", 
                    "dim variable_name as value", 
                    "set variable_name = value"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which of the following is NOT a built-in data type in Python?",
                "answers": [
                    "Array", 
                    "List", 
                    "Dictionary", 
                    "Tuple"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "What is the output of: print(2 + 3 * 4)?",
                "answers": [
                    "14", 
                    "20", 
                    "17", 
                    "Error"
                ],
                "correct_answer": 0
            }
        ],
        "Intermediate": [
            {
                "type": "multiple_choice",
                "question": "What does the 'self' parameter in Python class methods represent?",
                "answers": [
                    "The instance of the class", 
                    "The class itself", 
                    "A required keyword", 
                    "The parent class"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which of the following is NOT a valid way to create a list in Python?",
                "answers": [
                    "list(1, 2, 3)", 
                    "[1, 2, 3]", 
                    "list([1, 2, 3])", 
                    "list(range(1, 4))"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "What does the '[::-1]' slice notation do to a sequence in Python?",
                "answers": [
                    "Reverses the sequence", 
                    "Creates a copy of the sequence", 
                    "Removes the first and last elements", 
                    "Returns every other element"
                ],
                "correct_answer": 0
            }
        ],
        "Advanced": [
            {
                "type": "multiple_choice",
                "question": "What is a decorator in Python?",
                "answers": [
                    "A function that modifies the behavior of another function", 
                    "A class that inherits from multiple parent classes", 
                    "A design pattern for creating objects", 
                    "A function that executes asynchronously"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which statement correctly describes Python's GIL?",
                "answers": [
                    "It allows only one thread to execute Python bytecode at a time", 
                    "It manages memory allocation and garbage collection", 
                    "It optimizes code execution by just-in-time compilation", 
                    "It enforces strict typing in Python functions"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "What is the purpose of the '__slots__' attribute in a Python class?",
                "answers": [
                    "To limit the attributes that can be assigned to class instances", 
                    "To define abstract methods that must be implemented by subclasses", 
                    "To specify the order of attribute initialization", 
                    "To mark private attributes that shouldn't be accessed directly"
                ],
                "correct_answer": 0
            }
        ],
        "coding": {
            "Beginner": [
                {
                    "type": "coding",
                    "question": "Write a function that returns the sum of two numbers.",
                    "starter_code": "def add_numbers(a, b):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert add_numbers(1, 2) == 3\nassert add_numbers(-1, 1) == 0"
                },
                {
                    "type": "coding",
                    "question": "Write a function to check if a number is even or odd.",
                    "starter_code": "def is_even(number):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert is_even(2) == True\nassert is_even(3) == False\nassert is_even(0) == True"
                }
            ],
            "Intermediate": [
                {
                    "type": "coding",
                    "question": "Write a function that counts the frequency of each character in a string.",
                    "starter_code": "def char_frequency(text):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert char_frequency('hello') == {'h': 1, 'e': 1, 'l': 2, 'o': 1}\nassert char_frequency('') == {}"
                },
                {
                    "type": "coding",
                    "question": "Write a function to check if a string is a palindrome (reads the same forwards and backwards).",
                    "starter_code": "def is_palindrome(text):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert is_palindrome('racecar') == True\nassert is_palindrome('hello') == False\nassert is_palindrome('') == True"
                }
            ],
            "Advanced": [
                {
                    "type": "coding",
                    "question": "Implement a function that finds the longest common subsequence of two strings.",
                    "starter_code": "def longest_common_subsequence(str1, str2):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert longest_common_subsequence('ABCD', 'ACBAD') == 'ABD'\nassert longest_common_subsequence('ABCDEFG', 'ABCDEFG') == 'ABCDEFG'\nassert longest_common_subsequence('', 'ABC') == ''"
                },
                {
                    "type": "coding",
                    "question": "Implement a decorator that caches the results of a function call.",
                    "starter_code": "def memoize(func):\n    # Your code here\n    pass\n\n@memoize\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                    "test_cases": "# Test cases\nassert fibonacci(10) == 55\nassert fibonacci(20) == 6765"
                }
            ]
        }
    },
    "Data Structures": {
        "Beginner": [
            {
                "type": "multiple_choice",
                "question": "Which of the following data structures does NOT allow duplicate elements?",
                "answers": [
                    "Set", 
                    "List", 
                    "Tuple", 
                    "String"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which data structure in Python uses keys and values?",
                "answers": [
                    "Dictionary", 
                    "List", 
                    "Tuple", 
                    "Set"
                ],
                "correct_answer": 0
            }
        ],
        "Intermediate": [
            {
                "type": "multiple_choice",
                "question": "What is the time complexity of accessing an element in a Python dictionary?",
                "answers": [
                    "O(1)", 
                    "O(n)", 
                    "O(log n)", 
                    "O(n log n)"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which of the following is NOT an advantage of using linked lists over arrays?",
                "answers": [
                    "Faster random access to elements", 
                    "Dynamic size", 
                    "Easier insertion/deletion", 
                    "No need for contiguous memory"
                ],
                "correct_answer": 0
            }
        ],
        "Advanced": [
            {
                "type": "multiple_choice",
                "question": "Which data structure would be most efficient for implementing a priority queue?",
                "answers": [
                    "Heap", 
                    "Array", 
                    "Linked List", 
                    "Stack"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "What is the worst-case time complexity of inserting an element into a balanced binary search tree?",
                "answers": [
                    "O(log n)", 
                    "O(1)", 
                    "O(n)", 
                    "O(n²)"
                ],
                "correct_answer": 0
            }
        ],
        "coding": {
            "Beginner": [
                {
                    "type": "coding",
                    "question": "Write a function that reverses a list in-place.",
                    "starter_code": "def reverse_list(lst):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\ntest_list = [1, 2, 3, 4, 5]\nreverse_list(test_list)\nassert test_list == [5, 4, 3, 2, 1]"
                },
                {
                    "type": "coding",
                    "question": "Write a function that merges two sorted lists into a single sorted list.",
                    "starter_code": "def merge_sorted_lists(list1, list2):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert merge_sorted_lists([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]\nassert merge_sorted_lists([], [1, 2, 3]) == [1, 2, 3]"
                }
            ],
            "Intermediate": [
                {
                    "type": "coding",
                    "question": "Implement a stack using a list with push, pop, and peek operations.",
                    "starter_code": "class Stack:\n    def __init__(self):\n        # Your code here\n        pass\n    \n    def push(self, value):\n        # Your code here\n        pass\n    \n    def pop(self):\n        # Your code here\n        pass\n    \n    def peek(self):\n        # Your code here\n        pass\n    \n    def is_empty(self):\n        # Your code here\n        pass",
                    "test_cases": "# Test cases\nstack = Stack()\nassert stack.is_empty() == True\nstack.push(1)\nstack.push(2)\nassert stack.peek() == 2\nassert stack.pop() == 2\nassert stack.pop() == 1\nassert stack.is_empty() == True"
                },
                {
                    "type": "coding",
                    "question": "Implement a function to check if a string has balanced parentheses.",
                    "starter_code": "def has_balanced_parentheses(s):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert has_balanced_parentheses('()') == True\nassert has_balanced_parentheses('(()())') == True\nassert has_balanced_parentheses('(()') == False\nassert has_balanced_parentheses(')(') == False"
                }
            ],
            "Advanced": [
                {
                    "type": "coding",
                    "question": "Implement a function to detect a cycle in a linked list.",
                    "starter_code": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef has_cycle(head):\n    # Your code here\n    pass",
                    "test_cases": "# Helper function to create a linked list with a cycle\ndef create_linked_list_with_cycle(values, pos):\n    if not values:\n        return None\n    head = ListNode(values[0])\n    current = head\n    nodes = [head]\n    for i in range(1, len(values)):\n        current.next = ListNode(values[i])\n        current = current.next\n        nodes.append(current)\n    if pos >= 0 and pos < len(nodes):\n        current.next = nodes[pos]\n    return head\n\n# Test cases\nassert has_cycle(create_linked_list_with_cycle([1, 2, 3, 4], -1)) == False\nassert has_cycle(create_linked_list_with_cycle([1, 2, 3, 4], 1)) == True"
                }
            ]
        }
    },
    "Algorithms": {
        "Beginner": [
            {
                "type": "multiple_choice",
                "question": "What is the time complexity of a linear search algorithm?",
                "answers": [
                    "O(n)", 
                    "O(1)", 
                    "O(log n)", 
                    "O(n²)"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which sorting algorithm generally has the worst time complexity?",
                "answers": [
                    "Bubble Sort", 
                    "Quick Sort", 
                    "Merge Sort", 
                    "Heap Sort"
                ],
                "correct_answer": 0
            }
        ],
        "Intermediate": [
            {
                "type": "multiple_choice",
                "question": "What is the average time complexity of Quick Sort?",
                "answers": [
                    "O(n log n)", 
                    "O(n)", 
                    "O(n²)", 
                    "O(log n)"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which algorithm is best for finding the shortest path in a weighted graph?",
                "answers": [
                    "Dijkstra's algorithm", 
                    "Depth-First Search", 
                    "Breadth-First Search", 
                    "Binary Search"
                ],
                "correct_answer": 0
            }
        ],
        "Advanced": [
            {
                "type": "multiple_choice",
                "question": "What problem does the Knapsack algorithm solve?",
                "answers": [
                    "Maximizing value given weight constraints", 
                    "Finding the shortest path in a graph", 
                    "Sorting a list efficiently", 
                    "Finding the minimum spanning tree"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "Which of the following is NOT an NP-complete problem?",
                "answers": [
                    "Binary search", 
                    "Traveling Salesman Problem", 
                    "Satisfiability Problem", 
                    "Graph Coloring"
                ],
                "correct_answer": 0
            }
        ],
        "coding": {
            "Beginner": [
                {
                    "type": "coding",
                    "question": "Implement a linear search algorithm to find an element in a list.",
                    "starter_code": "def linear_search(arr, target):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert linear_search([1, 3, 5, 7, 9], 5) == 2\nassert linear_search([1, 3, 5, 7, 9], 6) == -1"
                },
                {
                    "type": "coding",
                    "question": "Implement a function to find the maximum element in a list.",
                    "starter_code": "def find_max(arr):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert find_max([1, 5, 3, 9, 7]) == 9\nassert find_max([-1, -5, -3]) == -1"
                }
            ],
            "Intermediate": [
                {
                    "type": "coding",
                    "question": "Implement a binary search algorithm.",
                    "starter_code": "def binary_search(arr, target):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert binary_search([1, 2, 3, 4, 5], 3) == 2\nassert binary_search([1, 2, 3, 4, 5], 6) == -1"
                },
                {
                    "type": "coding",
                    "question": "Implement the Bubble Sort algorithm.",
                    "starter_code": "def bubble_sort(arr):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\ntest_arr = [5, 2, 4, 1, 3]\nbubble_sort(test_arr)\nassert test_arr == [1, 2, 3, 4, 5]"
                }
            ],
            "Advanced": [
                {
                    "type": "coding",
                    "question": "Implement the Quick Sort algorithm.",
                    "starter_code": "def quick_sort(arr):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert quick_sort([5, 2, 4, 1, 3]) == [1, 2, 3, 4, 5]\nassert quick_sort([]) == []"
                },
                {
                    "type": "coding",
                    "question": "Implement a function to find the longest increasing subsequence in an array.",
                    "starter_code": "def longest_increasing_subsequence(arr):\n    # Your code here\n    pass",
                    "test_cases": "# Test cases\nassert longest_increasing_subsequence([10, 9, 2, 5, 3, 7, 101, 18]) == 4\nassert longest_increasing_subsequence([]) == 0"
                }
            ]
        }
    },
    "File Handling": {
        "Beginner": [
            {
                "type": "multiple_choice",
                "question": "Which mode should be used to open a file for both reading and writing?",
                "answers": [
                    "'r+'", 
                    "'w'", 
                    "'r'", 
                    "'a'"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "What does the 'with' statement do when used with file operations?",
                "answers": [
                    "Ensures the file is properly closed after operations", 
                    "Increases file operation speed", 
                    "Creates a backup of the file", 
                    "Restricts access to the file"
                ],
                "correct_answer": 0
            }
        ],
        "Intermediate": [
            {
                "type": "multiple_choice",
                "question": "Which method would you use to read a single line from a file?",
                "answers": [
                    "readline()", 
                    "read()", 
                    "readlines()", 
                    "fetch()"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "What is the purpose of the 'seek()' method in file handling?",
                "answers": [
                    "To move the file cursor to a specific position", 
                    "To search for a specific string in the file", 
                    "To count the number of lines in a file", 
                    "To check if a file exists"
                ],
                "correct_answer": 0
            }
        ],
        "Advanced": [
            {
                "type": "multiple_choice",
                "question": "Which module would you use for working with CSV files in Python?",
                "answers": [
                    "csv", 
                    "pandas", 
                    "tabular", 
                    "excel"
                ],
                "correct_answer": 0
            },
            {
                "type": "multiple_choice",
                "question": "What's the difference between 'r+' and 'w+' file modes?",
                "answers": [
                    "'r+' doesn't truncate the file while 'w+' does", 
                    "'r+' is read-only while 'w+' allows writing", 
                    "'r+' is faster than 'w+'", 
                    "There is no difference"
                ],
                "correct_answer": 0
            }
        ],
        "coding": {
            "Beginner": [
                {
                    "type": "coding",
                    "question": "Write a function to read a text file and return its contents as a string.",
                    "starter_code": "def read_file(filename):\n    # Your code here\n    pass",
                    "test_cases": "# This test assumes a file named 'sample.txt' with content 'Hello, world!'\n# For the purpose of testing, we'll create and remove this file\nimport os\n\nwith open('sample.txt', 'w') as f:\n    f.write('Hello, world!')\n\nassert read_file('sample.txt') == 'Hello, world!'\nos.remove('sample.txt')"
                },
                {
                    "type": "coding",
                    "question": "Write a function to count the number of lines in a text file.",
                    "starter_code": "def count_lines(filename):\n    # Your code here\n    pass",
                    "test_cases": "# Create a test file\nimport os\n\nwith open('lines.txt', 'w') as f:\n    f.write('Line 1\\nLine 2\\nLine 3')\n\nassert count_lines('lines.txt') == 3\nos.remove('lines.txt')"
                }
            ],
            "Intermediate": [
                {
                    "type": "coding",
                    "question": "Write a function to read a CSV file and return a list of dictionaries.",
                    "starter_code": "def read_csv(filename):\n    # Your code here\n    pass",
                    "test_cases": "# Create a test CSV file\nimport os\n\nwith open('data.csv', 'w') as f:\n    f.write('name,age\\nAlice,30\\nBob,25')\n\nresult = read_csv('data.csv')\nassert len(result) == 2\nassert result[0]['name'] == 'Alice'\nassert int(result[0]['age']) == 30\nos.remove('data.csv')"
                },
                {
                    "type": "coding",
                    "question": "Write a function to find and replace text in a file.",
                    "starter_code": "def find_and_replace(filename, old_text, new_text):\n    # Your code here\n    pass",
                    "test_cases": "# Create a test file\nimport os\n\nwith open('replace.txt', 'w') as f:\n    f.write('Hello, world!')\n\nfind_and_replace('replace.txt', 'world', 'Python')\nwith open('replace.txt', 'r') as f:\n    content = f.read()\nassert content == 'Hello, Python!'\nos.remove('replace.txt')"
                }
            ],
            "Advanced": [
                {
                    "type": "coding",
                    "question": "Write a function to recursively list all files in a directory and its subdirectories.",
                    "starter_code": "def list_all_files(directory):\n    # Your code here\n    pass",
                    "test_cases": "# Create a test directory structure\nimport os\nimport shutil\n\nos.makedirs('test_dir/subdir', exist_ok=True)\nwith open('test_dir/file1.txt', 'w') as f:\n    f.write('test')\nwith open('test_dir/subdir/file2.txt', 'w') as f:\n    f.write('test')\n\nfiles = list_all_files('test_dir')\nassert len(files) == 2\nassert any('file1.txt' in f for f in files)\nassert any('file2.txt' in f for f in files)\n\nshutil.rmtree('test_dir')"
                }
            ]
        }
    }
} 