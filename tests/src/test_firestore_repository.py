"""
Test script for Firestore Repository

This script tests all methods of the FirestoreRepository class.
Run this script to verify that the Firestore repository is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.src.firestore_repository import FirestoreRepository


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")


def test_initialization():
    """Test repository initialization"""
    print_test_header("Repository Initialization")
    try:
        repo = FirestoreRepository()
        print_success("FirestoreRepository initialized successfully")
        return repo
    except Exception as e:
        print_error(f"Failed to initialize repository: {e}")
        return None


def test_get_all_conversations(repo: FirestoreRepository):
    """Test getting all conversations"""
    print_test_header("Get All Conversations")
    try:
        conversations = repo.get_conversations()
        print_success(f"Retrieved {len(conversations)} conversations")
        
        if conversations:
            print_info("Sample conversation:")
            sample = conversations[0]
            print(f"  ID: {sample['id']}")
            print(f"  Data keys: {list(sample['data'].keys())}")
        else:
            print_info("No conversations found in database")
        
        return True
    except Exception as e:
        print_error(f"Failed to get conversations: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_all_documents(repo: FirestoreRepository):
    """Test getting all documents from a collection"""
    print_test_header("Get All Documents (Generic Method)")
    try:
        documents = repo.get_all_documents('conversations')
        print_success(f"Retrieved {len(documents)} documents from 'conversations' collection")
        
        # Print first few documents
        for i, doc in enumerate(documents[:3], 1):
            print_info(f"\nDocument {i}:")
            print(f"  ID: {doc['id']}")
            print(f"  Data: {doc['data']}")
        
        if len(documents) > 3:
            print_info(f"... and {len(documents) - 3} more documents")
        
        return True
    except Exception as e:
        print_error(f"Failed to get all documents: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_document_by_id(repo: FirestoreRepository):
    """Test getting a document by ID"""
    print_test_header("Get Document by ID")
    try:
        # First, get all documents to find an ID
        all_docs = repo.get_all_documents('conversations')
        
        if not all_docs:
            print_info("No documents found, skipping get by ID test")
            return True
        
        # Use the first document's ID
        test_id = all_docs[0]['id']
        print_info(f"Testing with document ID: {test_id}")
        
        doc = repo.get_document_by_id('conversations', test_id)
        
        if doc:
            print_success(f"Retrieved document with ID: {doc['id']}")
            print_info(f"Document data keys: {list(doc['data'].keys())}")
        else:
            print_error(f"Document with ID {test_id} not found")
            return False
        
        # Test with non-existent ID
        non_existent = repo.get_document_by_id('conversations', 'non-existent-id-12345')
        if non_existent is None:
            print_success("Correctly returned None for non-existent document")
        else:
            print_error("Should have returned None for non-existent document")
            return False
        
        return True
    except Exception as e:
        print_error(f"Failed to get document by ID: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_documents(repo: FirestoreRepository):
    """Test querying documents with filters"""
    print_test_header("Query Documents")
    try:
        # Get all documents first to see what fields are available
        all_docs = repo.get_all_documents('conversations')
        
        if not all_docs:
            print_info("No documents found, skipping query test")
            return True
        
        print_info("Querying all documents (no filters)")
        results = repo.query_documents('conversations')
        print_success(f"Query returned {len(results)} documents")
        
        # Try a query with limit
        print_info("Querying with limit of 5")
        limited_results = repo.query_documents('conversations', limit=5)
        print_success(f"Limited query returned {len(limited_results)} documents")
        
        return True
    except Exception as e:
        print_error(f"Failed to query documents: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}Firestore Repository Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    # Initialize repository
    repo = test_initialization()
    if repo is None:
        print_error("Cannot proceed without repository initialization")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Get All Conversations", lambda: test_get_all_conversations(repo)),
        ("Get All Documents", lambda: test_get_all_documents(repo)),
        ("Get Document by ID", lambda: test_get_document_by_id(repo)),
        ("Query Documents", lambda: test_query_documents(repo)),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' raised an exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}Test Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print_success("\nAll tests passed! ✓")
        sys.exit(0)
    else:
        print_error(f"\n{total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

