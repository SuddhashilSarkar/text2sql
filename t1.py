# test_protocol_recognizer.py
from pr_engine import ProtocolClassifier
import json

def run_tests():
    # Initialize classifier
    classifier = ProtocolClassifier()
    
    # Test cases: (query, expected_protocol)
    test_cases = [
        ("Show me recent sales", "10"),
        ("Plot monthly revenue as bars", "12"),
        ("Insert new customer John Doe", "21"),
        ("Update prices for electronics", "22"),
        ("Delete user ID 456", "23"),
        ("Create table inventory", "31"),
        ("List all tables", "41"),
        ("Describe customers table", "42"),
        ("Truncate log entries", "34"),
        ("Make pretty graph", "12"),  # Ambiguous case
        ("Random gibberish", "00")    # Error case
    ]

    print("🚀 Starting Protocol Recognition Tests\n")
    print(f"{'Query':<35} | {'Protocol':<8} | {'Improved Query':<40} | Status")
    print("-" * 110)

    for query, expected_protocol in test_cases:
        try:
            result = classifier.classify(query)
            
            # Validate structure
            assert all(k in result for k in ["protocol", "original_query", "improved_query", "metadata"])
            
            # Check protocol match
            status = "PASS" if result["protocol"] == expected_protocol else "FAIL"
            
            # Print results
            print(f"{result['original_query'][:30]:<35} | {result['protocol']:<8} | {result['improved_query'][:40]:<40} | {status}")
            
        except Exception as e:
            print(f"Error testing query '{query}': {str(e)}")
            continue

    print("\n✅ Test completed. Check protocol matches and query improvements!")

if __name__ == "__main__":
    run_tests()