"""
Firebase Firestore Repository

This module provides a repository class for interacting with Firebase Firestore database.
It uses Firebase Admin SDK with service account credentials and provides methods for CRUD operations.
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreRepository:
    """
    Repository class for Firebase Firestore operations.
    
    Provides methods to:
    - Get all documents from a collection
    - Get a document by ID
    - Create documents
    - Update documents
    - Delete documents
    - Query documents with filters
    """
    
    def __init__(
        self,
        credentials_file: Optional[str] = None
    ):
        """
        Initialize the Firestore Repository.
        
        Args:
            credentials_file: Path to the Firebase service account credentials JSON file.
                           If None, uses default path: app/creds/ai-task-master-7dc79-firebase-adminsdk-fbsvc-9d2fe1e4e1.json
        """
        # Set default credentials path if not provided
        if credentials_file is None:
            # Get the path relative to the project root
            project_root = Path(__file__).parent.parent.parent
            credentials_file = str(
                project_root / "app" / "creds" / "ai-task-master-7dc79-firebase-adminsdk-fbsvc-9d2fe1e4e1.json"
            )
        
        # Initialize Firebase Admin SDK if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_file)
            firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        self.db = firestore.client()
    
    def get_all_documents(
        self,
        collection_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all documents from a collection.
        
        Args:
            collection_name: Name of the collection to query.
        
        Returns:
            List of dictionaries, each containing 'id' and 'data' keys.
            Format: [{'id': 'doc_id', 'data': {...}}, ...]
        
        Raises:
            Exception: If the query fails.
        """
        try:
            docs = self.db.collection(collection_name).stream()
            result = []
            for doc in docs:
                result.append({
                    'id': doc.id,
                    'data': doc.to_dict() or {}
                })
            return result
        except Exception as e:
            raise Exception(f"Failed to get all documents from {collection_name}: {e}")
    
    def get_document_by_id(
        self,
        collection_name: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID.
        
        Args:
            collection_name: Name of the collection.
            document_id: ID of the document to retrieve.
        
        Returns:
            Dictionary with 'id' and 'data' keys, or None if document doesn't exist.
            Format: {'id': 'doc_id', 'data': {...}}
        
        Raises:
            Exception: If the query fails.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return {
                    'id': doc.id,
                    'data': doc.to_dict() or {}
                }
            return None
        except Exception as e:
            raise Exception(f"Failed to get document {document_id} from {collection_name}: {e}")
    
    def create_document(
        self,
        collection_name: str,
        data: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """
        Create a new document in a collection.
        
        Args:
            collection_name: Name of the collection.
            data: Dictionary containing the document data.
            document_id: Optional document ID. If None, Firestore will auto-generate an ID.
        
        Returns:
            The ID of the created document.
        
        Raises:
            Exception: If the creation fails.
        """
        try:
            if document_id:
                doc_ref = self.db.collection(collection_name).document(document_id)
                doc_ref.set(data)
                return document_id
            else:
                doc_ref = self.db.collection(collection_name).document()
                doc_ref.set(data)
                return doc_ref.id
        except Exception as e:
            raise Exception(f"Failed to create document in {collection_name}: {e}")
    
    def update_document(
        self,
        collection_name: str,
        document_id: str,
        data: Dict[str, Any],
        merge: bool = True
    ) -> None:
        """
        Update an existing document.
        
        Args:
            collection_name: Name of the collection.
            document_id: ID of the document to update.
            data: Dictionary containing the fields to update.
            merge: If True, merges data with existing document. If False, replaces entire document.
        
        Raises:
            Exception: If the update fails.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            if merge:
                doc_ref.update(data)
            else:
                doc_ref.set(data)
        except Exception as e:
            raise Exception(f"Failed to update document {document_id} in {collection_name}: {e}")
    
    def delete_document(
        self,
        collection_name: str,
        document_id: str
    ) -> None:
        """
        Delete a document from a collection.
        
        Args:
            collection_name: Name of the collection.
            document_id: ID of the document to delete.
        
        Raises:
            Exception: If the deletion fails.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(document_id)
            doc_ref.delete()
        except Exception as e:
            raise Exception(f"Failed to delete document {document_id} from {collection_name}: {e}")
    
    def query_documents(
        self,
        collection_name: str,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents with filters, ordering, and limit.
        
        Args:
            collection_name: Name of the collection.
            filters: List of tuples (field, operator, value) for filtering.
                    Operators: '==', '!=', '<', '<=', '>', '>=', 'in', 'array-contains', etc.
                    Example: [('status', '==', 'active'), ('age', '>', 18)]
            order_by: Field name to order by.
            limit: Maximum number of documents to return.
        
        Returns:
            List of dictionaries, each containing 'id' and 'data' keys.
        
        Raises:
            Exception: If the query fails.
        """
        try:
            query = self.db.collection(collection_name)
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            result = []
            for doc in docs:
                result.append({
                    'id': doc.id,
                    'data': doc.to_dict() or {}
                })
            return result
        except Exception as e:
            raise Exception(f"Failed to query documents from {collection_name}: {e}")
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """
        Convenience method to get all documents from the 'conversations' collection.
        
        Returns:
            List of dictionaries, each containing 'id' and 'data' keys.
        """
        return self.get_all_documents('conversations')
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Convenience method to get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to retrieve.
        
        Returns:
            Dictionary with 'id' and 'data' keys, or None if not found.
        """
        return self.get_document_by_id('conversations', conversation_id)
    
    def create_conversation(
        self,
        data: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Convenience method to create a conversation.
        
        Args:
            data: Dictionary containing the conversation data.
            conversation_id: Optional conversation ID. If None, auto-generated.
        
        Returns:
            The ID of the created conversation.
        """
        return self.create_document('conversations', data, conversation_id)
    
    def update_conversation(
        self,
        conversation_id: str,
        data: Dict[str, Any],
        merge: bool = True
    ) -> None:
        """
        Convenience method to update a conversation.
        
        Args:
            conversation_id: ID of the conversation to update.
            data: Dictionary containing the fields to update.
            merge: If True, merges data with existing document.
        """
        self.update_document('conversations', conversation_id, data, merge)
    
    def delete_conversation(self, conversation_id: str) -> None:
        """
        Convenience method to delete a conversation.
        
        Args:
            conversation_id: ID of the conversation to delete.
        """
        self.delete_document('conversations', conversation_id)

