"""
AWS DynamoDB Database Setup and Operations
This module provides DynamoDB client initialization and common database operations
for the Food Agent App backend.
"""

import boto3
import logging
from typing import Any, Dict, List, Optional
from botocore.exceptions import ClientError
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)


class DynamoDBClient:
    """
    DynamoDB client wrapper for managing database connections and operations.
    """

    def __init__(self, region_name: str = "us-east-1", endpoint_url: Optional[str] = None):
        """
        Initialize DynamoDB client.

        Args:
            region_name: AWS region (default: us-east-1)
            endpoint_url: Optional endpoint URL for local DynamoDB testing
        """
        try:
            if endpoint_url:
                self.dynamodb = boto3.resource("dynamodb", region_name=region_name, endpoint_url=endpoint_url)
            else:
                self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
            logger.info(f"DynamoDB client initialized for region: {region_name}")
        except ClientError as e:
            logger.error(f"Failed to initialize DynamoDB client: {e}")
            raise

    def get_table(self, table_name: str) -> Any:
        """
        Get a reference to a DynamoDB table.

        Args:
            table_name: Name of the DynamoDB table

        Returns:
            DynamoDB table resource

        Raises:
            ClientError: If table doesn't exist
        """
        try:
            table = self.dynamodb.Table(table_name)
            table.load()  # Verify table exists
            return table
        except ClientError as e:
            logger.error(f"Failed to get table '{table_name}': {e}")
            raise

    def create_table(
        self,
        table_name: str,
        key_schema: List[Dict[str, str]],
        attribute_definitions: List[Dict[str, str]],
        billing_mode: str = "PAY_PER_REQUEST",
        global_secondary_indexes: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new DynamoDB table.

        Args:
            table_name: Name of the table to create
            key_schema: Primary key schema
            attribute_definitions: Attribute definitions
            billing_mode: Billing mode (PAY_PER_REQUEST or PROVISIONED)
            global_secondary_indexes: Optional GSI configuration
            **kwargs: Additional arguments (e.g., BillingMode, ProvisionedThroughput)

        Returns:
            Table creation response

        Raises:
            ClientError: If table creation fails
        """
        try:
            params = {
                "TableName": table_name,
                "KeySchema": key_schema,
                "AttributeDefinitions": attribute_definitions,
                "BillingMode": billing_mode,
                **kwargs
            }

            if global_secondary_indexes:
                params["GlobalSecondaryIndexes"] = global_secondary_indexes

            response = self.dynamodb.create_table(**params)
            logger.info(f"Table '{table_name}' creation initiated")
            return response
        except ClientError as e:
            logger.error(f"Failed to create table '{table_name}': {e}")
            raise

    def delete_table(self, table_name: str) -> Dict[str, Any]:
        """
        Delete a DynamoDB table.

        Args:
            table_name: Name of the table to delete

        Returns:
            Deletion response

        Raises:
            ClientError: If deletion fails
        """
        try:
            table = self.get_table(table_name)
            response = table.delete()
            logger.info(f"Table '{table_name}' deletion initiated")
            return response
        except ClientError as e:
            logger.error(f"Failed to delete table '{table_name}': {e}")
            raise

    def put_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Put an item into a DynamoDB table.

        Args:
            table_name: Name of the table
            item: Item to put

        Returns:
            Put operation response

        Raises:
            ClientError: If put operation fails
        """
        try:
            table = self.get_table(table_name)
            response = table.put_item(Item=item)
            logger.debug(f"Item put into '{table_name}'")
            return response
        except ClientError as e:
            logger.error(f"Failed to put item into '{table_name}': {e}")
            raise

    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get an item from a DynamoDB table.

        Args:
            table_name: Name of the table
            key: Primary key of the item

        Returns:
            Item if found, None otherwise

        Raises:
            ClientError: If get operation fails
        """
        try:
            table = self.get_table(table_name)
            response = table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            logger.error(f"Failed to get item from '{table_name}': {e}")
            raise

    def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an item in a DynamoDB table.

        Args:
            table_name: Name of the table
            key: Primary key of the item
            update_expression: UpdateExpression string
            expression_attribute_values: Expression attribute values
            expression_attribute_names: Expression attribute names
            **kwargs: Additional arguments (e.g., ReturnValues)

        Returns:
            Update operation response

        Raises:
            ClientError: If update operation fails
        """
        try:
            table = self.get_table(table_name)
            params = {
                "Key": key,
                "UpdateExpression": update_expression,
                **kwargs
            }

            if expression_attribute_values:
                params["ExpressionAttributeValues"] = expression_attribute_values

            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names

            response = table.update_item(**params)
            logger.debug(f"Item updated in '{table_name}'")
            return response
        except ClientError as e:
            logger.error(f"Failed to update item in '{table_name}': {e}")
            raise

    def delete_item(self, table_name: str, key: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete an item from a DynamoDB table.

        Args:
            table_name: Name of the table
            key: Primary key of the item

        Returns:
            Delete operation response

        Raises:
            ClientError: If delete operation fails
        """
        try:
            table = self.get_table(table_name)
            response = table.delete_item(Key=key)
            logger.debug(f"Item deleted from '{table_name}'")
            return response
        except ClientError as e:
            logger.error(f"Failed to delete item from '{table_name}': {e}")
            raise

    def query(
        self,
        table_name: str,
        key_condition_expression: str,
        expression_attribute_values: Dict[str, Any],
        expression_attribute_names: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Query items from a DynamoDB table.

        Args:
            table_name: Name of the table
            key_condition_expression: KeyConditionExpression string
            expression_attribute_values: Expression attribute values
            expression_attribute_names: Expression attribute names
            limit: Maximum number of items to return
            **kwargs: Additional arguments

        Returns:
            List of items matching the query

        Raises:
            ClientError: If query operation fails
        """
        try:
            table = self.get_table(table_name)
            params = {
                "KeyConditionExpression": key_condition_expression,
                "ExpressionAttributeValues": expression_attribute_values,
                **kwargs
            }

            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names

            if limit:
                params["Limit"] = limit

            response = table.query(**params)
            logger.debug(f"Query executed on '{table_name}'")
            return response.get("Items", [])
        except ClientError as e:
            logger.error(f"Failed to query '{table_name}': {e}")
            raise

    def scan(
        self,
        table_name: str,
        filter_expression: Optional[str] = None,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Scan items from a DynamoDB table.

        Args:
            table_name: Name of the table
            filter_expression: Optional FilterExpression string
            expression_attribute_values: Expression attribute values
            expression_attribute_names: Expression attribute names
            limit: Maximum number of items to return
            **kwargs: Additional arguments

        Returns:
            List of items from scan operation

        Raises:
            ClientError: If scan operation fails
        """
        try:
            table = self.get_table(table_name)
            params = {**kwargs}

            if filter_expression:
                params["FilterExpression"] = filter_expression

            if expression_attribute_values:
                params["ExpressionAttributeValues"] = expression_attribute_values

            if expression_attribute_names:
                params["ExpressionAttributeNames"] = expression_attribute_names

            if limit:
                params["Limit"] = limit

            response = table.scan(**params)
            logger.debug(f"Scan executed on '{table_name}'")
            return response.get("Items", [])
        except ClientError as e:
            logger.error(f"Failed to scan '{table_name}': {e}")
            raise

    def batch_write_item(self, table_name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch write items to a DynamoDB table.

        Args:
            table_name: Name of the table
            items: List of items to write

        Returns:
            Batch write response

        Raises:
            ClientError: If batch write operation fails
        """
        try:
            table = self.get_table(table_name)
            with table.batch_writer(overwrite_by_pkeys=["id"]) as batch:
                for item in items:
                    batch.put_item(Item=item)
            logger.info(f"Batch write completed for '{table_name}' with {len(items)} items")
            return {"Count": len(items)}
        except ClientError as e:
            logger.error(f"Failed to batch write to '{table_name}': {e}")
            raise

    def batch_get_item(self, table_name: str, keys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch get items from a DynamoDB table.

        Args:
            table_name: Name of the table
            keys: List of primary keys to retrieve

        Returns:
            List of items

        Raises:
            ClientError: If batch get operation fails
        """
        try:
            table = self.get_table(table_name)
            response = self.dynamodb.batch_get_item(
                RequestItems={
                    table_name: {
                        "Keys": keys
                    }
                }
            )
            logger.debug(f"Batch get completed for '{table_name}'")
            return response.get("Responses", {}).get(table_name, [])
        except ClientError as e:
            logger.error(f"Failed to batch get from '{table_name}': {e}")
            raise

    @contextmanager
    def batch_writer(self, table_name: str, **kwargs):
        """
        Context manager for batch writing items.

        Args:
            table_name: Name of the table
            **kwargs: Additional arguments for batch_writer

        Yields:
            Batch writer context
        """
        try:
            table = self.get_table(table_name)
            with table.batch_writer(**kwargs) as batch:
                yield batch
        except ClientError as e:
            logger.error(f"Failed to create batch writer for '{table_name}': {e}")
            raise


# Singleton instance
_dynamodb_client: Optional[DynamoDBClient] = None


def get_dynamodb_client(region_name: str = "us-east-1", endpoint_url: Optional[str] = None) -> DynamoDBClient:
    """
    Get or create the DynamoDB client singleton.

    Args:
        region_name: AWS region
        endpoint_url: Optional endpoint URL for local testing

    Returns:
        DynamoDBClient instance
    """
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient(region_name=region_name, endpoint_url=endpoint_url)
    return _dynamodb_client


def initialize_dynamodb(region_name: str = "us-east-1", endpoint_url: Optional[str] = None) -> None:
    """
    Initialize the DynamoDB client.

    Args:
        region_name: AWS region
        endpoint_url: Optional endpoint URL for local testing
    """
    global _dynamodb_client
    _dynamodb_client = DynamoDBClient(region_name=region_name, endpoint_url=endpoint_url)
    logger.info("DynamoDB client initialized")
